"""Give all three outlined frames the same cropped viewBox."""
import os
import xml.etree.ElementTree as ET

from fontTools.pens.boundsPen import BoundsPen
from fontTools.svgLib.path import parse_path

ET.register_namespace("", "http://www.w3.org/2000/svg")
NS = "{http://www.w3.org/2000/svg}"
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DIR = os.path.join(ROOT, "assets", "src")
MARGIN = 20
NAMES = ["idle", "left-down", "right-down"]

boxes = []
for name in NAMES:
    root = ET.parse(os.path.join(DIR, name + ".svg")).getroot()
    pen = BoundsPen(None)
    for path in root.iter(NS + "path"):
        if path.get("d"):
            parse_path(path.get("d"), pen)
    boxes.append(pen.bounds)
    print(name, "content bbox", tuple(round(v, 1) for v in pen.bounds))

x0 = min(b[0] for b in boxes) - MARGIN
y0 = min(b[1] for b in boxes) - MARGIN
x1 = max(b[2] for b in boxes) + MARGIN
y1 = max(b[3] for b in boxes) + MARGIN
W, H = int(round(x1 - x0)), int(round(y1 - y0))

for name in NAMES:
    path = os.path.join(DIR, name + ".svg")
    root = ET.parse(path).getroot()
    root.set("viewBox", "%d %d %d %d" % (round(x0), round(y0), W, H))
    root.set("width", str(W))
    root.set("height", str(H))
    ET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)
    print("cropped", name, root.get("viewBox"))
