"""Diagnose left cheek/jaw highlight issue in Live2D assembly."""
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
bg = (238, 239, 241, 255)

# Full assembly
canvas = Image.new("RGBA", size, bg)
canvas.alpha_composite(body)
canvas.alpha_composite(neck)
canvas.alpha_composite(cranium)
canvas.alpha_composite(collar)
canvas.convert("RGB").save(OUT / "cheek_assembly_preview.jpg", quality=95)

# Crop the left cheek/jaw region (red circle area)
crop_box = (360, 260, 560, 420)
cropped = canvas.crop(crop_box)
magnified = cropped.resize(((crop_box[2] - crop_box[0]) * 3, (crop_box[3] - crop_box[1]) * 3), Image.Resampling.NEAREST)
magnified.convert("RGB").save(OUT / "cheek_left_magnified.jpg", quality=95)

# Layer isolation: cranium only over background
white = Image.new("RGBA", size, (255, 255, 255, 255))
white.paste(cranium, (0, 0), cranium)
white.crop(crop_box).resize(((crop_box[2] - crop_box[0]) * 3, (crop_box[3] - crop_box[1]) * 3), Image.Resampling.NEAREST).convert("RGB").save(OUT / "cheek_cranium_only.jpg", quality=95)

# Neck only over background
white2 = Image.new("RGBA", size, (255, 255, 255, 255))
white2.paste(neck, (0, 0), neck)
white2.crop(crop_box).resize(((crop_box[2] - crop_box[0]) * 3, (crop_box[3] - crop_box[1]) * 3), Image.Resampling.NEAREST).convert("RGB").save(OUT / "cheek_neck_only.jpg", quality=95)

# Body only over background
white3 = Image.new("RGBA", size, (255, 255, 255, 255))
white3.paste(body, (0, 0), body)
white3.crop(crop_box).resize(((crop_box[2] - crop_box[0]) * 3, (crop_box[3] - crop_box[1]) * 3), Image.Resampling.NEAREST).convert("RGB").save(OUT / "cheek_body_only.jpg", quality=95)

# Collar only over background
white4 = Image.new("RGBA", size, (255, 255, 255, 255))
white4.paste(collar, (0, 0), collar)
white4.crop(crop_box).resize(((crop_box[2] - crop_box[0]) * 3, (crop_box[3] - crop_box[1]) * 3), Image.Resampling.NEAREST).convert("RGB").save(OUT / "cheek_collar_only.jpg", quality=95)

# Crop indicator on preview
preview_draw = canvas.copy()
draw = ImageDraw.Draw(preview_draw)
draw.rectangle(crop_box, outline="red", width=3)
preview_draw.convert("RGB").save(OUT / "cheek_crop_indicator.jpg", quality=95)

print("saved cheek diagnostics to", OUT)
