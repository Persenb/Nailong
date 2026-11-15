"""Generate the README demo GIF from the built icon font.

Prerequisite: run build_font.py first (assets/build/bongocat.woff).
Output: assets/demo.gif (tracked) and assets/demo_preview.png (ignored).
"""
import os

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FONT = os.path.join(ROOT, "assets", "build", "bongocat.woff")
OUT_GIF = os.path.join(ROOT, "assets", "demo.gif")
OUT_PREVIEW = os.path.join(ROOT, "assets", "demo_preview.png")

icon = ImageFont.truetype(FONT, 48)
try:
    ui = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 36)
    ui_small = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 28)
except Exception:
    ui = ImageFont.load_default()
    ui_small = ui

W, H = 760, 84
BG = (0, 122, 204)  # VS Code status bar blue
FG = (255, 255, 255)


def frame(ch):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    d.text((24, H // 2), ch, font=icon, fill=FG, anchor="lm")
    adv = int(icon.getlength(ch))
    d.text((24 + adv + 16, H // 2), "Nailong", font=ui, fill=FG, anchor="lm")
    d.text((W - 24, H // 2), "UTF-8", font=ui_small, fill=(230, 240, 250), anchor="rm")
    return img


idle = frame("\ue900")
left = frame("\ue901")
right = frame("\ue902")

# A typing rhythm: idle -> tap -> idle -> tap -> ... -> idle
seq = [idle, left, idle, right, idle, left, idle, right, idle]
durations = [700, 160, 120, 160, 120, 160, 120, 160, 900]

seq[0].save(
    OUT_GIF,
    save_all=True,
    append_images=seq[1:],
    duration=durations,
    loop=0,
    optimize=True,
    disposal=2,
)
idle.save(OUT_PREVIEW)
print("wrote", OUT_GIF)
