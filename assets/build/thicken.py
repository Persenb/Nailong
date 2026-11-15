"""Add a stroke to the normalized thin SVGs so the lines survive at 16px.

Tune STROKE_WIDTH here if the icon looks too thin or too heavy. After running
this, run outline.js (stroke -> filled paths), crop_frames.py, then
build_font.py.
"""
import os
import xml.etree.ElementTree as ET

ET.register_namespace("", "http://www.w3.org/2000/svg")
NS = "{http://www.w3.org/2000/svg}"
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(ROOT, "assets", "src", "source")
DST = os.path.join(ROOT, "assets", "build", "thick")
STROKE_WIDTH = 15

os.makedirs(DST, exist_ok=True)
for name in ["idle", "left-down", "right-down"]:
    root = ET.parse(os.path.join(SRC, name + ".svg")).getroot()
    for g in root.iter(NS + "g"):
        if g.get("id") == "dots":
            continue
        g.set("stroke", "#000")
        g.set("stroke-width", str(STROKE_WIDTH))
        g.set("stroke-linejoin", "round")
        g.set("stroke-linecap", "round")
    ET.ElementTree(root).write(os.path.join(DST, name + ".svg"), encoding="utf-8", xml_declaration=True)
    print("thickened", name, "stroke-width", STROKE_WIDTH)
