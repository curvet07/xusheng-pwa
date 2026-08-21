"""Full character preview with repair zone marked, for user verification."""
from PIL import Image, ImageDraw
from pathlib import Path

BASE = Path("C:/Users/hoverliu/Documents/ChatGPT/个人生活工作台/assets/live2d")
OUT = Path("C:/Users/hoverliu/Documents/ChatGPT/个人生活工作台/tools/diagnose_output")
OUT.mkdir(parents=True, exist_ok=True)

body = Image.open(BASE / "body_master_aligned.png").convert("RGBA")
neck = Image.open(BASE / "neck_body_clean_v2.png").convert("RGBA")
cranium = Image.open(BASE / "cranium_earless_refined_v2.png").convert("RGBA")
collar = Image.open(BASE / "collar_foreground_aligned.png").convert("RGBA")

size = body.size
canvas = Image.new("RGBA", size, (238, 239, 241, 255))
canvas.alpha_composite(body)
canvas.alpha_composite(neck)
canvas.alpha_composite(cranium)
canvas.alpha_composite(collar)

draw = ImageDraw.Draw(canvas)
# Repair zone 1: left jaw seam (first fix)
draw.rectangle([(350, 260), (470, 420)], outline="lime", width=4)
# Repair zone 2: left cheek highlight (second fix)
draw.rectangle([(380, 270), (500, 400)], outline="red", width=4)

canvas.convert("RGB").save(OUT / "preview_marked.jpg", quality=95)
print("saved", OUT / "preview_marked.jpg")
