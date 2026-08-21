from pathlib import Path

import numpy as np
from PIL import Image
from PIL import ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
ALIGNED = ROOT / "design-concepts" / "live2d" / "aligned"


def remove_green(source: Path, target: Path) -> Image.Image:
    image = Image.open(source).convert("RGBA")
    data = np.asarray(image).astype(np.float32)
    rgb = data[..., :3]
    dominance = rgb[..., 1] - np.maximum(rgb[..., 0], rgb[..., 2])
    alpha = np.clip((150.0 - dominance) * 255.0 / 80.0, 0.0, 255.0)
    alpha = np.minimum(alpha, data[..., 3])

    # Suppress green spill only along semi-transparent antialiased edges.
    spill = (alpha > 0) & (dominance > 8)
    rgb[..., 1][spill] = np.minimum(
        rgb[..., 1][spill],
        np.maximum(rgb[..., 0][spill], rgb[..., 2][spill]) * 1.05,
    )

    result = np.dstack((np.clip(rgb, 0, 255), alpha)).astype(np.uint8)
    output = Image.fromarray(result, "RGBA")
    output.save(target)
    return output


head_raw = remove_green(ALIGNED / "head_master_chroma.png", ALIGNED / "head_master_aligned_raw.png")
body = remove_green(ALIGNED / "body_master_chroma.png", ALIGNED / "body_master_aligned.png")

# Image generation preserved the canvas but enlarged the head contents. Normalize
# its alpha bounds back to the master artwork's ear-tip/chin anchors.
source_box = head_raw.getchannel("A").getbbox()
target_box = (370, 31, 655, 375)
if source_box is None:
    raise SystemExit("Head layer is empty")
head_content = head_raw.crop(source_box).resize(
    (target_box[2] - target_box[0], target_box[3] - target_box[1]),
    Image.Resampling.LANCZOS,
)
head = Image.new("RGBA", head_raw.size, (0, 0, 0, 0))
head.alpha_composite(head_content, (target_box[0], target_box[1]))
head.save(ALIGNED / "head_master_aligned.png")

# The neck remains attached to the torso. A generous overlap sits behind the
# cranium so small rotations never reveal a gap around the jaw.
neck_mask = Image.new("L", head.size, 0)
ImageDraw.Draw(neck_mask).polygon(
    [(435, 305), (470, 330), (555, 330), (590, 305), (585, 390), (430, 390)],
    fill=255,
)
neck_alpha = Image.fromarray(
    np.minimum(np.asarray(head.getchannel("A")), np.asarray(neck_mask)).astype(np.uint8),
    "L",
)
neck = head.copy()
neck.putalpha(neck_alpha)
neck.save(ALIGNED / "neck_body_aligned.png")

cranium_raw = remove_green(
    ALIGNED / "cranium_master_chroma.png", ALIGNED / "cranium_master_aligned_raw.png"
)
cranium_box = cranium_raw.getchannel("A").getbbox()
if cranium_box is None:
    raise SystemExit("Cranium layer is empty")
head_source_width = source_box[2] - source_box[0]
head_source_height = source_box[3] - source_box[1]
scale_x = (target_box[2] - target_box[0]) / head_source_width
scale_y = (target_box[3] - target_box[1]) / head_source_height
cranium_content = cranium_raw.crop(cranium_box).resize(
    (
        round((cranium_box[2] - cranium_box[0]) * scale_x),
        round((cranium_box[3] - cranium_box[1]) * scale_y),
    ),
    Image.Resampling.LANCZOS,
)
cranium = Image.new("RGBA", head.size, (0, 0, 0, 0))
cranium.alpha_composite(cranium_content, (target_box[0], target_box[1]))
cranium.save(ALIGNED / "cranium_master_aligned.png")

earless_raw = remove_green(
    ALIGNED / "cranium_earless_chroma.png", ALIGNED / "cranium_earless_aligned_raw.png"
)
earless_box = earless_raw.getchannel("A").getbbox()
if earless_box is None:
    raise SystemExit("Earless cranium layer is empty")
earless_content = earless_raw.crop(earless_box).resize(cranium_content.size, Image.Resampling.LANCZOS)
earless = Image.new("RGBA", head.size, (0, 0, 0, 0))
earless.alpha_composite(earless_content, (target_box[0], target_box[1]))
earless.save(ALIGNED / "cranium_earless_aligned.png")


def polygon_patch(frame: Image.Image, points: list[tuple[int, int]], target: Path) -> None:
    mask = Image.new("L", frame.size, 0)
    ImageDraw.Draw(mask).polygon(points, fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(1.2))
    patch = frame.copy()
    patch.putalpha(
        Image.fromarray(
            np.minimum(np.asarray(frame.getchannel("A")), np.asarray(mask)).astype(np.uint8),
            "L",
        )
    )
    patch.save(target)


