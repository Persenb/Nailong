"""Build a WOFF icon font from the three normalized SVG frames.

The outlined SVGs from potrace use fill-rule="evenodd". TrueType glyphs are
filled with the nonzero rule, so contours are reversed by nesting depth to
keep the holes (body interior, eye whites) transparent.

All frames share one scale/origin so the body does not move between them.
Glyphs live in the Unicode Private Use Area (U+E900..U+E902).
"""
import os
import xml.etree.ElementTree as ET

from fontTools.fontBuilder import FontBuilder
from fontTools.misc.transform import Transform
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.pointInsidePen import PointInsidePen
from fontTools.pens.reverseContourPen import ReverseContourPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.svgLib.path import parse_path

NS = "{http://www.w3.org/2000/svg}"
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(ROOT, "assets", "frames")
OUT_DIR = os.path.join(ROOT, "assets", "build")
os.makedirs(OUT_DIR, exist_ok=True)

FRAMES = [
    ("idle", "idle", 0xE900),
    ("leftdown", "left-down", 0xE901),
    ("rightdown", "right-down", 0xE902),
]

UPEM = 1024
ASCENT = 960
DESCENT = -64
TARGET_H = 920
BOTTOM_PAD = 24
SIDE_PAD = 48


class ContourRecorder:
    def __init__(self):
        self.contours = []
        self.cur = None

    def moveTo(self, pt):
        self.cur = [("M", pt)]
        self.contours.append(self.cur)

    def lineTo(self, pt):
        self.cur.append(("L", pt))

    def curveTo(self, *pts):
        self.cur.append(("C", pts))

    def qCurveTo(self, *pts):
        self.cur.append(("Q", pts))

    def closePath(self):
        self._close()

    def endPath(self):
        self._close()

    def _close(self):
        if self.cur is not None:
            if not self.cur or self.cur[-1][0] != "Z":
                self.cur.append(("Z",))
            self.cur = None


def svg_contours(name):
    root = ET.parse(os.path.join(SRC, name + ".svg")).getroot()
    rec = ContourRecorder()
    for path in root.iter(NS + "path"):
        d = path.get("d")
        if d:
            parse_path(d, rec)
    return rec.contours


def path_bbox(paths, transform):
    pen = BoundsPen(None)
    for contour in paths:
        draw(contour, pen, transform)
    return pen.bounds


def draw(contour, pen, transform):
    for cmd in contour:
        kind = cmd[0]
        if kind == "M":
            pen.moveTo(transform.transformPoint(cmd[1]))
        elif kind == "L":
            pen.lineTo(transform.transformPoint(cmd[1]))
        elif kind == "C":
            pen.curveTo(*(transform.transformPoint(p) for p in cmd[1]))
        elif kind == "Q":
            pen.qCurveTo(*(None if p is None else transform.transformPoint(p) for p in cmd[1]))
        elif kind == "Z":
            pen.closePath()


def contour_test_point(contour, transform):
    cmd = contour[0]
    assert cmd[0] == "M"
    return transform.transformPoint(cmd[1])


def containment_depth(contours, index, transform):
    """How many other contours contain a point on this contour."""
    test_point = contour_test_point(contours[index], transform)
    depth = 0
    for j, other in enumerate(contours):
        if j == index:
            continue
        probe = PointInsidePen(None, test_point)
        draw(other, probe, transform)
        if probe.getResult():
            depth += 1
    return depth


raw = {glyph_name: svg_contours(file_name) for glyph_name, file_name, _cp in FRAMES}

# Union bbox in SVG coordinates (before scaling)
boxes = []
for name, _f, _c in FRAMES:
    pen = BoundsPen(None)
    for contour in raw[name]:
        draw(contour, pen, Transform(1, 0, 0, 1, 0, 0))
    boxes.append(pen.bounds)
x0 = min(b[0] for b in boxes)
y0 = min(b[1] for b in boxes)
x1 = max(b[2] for b in boxes)
y1 = max(b[3] for b in boxes)

scale = TARGET_H / (y1 - y0)
advance = int(round((x1 - x0) * scale + 2 * SIDE_PAD))
transform = Transform(
    scale, 0, 0, -scale,
    -x0 * scale + SIDE_PAD,
    y1 * scale + BOTTOM_PAD,
)
print("union bbox", tuple(round(v, 2) for v in (x0, y0, x1, y1)))
print("scale", round(scale, 4), "advance", advance)

glyphs = {}
metrics = {".notdef": (advance, 0)}
glyph_order = [".notdef"]

nt = TTGlyphPen(None)
glyphs[".notdef"] = nt.glyph()

for glyph_name, file_name, _cp in FRAMES:
    contours = raw[glyph_name]
    depths = [containment_depth(contours, i, transform) for i in range(len(contours))]
    print(file_name, "contours:", len(contours), "depths:", depths)
    pen = TTGlyphPen(None)
    quad_pen = Cu2QuPen(pen, max_err=0.5)
    for contour, depth in zip(contours, depths):
        target = ReverseContourPen(quad_pen) if depth % 2 == 1 else quad_pen
        draw(contour, target, transform)
    glyphs[glyph_name] = pen.glyph()
    xs = [transform.transformPoint(cmd[1])[0] for contour in contours for cmd in contour if cmd[0] in "ML"]
    xs += [transform.transformPoint(p)[0] for contour in contours for cmd in contour if cmd[0] in "CQ" for p in cmd[1] if p is not None]
    metrics[glyph_name] = (advance, max(0, int(round(min(xs)))))
    glyph_order.append(glyph_name)

fb = FontBuilder(UPEM, isTTF=True)
fb.setupGlyphOrder(glyph_order)
fb.setupCharacterMap({cp: glyph_name for glyph_name, _f, cp in FRAMES})
fb.setupGlyf(glyphs)
fb.setupHorizontalMetrics(metrics)
fb.setupHorizontalHeader(ascent=ASCENT, descent=DESCENT)
fb.setupNameTable({
    "familyName": "Nailong Status Icons",
    "styleName": "Regular",
    "uniqueFontIdentifier": "Nailong Status Icons Regular 1.0",
    "fullName": "Nailong Status Icons Regular",
    "psName": "NailongStatusIcons-Regular",
    "version": "Version 1.0",
})
fb.setupOS2(
    sTypoAscender=ASCENT,
    sTypoDescender=DESCENT,
    sTypoLineGap=0,
    usWinAscent=ASCENT,
    usWinDescent=abs(DESCENT),
    usWeightClass=400,
    sxHeight=700,
    sCapHeight=700,
)
fb.setupPost()

font = fb.font
font.flavor = None
ttf_path = os.path.join(OUT_DIR, "nailong.ttf")
font.save(ttf_path)
font.flavor = "woff"
woff_path = os.path.join(OUT_DIR, "nailong.woff")
font.save(woff_path)
print("wrote", ttf_path)
print("wrote", woff_path)

from fontTools.ttLib import TTFont
check = TTFont(woff_path)
print("glyph order:", check.getGlyphOrder())
print("cmap:", {hex(k): v for k, v in check.getBestCmap().items()})
print("upem:", check["head"].unitsPerEm, "ascent:", check["hhea"].ascent, "descent:", check["hhea"].descent)
for name, _f, _c in FRAMES:
    glyph = check["glyf"][name]
    print(name, "advance:", check["hmtx"][name][0], "lsb:", check["hmtx"][name][1],
          "bbox:", (glyph.xMin, glyph.yMin, glyph.xMax, glyph.yMax) if glyph.numberOfContours else "empty")
