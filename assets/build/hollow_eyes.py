"""Punch hollow centers into the two eyes.

Run after outline.js (the potrace output uses fill-rule="evenodd"), before
crop_frames.py and build_font.py. Appending an ellipse subpath to the same
evenodd path makes the eye ring instead of a solid dot.
"""
import os
import xml.etree.ElementTree as ET

ET.register_namespace("", "http://www.w3.org/2000/svg")
NS = "{http://www.w3.org/2000/svg}"
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DIR = os.path.join(ROOT, "assets", "frames")

# (center x, center y, radius x, radius y) in the original 1414x706 SVG space
EYES = [
    (619.4, 355.0, 15.0, 17.0),  # right eye (nearer the tail)
    (507.0, 357.0, 11.0, 14.0),  # left eye (under the chin)
]


def num(v):
    return ("%.3f" % v).rstrip("0").rstrip(".")


def ellipse(cx, cy, rx, ry):
    return (
        "M%s %s"
        "a%s %s 0 1 0 %s 0"
        "a%s %s 0 1 0 %s 0Z"
        % (num(cx - rx), num(cy), num(rx), num(ry), num(2 * rx),
           num(rx), num(ry), num(-2 * rx))
    )


for name in ["idle", "left-down", "right-down"]:
    path = os.path.join(DIR, name + ".svg")
    root = ET.parse(path).getroot()
    changed = False
    for p in root.iter(NS + "path"):
        if p.get("fill-rule") == "evenodd":
            p.set("d", p.get("d") + " " + " ".join(ellipse(*e) for e in EYES))
            changed = True
    if not changed:
        raise SystemExit("no evenodd path found in " + name)
    ET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)
    print("hollowed eyes:", name)
