"""Build polka dot & black chic collage — white canvas, lace left border."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets" / "products" / "polka-dot-look"
CUTOUTS = SRC / "cutouts" / "final"
OUT = SRC / "collage.png"
PREVIEW = SRC / "collage-preview.jpg"
CANVAS_W, CANVAS_H = 1200, 1500


def trim_white(img: Image.Image) -> Image.Image:
  px = img.load()
  w, h = img.size
  for y in range(h):
    for x in range(w):
      r, g, b, a = px[x, y]
      if a < 12:
        px[x, y] = (0, 0, 0, 0)
      elif r > 245 and g > 245 and b > 245:
        px[x, y] = (255, 255, 255, 0)
  bbox = img.getbbox()
  return img.crop(bbox) if bbox else img


def scale(img: Image.Image, max_w: int, max_h: int) -> Image.Image:
  img = trim_white(img)
  img.thumbnail((max_w, max_h), Image.Resampling.LANCZOS)
  return img


def soft_shadow(img: Image.Image, blur: int = 16, opacity: int = 38) -> Image.Image:
  pad = blur * 3
  shadow = Image.new("RGBA", (img.width + pad * 2, img.height + pad * 2), (0, 0, 0, 0))
  mask = img.split()[-1]
  sh = Image.new("RGBA", img.size, (30, 25, 25, opacity))
  shadow.paste(sh, (pad, pad + 5), mask)
  shadow = shadow.filter(ImageFilter.GaussianBlur(blur))
  shadow.alpha_composite(img, (pad, pad))
  return shadow


def paste_center(canvas: Image.Image, img: Image.Image, cx: int, cy: int) -> None:
  canvas.alpha_composite(img, (int(cx - img.width / 2), int(cy - img.height / 2)))


def lace_border(w: int, h: int) -> Image.Image:
  """Ornate black lace strip for left edge."""
  strip = Image.new("RGBA", (w, h), (0, 0, 0, 0))
  draw = ImageDraw.Draw(strip)
  for y in range(0, h, 28):
    draw.ellipse((8, y, 52, y + 44), outline=(20, 20, 20, 200), width=2)
    draw.ellipse((22, y + 10, 38, y + 26), fill=(15, 15, 15, 180))
    if y % 56 == 0:
      draw.line((30, y, 30, y + 80), fill=(25, 25, 25, 160), width=1)
      draw.ellipse((18, y + 50, 42, y + 74), outline=(20, 20, 20, 150), width=1)
  strip = strip.filter(ImageFilter.GaussianBlur(0.4))
  return strip


def main() -> None:
  canvas = Image.new("RGBA", (CANVAS_W, CANVAS_H), (255, 255, 255, 255))
  lace = lace_border(130, CANVAS_H)
  canvas.alpha_composite(lace, (0, 0))

  raw = {name: Image.open(CUTOUTS / f"{name}.png").convert("RGBA") for name in (
    "shirt", "pants", "shoes", "bag", "earrings"
  )}

  paste_center(canvas, soft_shadow(scale(raw["earrings"], 200, 200)), 300, 300)
  paste_center(canvas, soft_shadow(scale(raw["shirt"], 520, 560)), 740, 400)
  paste_center(canvas, soft_shadow(scale(raw["bag"], 280, 280)), 340, 720)
  paste_center(canvas, soft_shadow(scale(raw["pants"], 400, 780)), 740, 960)
  paste_center(canvas, soft_shadow(scale(raw["shoes"], 340, 200)), 560, 1280)

  final = canvas.convert("RGB")
  final.save(OUT, "PNG", optimize=True)
  preview = final.copy()
  preview.thumbnail((800, 1000), Image.Resampling.LANCZOS)
  preview.save(PREVIEW, "JPEG", quality=92)
  print("Wrote", OUT)


if __name__ == "__main__":
  main()
