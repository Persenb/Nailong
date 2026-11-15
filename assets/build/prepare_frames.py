"""Normalize the three hand-drawn SVGs before font conversion.

- idle is kept as drawn.
- In left-down / right-down the action paw is moved downward so the pose
  actually reads as a paw slamming down (the source drawings had it slightly
  higher than the resting paw).
- The tiny motion lines are replaced by three large, separate impact dots.
- Every subpath is explicitly closed (the source relies on implicit closing).
"""
import os
import xml.etree.ElementTree as ET

from fontTools.svgLib.path import parse_path

NS = "{http://www.w3.org/2000/svg}"
ET.register_namespace("", "http://www.w3.org/2000/svg")
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = ROOT
OUT = os.path.join(ROOT, "assets", "src", "source")
os.makedirs(OUT, exist_ok=True)

# paw_box: subpaths to translate (the action paw). mark_box: tiny motion lines
# to delete. dots: three impact marks added below the paw.
MOUTH_D = "M538 414 Q563 436 588 414"

SPECS = {
    "left_down.svg": {
        "paw_box": (415, 405, 560, 490),
        "paw_delta": (18, 28),
        "mark_box": (400, 465, 565, 505),
        "dots": [(468, 510), (500, 513), (532, 516)],
    },
    "right_down.svg": {
        "paw_box": (660, 440, 745, 490),
        "paw_delta": (-60, 20),
        "mark_box": (715, 485, 785, 510),
        "dots": [(610, 512), (642, 515), (674, 518)],
    },
}


class Recorder:
    """Collect absolute subpaths from a SVG path."""

    def __init__(self):
        self.subpaths = []
        self.cur = None

    def moveTo(self, pt):
        self.cur = [("M", pt)]
        self.subpaths.append(self.cur)

    def lineTo(self, pt):
        self.cur.append(("L", pt))

    def curveTo(self, *pts):
        self.cur.append(("C", pts))

    def qCurveTo(self, *pts):
        self.cur.append(("Q", pts))

    def closePath(self):
        self.cur = None

    def endPath(self):
        self.cur = None


def num(v):
    return ("%.4f" % v).rstrip("0").rstrip(".")


def subpath_bbox(sp):
    xs, ys = [], []
    for cmd in sp:
        if cmd[0] in "ML":
            pts = [cmd[1]]
        elif cmd[0] == "C":
            pts = list(cmd[1])
        else:
            pts = [p for p in cmd[1] if p is not None]
        for x, y in pts:
            xs.append(x)
            ys.append(y)
    return min(xs), min(ys), max(xs), max(ys)


def in_box(b, box):
    return b[0] >= box[0] and b[1] >= box[1] and b[2] <= box[2] and b[3] <= box[3]


def translate(sp, dx, dy):
    for i, cmd in enumerate(sp):
        if cmd[0] in "ML":
            x, y = cmd[1]
            sp[i] = (cmd[0], (x + dx, y + dy))
        else:
            pts = tuple(None if p is None else (p[0] + dx, p[1] + dy) for p in cmd[1])
            sp[i] = (cmd[0], pts)


def serialize(sp):
    parts = []
    for cmd in sp:
        if cmd[0] == "M":
            x, y = cmd[1]
            parts.append("M%s %s" % (num(x), num(y)))
        elif cmd[0] == "L":
            x, y = cmd[1]
            parts.append("L%s %s" % (num(x), num(y)))
        elif cmd[0] == "C":
            coords = " ".join("%s %s" % (num(x), num(y)) for x, y in cmd[1])
            parts.append("C" + coords)
        elif cmd[0] == "Q":
            coords = " ".join(
                "%s %s" % (num(p[0]), num(p[1])) for p in cmd[1] if p is not None
            )
            parts.append("Q" + coords)
    parts.append("Z")
    return " ".join(parts)


def circle_path(cx, cy, r):
    return (
        "M%s %s"
        "a%s %s 0 1 0 %s 0"
        "a%s %s 0 1 0 %s 0Z"
        % (num(cx - r), num(cy), num(r), num(r), num(2 * r),
           num(r), num(r), num(-2 * r))
    )


def process(fn, out_name):
    spec = SPECS.get(fn)
    root = ET.parse(os.path.join(SRC, fn)).getroot()
    for path in root.iter(NS + "path"):
        rec = Recorder()
        parse_path(path.get("d"), rec)
        kept = []
        for sp in rec.subpaths:
            if spec:
                b = subpath_bbox(sp)
                if in_box(b, spec["mark_box"]) and (b[3] - b[1]) <= 4:
                    continue
                if (
                    in_box(b, spec["paw_box"])
                    and 5 < (b[3] - b[1]) < 80
                    and (b[2] - b[0]) < 120
                ):
                    translate(sp, *spec["paw_delta"])
            kept.append(sp)
        path.set("d", " ".join(serialize(sp) for sp in kept))

    # A short fixed arc on the face, shared by all three frames.
    main_g = root.find(NS + "g")
    ET.SubElement(main_g, NS + "path", {
        "d": MOUTH_D,
        "fill": "none",
        "stroke-linecap": "round",
    })

    if spec:
        dots = ET.SubElement(root, NS + "g", {"id": "dots"})
        for cx, cy in spec["dots"]:
            ET.SubElement(dots, NS + "path", {"d": circle_path(cx, cy, 10)})

    out = os.path.join(OUT, out_name)
    ET.ElementTree(root).write(out, encoding="utf-8", xml_declaration=True)
    print("wrote", out)


process("idle.svg", "idle.svg")
process("left_down.svg", "left-down.svg")
process("right_down.svg", "right-down.svg")
