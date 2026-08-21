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

def composite(cranium, neck):
    size = body.size
    canvas = Image.new("RGBA", size, (238, 239, 241, 255))
    canvas.alpha_composite(body)
    canvas.alpha_composite(neck)
    canvas.alpha_composite(cranium)
    canvas.alpha_composite(collar)
    return canvas

body = load("body_master_aligned.png")
neck_orig = load("neck_body_clean_v2.png")
cranium_orig = load("cranium_earless_refined_v2.png")
collar = load("collar_foreground_aligned.png")

size = body.size

# Repair zone: left jaw / neck junction (raw 1024x1536 coordinates)
repair_mask = Image.new("L", size, 0)
draw = ImageDraw.Draw(repair_mask)
# Polygon covering the visible seam in the magnified diagnosis
draw.polygon(
    [(350, 260), (430, 250), (470, 320), (460, 410), (390, 420), (340, 360)],
    fill=255,
)
repair_mask = repair_mask.filter(ImageFilter.GaussianBlur(8))

# 1) Feather cranium alpha inside the repair zone to kill the hard black cut line
r = np.asarray(repair_mask)
cranium = cranium_orig.copy()
c_alpha = np.asarray(cranium.split()[3]).astype(np.float32)
# Blur only where mask is strong
blurred_c_alpha = np.asarray(cranium.split()[3].filter(ImageFilter.GaussianBlur(2.5))).astype(np.float32)
mask_f = r.astype(np.float32) / 255.0
new_c_alpha = (1 - mask_f) * c_alpha + mask_f * blurred_c_alpha
new_c_alpha = np.clip(new_c_alpha, 0, 255).astype(np.uint8)
cranium.putalpha(Image.fromarray(new_c_alpha, "L"))

# 2) Dilate + feather neck alpha inside the repair zone so more neck skin peeks above the jaw line
n_alpha = np.asarray(neck_orig.split()[3]).astype(np.float32)
dilated_n_alpha = np.asarray(neck_orig.split()[3].filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(2))).astype(np.float32)
new_n_alpha = (1 - mask_f) * n_alpha + mask_f * dilated_n_alpha
new_n_alpha = np.clip(new_n_alpha, 0, 255).astype(np.uint8)
neck = neck_orig.copy()
neck.putalpha(Image.fromarray(new_n_alpha, "L"))

# 3) Color correct neck in repair zone: sample a cheek skin tone from cranium and tint neck slightly
# Pick a sample point on the left cheek (safe area)
c_data = np.asarray(cranium_orig).astype(np.float32)
n_data = np.asarray(neck).astype(np.float32)

# Sample cheek tone near left jaw/cheek
sample_box = c_data[280:320, 420:460]
mask_box = sample_box[..., 3] > 50
if mask_box.any():
    target_tone = sample_box[mask_box][:, :3].mean(axis=0)
    # Sample current neck tone in repair zone
    neck_mask = (new_n_alpha > 20) & (mask_f > 0.1)
    if neck_mask.any():
        current_tone = n_data[neck_mask][:, :3].mean(axis=0)
        # Compute a gentle tint factor (don't fully replace; keep texture)
        tint = target_tone / (current_tone + 1e-5)
        tint = np.clip(tint, 0.85, 1.25)  # constrain to avoid wild shifts
        # Apply tint only in repair zone, weighted by mask and alpha
        for c in range(3):
            n_data[..., c] = np.where(
                neck_mask,
                n_data[..., c] * (1 - mask_f * 0.35) + (n_data[..., c] * tint[c]) * (mask_f * 0.35),
                n_data[..., c],
            )
        n_data = np.clip(n_data, 0, 255).astype(np.uint8)
        neck = Image.fromarray(n_data, "RGBA")

# Save fixed assets (preview only, do not overwrite originals yet)
cranium.save(OUT / "cranium_earless_refined_v2_fixed.png")
neck.save(OUT / "neck_body_clean_v2_fixed.png")

# Generate before / after comparison
before = composite(cranium_orig, neck_orig)
after = composite(cranium, neck)

# Full previews
before.resize((size[0] // 2, size[1] // 2), Image.Resampling.LANCZOS).convert("RGB").save(OUT / "compare_before_preview.jpg", quality=92)
after.resize((size[0] // 2, size[1] // 2), Image.Resampling.LANCZOS).convert("RGB").save(OUT / "compare_after_preview.jpg", quality=92)

# Magnified crop of the repaired region
crop = (360, 260, 560, 420)
before_crop = before.crop(crop).resize((600, 480), Image.Resampling.NEAREST)
after_crop = after.crop(crop).resize((600, 480), Image.Resampling.NEAREST)
compare = Image.new("RGB", (1220, 480), (238, 239, 241))
compare.paste(before_crop.convert("RGB"), (10, 0))
compare.paste(after_crop.convert("RGB"), (610, 0))
compare.save(OUT / "compare_magnified.jpg", quality=95)

print("done")
