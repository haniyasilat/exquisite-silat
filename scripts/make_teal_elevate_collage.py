"""Build teal elevate basic look collage with headline text."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont
from rembg import remove

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets" / "products" / "teal-elevate-look"
CUTOUTS = SRC / "cutouts"
OUT = SRC / "collage.png"
CANVAS_W, CANVAS_H = 1200, 1500
TEAL = (15, 118, 128)
CREAM = (252, 249, 244, 255)


def rembg_file(src: Path, dst: Path) -> Image.Image:
  base = Image.open(src).convert("RGBA")
  px = base.load()
  w, h = base.size
  for y in range(h):
    for x in range(w):
      r, g, b, a = px[x, y]
      if r > 240 and g > 240 and b > 240:
        px[x, y] = (255, 255, 255, 0)
  buf = BytesIO()
  base.save(buf, format="PNG")
  out = remove(buf.getvalue())
  dst.write_bytes(out)
  return Image.open(dst).convert("RGBA")


def trim(img: Image.Image) -> Image.Image:
  bbox = img.getbbox()
  return img.crop(bbox) if bbox else img


def scale(img: Image.Image, max_w: int, max_h: int) -> Image.Image:
  img = trim(img)
  img.thumbnail((max_w, max_h), Image.Resampling.LANCZOS)
  return img


def shadow(img: Image.Image, blur: int = 14, opacity: int = 38) -> Image.Image:
  pad = blur * 3
  layer = Image.new("RGBA", (img.width + pad * 2, img.height + pad * 2), (0, 0, 0, 0))
  mask = img.split()[-1]
  sh = Image.new("RGBA", img.size, (35, 30, 28, opacity))
  layer.paste(sh, (pad, pad + 4), mask)
  layer = layer.filter(ImageFilter.GaussianBlur(blur))
  layer.alpha_composite(img, (pad, pad))
  return layer


def paste(canvas: Image.Image, img: Image.Image, cx: int, cy: int) -> None:
  canvas.alpha_composite(img, (int(cx - img.width / 2), int(cy - img.height / 2)))


def load_cutout(name: str) -> Image.Image:
  CUTOUTS.mkdir(parents=True, exist_ok=True)
  src = SRC / f"{name}.jpg"
  dst = CUTOUTS / f"{name}.png"
  if not dst.exists() or dst.stat().st_size == 0:
    rembg_file(src, dst)
  return Image.open(dst).convert("RGBA")


def draw_headline(canvas: Image.Image) -> None:
  draw = ImageDraw.Draw(canvas)
  try:
    title_font = ImageFont.truetype("C:/Windows/Fonts/georgia.ttf", 42)
    sub_font = ImageFont.truetype("C:/Windows/Fonts/georgia.ttf", 30)
  except OSError:
    title_font = ImageFont.load_default()
    sub_font = ImageFont.load_default()

  lines = [
    "How to Elevate a Basic Look",
    "with Teal — The Colour of Summer 2026",
  ]
  y = 52
  for i, line in enumerate(lines):
    font = title_font if i == 0 else sub_font
    bbox = draw.textbbox((0, 0), line, font=font)
    tw = bbox[2] - bbox[0]
    x = (CANVAS_W - tw) // 2
    draw.text((x + 1, y + 1), line, fill=(220, 220, 220, 180), font=font)
    draw.text((x, y), line, fill=TEAL + (255,), font=font)
    y += (bbox[3] - bbox[1]) + 14

  draw.line((120, 188, CANVAS_W - 120, 188), fill=TEAL + (90,), width=2)


def main() -> None:
  items = {
    "shirt": scale(load_cutout("shirt"), 360, 420),
    "skirt": scale(load_cutout("skirt"), 420, 760),
    "teal_shirt": scale(load_cutout("teal_shirt"), 300, 360),
    "bag": scale(load_cutout("bag"), 280, 280),
    "belt": scale(load_cutout("belt"), 260, 120),
    "earrings": scale(load_cutout("earrings"), 150, 150),
    "bangle": scale(load_cutout("bangle"), 170, 170),
    "heels": scale(load_cutout("heels"), 250, 180),
  }

  canvas = Image.new("RGBA", (CANVAS_W, CANVAS_H), CREAM)

  # Soft teal wash at top
  top = Image.new("RGBA", (CANVAS_W, 220), (230, 246, 248, 120))
  canvas.alpha_composite(top, (0, 0))

  draw_headline(canvas)

  # Base look — left
  paste(canvas, shadow(items["shirt"]), 310, 520)
  paste(canvas, shadow(items["skirt"]), 320, 980)

  # Elevate pieces — right
  paste(canvas, shadow(items["teal_shirt"]), 860, 360)
  paste(canvas, shadow(items["bag"]), 870, 620)
  paste(canvas, shadow(items["earrings"]), 650, 360)
  paste(canvas, shadow(items["bangle"]), 650, 540)
  paste(canvas, shadow(items["belt"]), 860, 820)
  paste(canvas, shadow(items["heels"]), 870, 1080)

  final = canvas.convert("RGB")
  final.save(OUT, "PNG", optimize=True)
  print("Wrote", OUT)


if __name__ == "__main__":
  main()
