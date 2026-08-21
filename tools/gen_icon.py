from PIL import Image, ImageDraw

BG = (8, 12, 15)
CYAN = (109, 251, 211)
YELLOW = (242, 206, 91)


def draw_icon(size):
    img = Image.new("RGB", (size, size), BG)
    d = ImageDraw.Draw(img)
    s = size / 512.0
    pts = [(166, 176), (346, 176), (302, 230), (210, 230),
           (302, 282), (258, 336), (166, 336), (210, 282), (122, 230)]
    d.polygon([(x * s, y * s) for x, y in pts], fill=CYAN)
    cx, cy, r = 386 * s, 126 * s, 18 * s
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=YELLOW)
    return img


if __name__ == "__main__":
    draw_icon(512).save("icons/icon-512.png")
    draw_icon(192).save("icons/icon-192.png")
    print("icons generated")