polygon_patch(
    cranium,
    [(372, 28), (455, 28), (474, 174), (438, 205), (386, 170)],
    ALIGNED / "wolf_ear_left_aligned.png",
)
polygon_patch(
    cranium,
    [(568, 28), (655, 28), (650, 170), (594, 205), (552, 174)],
    ALIGNED / "wolf_ear_right_aligned.png",
)

blink_raw = remove_green(
    ALIGNED / "earless_closedblink_chroma.png", ALIGNED / "earless_closedblink_aligned_raw.png"
)
blink_box = blink_raw.getchannel("A").getbbox()
if blink_box is None:
    raise SystemExit("Blink layer is empty")
blink_content = blink_raw.crop(blink_box).resize(cranium_content.size, Image.Resampling.LANCZOS)
blink = Image.new("RGBA", head.size, (0, 0, 0, 0))
blink.alpha_composite(blink_content, (target_box[0], target_box[1]))
blink.save(ALIGNED / "cranium_blink_aligned.png")

half_raw = remove_green(
    ALIGNED / "earless_halfblink_chroma.png", ALIGNED / "earless_halfblink_aligned_raw.png"
)
half_box = half_raw.getchannel("A").getbbox()
if half_box is None:
    raise SystemExit("Half-blink layer is empty")
half_content = half_raw.crop(half_box).resize(cranium_content.size, Image.Resampling.LANCZOS)
half = Image.new("RGBA", head.size, (0, 0, 0, 0))
half.alpha_composite(half_content, (target_box[0], target_box[1]))
half.save(ALIGNED / "cranium_halfblink_aligned.png")


def eye_patch(frame: Image.Image, target: Path) -> None:
    mask = Image.new("L", frame.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((405, 222, 505, 282), fill=255)
    draw.ellipse((516, 222, 616, 282), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(3))
    patch = frame.copy()
    patch.putalpha(
        Image.fromarray(
            np.minimum(np.asarray(frame.getchannel("A")), np.asarray(mask)).astype(np.uint8),
            "L",
        )
    )
    patch.save(target)


eye_patch(half, ALIGNED / "eyes_halfblink_patch.png")
eye_patch(blink, ALIGNED / "eyes_closed_patch.png")

if head.size != body.size:
    raise SystemExit(f"Canvas mismatch: head={head.size}, body={body.size}")

assembly = Image.new("RGBA", head.size, (238, 239, 241, 255))
assembly.alpha_composite(body)
assembly.alpha_composite(neck)
assembly.alpha_composite(cranium)

# A shaped foreground collar occlusion layer makes the neck sit inside the armor.
# Never use a rectangular crop here: its straight top edge visibly cuts the chin
# as soon as the head moves.
body_data = np.asarray(body).copy()
collar_data = np.zeros_like(body_data)
yy, xx = np.ogrid[:body_data.shape[0], :body_data.shape[1]]
# Keep only the low front collar flaps. The central U-shaped opening remains
# transparent, giving the chin and neck enough room for the idle animation.
collar_region = (
    (yy >= 365)
    & (yy < 455)
    & (xx >= 335)
    & (xx < 690)
    & ((xx < 430) | (xx > 595) | (yy > 420))
)
collar_data[collar_region] = body_data[collar_region]
collar = Image.fromarray(collar_data, "RGBA")
collar.save(ALIGNED / "collar_foreground_aligned.png")
assembly.alpha_composite(collar)

assembly.convert("RGB").save(ALIGNED / "assembly_aligned_preview.jpg", quality=94)

blink_assembly = Image.new("RGBA", head.size, (238, 239, 241, 255))
blink_assembly.alpha_composite(body)
blink_assembly.alpha_composite(neck)
blink_assembly.alpha_composite(blink)
blink_assembly.alpha_composite(collar)
blink_assembly.convert("RGB").save(ALIGNED / "assembly_blink_preview.jpg", quality=94)

half_preview = earless.copy()
half_preview.alpha_composite(Image.open(ALIGNED / "eyes_halfblink_patch.png").convert("RGBA"))
half_assembly = Image.new("RGBA", head.size, (238, 239, 241, 255))
half_assembly.alpha_composite(body)
half_assembly.alpha_composite(neck)
half_assembly.alpha_composite(half_preview)
half_assembly.alpha_composite(collar)
half_assembly.convert("RGB").save(ALIGNED / "assembly_halfblink_preview.jpg", quality=94)

ear_assembly = Image.new("RGBA", head.size, (238, 239, 241, 255))
ear_assembly.alpha_composite(body)
ear_assembly.alpha_composite(neck)
ear_assembly.alpha_composite(Image.open(ALIGNED / "wolf_ear_left_aligned.png").convert("RGBA"))
ear_assembly.alpha_composite(Image.open(ALIGNED / "wolf_ear_right_aligned.png").convert("RGBA"))
ear_assembly.alpha_composite(earless)
ear_assembly.alpha_composite(collar)
ear_assembly.convert("RGB").save(ALIGNED / "assembly_ears_preview.jpg", quality=94)
print(f"aligned canvas: {head.size[0]}x{head.size[1]}")
