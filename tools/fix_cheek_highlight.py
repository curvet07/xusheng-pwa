"""Fix left cheek highlight patch under the jaw line."""
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets" / "live2d"
OUT = ROOT / "tools" / "diagnose_output"
OUT.mkdir(exist_ok=True)

def load(name):
    return Image.open(ASSETS / name).convert("RGBA")

def save(img, name):
    img.save(OUT / name)
    print(f"saved: {OUT / name}")

body = load("body_master_aligned.png")
neck_orig = load("neck_body_clean_v2.png")
cranium_orig = load("cranium_earless_refined_v2.png")
collar = load("collar_foreground_aligned.png")

size = body.size

def composite(cranium, neck):
    canvas = Image.new("RGBA", size, (238, 239, 241, 255))
    canvas.alpha_composite(body)
    canvas.alpha_composite(neck)
    canvas.alpha_composite(cranium)
    canvas.alpha_composite(collar)
    return canvas

# Repair zone: left cheek highlight patch below the jaw line
# This sits slightly above the previous neck seam repair.
repair_mask = Image.new("L", size, 0)
draw = ImageDraw.Draw(repair_mask)
draw.polygon(
    [(380, 270), (460, 260), (500, 310), (490, 380), (430, 400), (370, 360)],
    fill=255,
)
repair_mask = repair_mask.filter(ImageFilter.GaussianBlur(14))

r = np.asarray(repair_mask).astype(np.float32) / 255.0

cranium = cranium_orig.copy()
c_data = np.asarray(cranium).astype(np.float32)
c_alpha = c_data[..., 3]

# 1) Darken/tint the light cheek patch so it blends with surrounding skin.
# Pick a darker cheek tone sample just outside the patch.
sample_box = c_data[300:340, 460:520]  # right/lower side of left cheek, outside patch
mask_box = sample_box[..., 3] > 50
if mask_box.any():
    target_tone = sample_box[mask_box][:, :3].mean(axis=0)
    # Compute current tone in repair zone
    zone = (r > 0.05) & (c_alpha > 20)
    if zone.any():
        current_tone = c_data[zone][:, :3].mean(axis=0)
        # Darken by moving 35% toward target tone; keep texture
        blend = 0.35
        for c in range(3):
            c_data[..., c] = np.where(
                zone,
                c_data[..., c] * (1 - blend * r) + target_tone[c] * (blend * r),
                c_data[..., c],
            )

# 2) Feather cranium alpha in the repair zone to remove hard edge against neck.
blurred_c_alpha = np.asarray(cranium.split()[3].filter(ImageFilter.GaussianBlur(2))).astype(np.float32)
new_c_alpha = (1 - r) * c_alpha + r * blurred_c_alpha
new_c_alpha = np.clip(new_c_alpha, 0, 255)
c_data[..., 3] = new_c_alpha
cranium = Image.fromarray(c_data.astype(np.uint8), "RGBA")

# 3) Slightly dilate neck alpha under the patch so neck peeks through for softer transition.
n_alpha = np.asarray(neck_orig.split()[3]).astype(np.float32)
dilated_n_alpha = np.asarray(neck_orig.split()[3].filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(2))).astype(np.float32)
new_n_alpha = (1 - r * 0.5) * n_alpha + (r * 0.5) * dilated_n_alpha
new_n_alpha = np.clip(new_n_alpha, 0, 255)
neck = neck_orig.copy()
neck.putalpha(Image.fromarray(new_n_alpha.astype(np.uint8), "L"))

# Save preview files (do not overwrite assets until verified)
cranium.save(OUT / "cranium_cheek_fixed.png")
neck.save(OUT / "neck_cheek_fixed.png")

# Comparison
before = composite(cranium_orig, neck_orig)
after = composite(cranium, neck)

before.resize((size[0] // 2, size[1] // 2), Image.Resampling.LANCZOS).convert("RGB").save(OUT / "cheek_compare_before.jpg", quality=92)
after.resize((size[0] // 2, size[1] // 2), Image.Resampling.LANCZOS).convert("RGB").save(OUT / "cheek_compare_after.jpg", quality=92)

crop = (360, 260, 560, 420)
before_crop = before.crop(crop).resize((600, 480), Image.Resampling.NEAREST)
after_crop = after.crop(crop).resize((600, 480), Image.Resampling.NEAREST)
compare = Image.new("RGB", (1220, 480), (238, 239, 241))
compare.paste(before_crop.convert("RGB"), (10, 0))
compare.paste(after_crop.convert("RGB"), (610, 0))
compare.save(OUT / "cheek_compare_magnified.jpg", quality=95)

print("done")
