from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets" / "live2d"


def clean_neck_edge() -> None:
    source = Image.open(ASSETS / "neck_body_aligned.png").convert("RGBA")
    data = np.asarray(source).copy()
    rgb = data[..., :3].astype(np.float32)
    alpha = source.getchannel("A")

    # Remove the final antialiased fringe instead of hiding it with a page filter.
    clean_alpha = alpha.filter(ImageFilter.MinFilter(5))

    # Neutralize residual green-screen spill in the remaining neck pixels.
    strongest_neighbor = np.maximum(rgb[..., 0], rgb[..., 2])
    spill = (np.asarray(clean_alpha) > 0) & (rgb[..., 1] > strongest_neighbor * 0.94)
    rgb[..., 1][spill] = strongest_neighbor[spill] * 0.9

    data[..., :3] = np.clip(rgb, 0, 255).astype(np.uint8)
    data[..., 3] = np.asarray(clean_alpha)
    Image.fromarray(data, "RGBA").save(ASSETS / "neck_body_clean_v2.png")


def build_clean_cranium_mask() -> None:
    source = Image.open(ASSETS / "cranium_earless_aligned.png").convert("RGBA")
    alpha = source.getchannel("A").filter(ImageFilter.MinFilter(5))
    mask = Image.new("RGBA", source.size, (255, 255, 255, 0))
    mask.putalpha(alpha)
    mask.save(ASSETS / "cranium_earless_mask_clean_v1.png")


clean_neck_edge()
build_clean_cranium_mask()
print("cleaned neck edge and cranium alpha mask")
