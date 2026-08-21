from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets" / "live2d"
OUT = ROOT / "tools" / "diagnose_output"
OUT.mkdir(exist_ok=True)

body = Image.open(ASSETS / "body_master_aligned.png").convert("RGBA")
neck = Image.open(ASSETS / "neck_body_clean_v2.png").convert("RGBA")
cranium = Image.open(ASSETS / "cranium_earless_refined_v2.png").convert("RGBA")
collar = Image.open(ASSETS / "collar_foreground_aligned.png").convert("RGBA")

size = body.size
canvas = Image.new("RGBA", size, (238, 239, 241, 255))

# index.html layer order: body -> neck -> ears -> cranium -> collar
canvas.alpha_composite(body)
canvas.alpha_composite(neck)
canvas.alpha_composite(cranium)
canvas.alpha_composite(collar)

# Save full-size and a downscaled preview
canvas.convert("RGB").save(OUT / "neck_assembly_before.jpg", quality=95)
preview = canvas.resize((size[0] // 2, size[1] // 2), Image.Resampling.LANCZOS)
preview.convert("RGB").save(OUT / "neck_assembly_before_preview.jpg", quality=92)

# Crop the left jaw/neck trouble region and magnify 2x
# Coordinates in original 1024x1536 space: left jaw / neck junction
crop_box = (360, 260, 560, 420)
cropped = canvas.crop(crop_box)
magnified = cropped.resize(((crop_box[2] - crop_box[0]) * 3, (crop_box[3] - crop_box[1]) * 3), Image.Resampling.NEAREST)
magnified.convert("RGB").save(OUT / "neck_left_junction_magnified.jpg", quality=95)

print(f"saved: {OUT / 'neck_assembly_before_preview.jpg'}")
print(f"saved: {OUT / 'neck_left_junction_magnified.jpg'}")
