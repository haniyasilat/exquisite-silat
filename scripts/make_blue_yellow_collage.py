"""Build blue-yellow polka + gold corner border collage."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter
from rembg import remove

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets" / "products" / "blue-yellow-look"
CUTOUTS = SRC / "cutouts"
OUT = SRC / "collage.png"
PREVIEW = SRC / "collage-preview.jpg"
CURSOR_ASSETS = Path(
  r"C:\Users\hnsil\.cursor\projects\c-Users-hnsil-OneDrive-Middlesex-University-summer-26-projects-pinterest-wordpress\assets"
)


def rembg_file(src: Path, dst: Path, force: bool = False) -> Image.Image:
  if dst.exists() and not force and dst.stat().st_size > 0:
    return Image.open(dst).convert("RGBA")
  # Pre-key white product photo backgrounds before rembg
  base = Image.open(src).convert("RGBA")
  px = base.load()
  w, h = base.size
  for y in range(h):
    for x in range(w):
      r, g, b, a = px[x, y]
      if r > 240 and g > 240 and b > 240:
        px[x, y] = (255, 255, 255, 0)
  from io import BytesIO

  buf = BytesIO()
  base.save(buf, format="PNG")
  out = remove(buf.getvalue())
  dst.write_bytes(out)
  return Image.open(dst).convert("RGBA")


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


def soft_shadow(img: Image.Image, blur: int = 16, opacity: int = 42) -> Image.Image:
  pad = blur * 3
  shadow = Image.new("RGBA", (img.width + pad * 2, img.height + pad * 2), (0, 0, 0, 0))
  mask = img.split()[-1]
  sh = Image.new("RGBA", img.size, (35, 30, 20, opacity))
  shadow.paste(sh, (pad, pad + 5), mask)
  shadow = shadow.filter(ImageFilter.GaussianBlur(blur))
  shadow.alpha_composite(img, (pad, pad))
  return shadow


def paste_center(canvas: Image.Image, img: Image.Image, cx: int, cy: int) -> None:
  x = int(cx - img.width / 2)
  y = int(cy - img.height / 2)
  canvas.alpha_composite(img, (x, y))


def polka_background(w: int, h: int) -> Image.Image:
  canvas = Image.new("RGBA", (w, h), (255, 249, 196, 255))
  draw = ImageDraw.Draw(canvas)
  spacing = 44
  radius = 7
  dot = (173, 216, 230)
  for y in range(-spacing, h + spacing, spacing):
    for x in range(-spacing, w + spacing, spacing):
      ox = x + (spacing // 2 if ((y // spacing) % 2) else 0)
      draw.ellipse((ox - radius, y - radius, ox + radius, y + radius), fill=(*dot, 255))
  return canvas


def procedural_corners(canvas: Image.Image) -> None:
  overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
  draw = ImageDraw.Draw(overlay)
  w, h = canvas.size
  size = 280
  gold = (186, 140, 62)
  corners = {
    "tl": (0, 0, 1, 1, 180, 270),
    "tr": (w, 0, -1, 1, 270, 360),
    "bl": (0, h, 1, -1, 90, 180),
    "br": (w, h, -1, -1, 0, 90),
  }
  for cx, cy, dx, dy, a0, a1 in corners.values():
    for t in range(12, size, 24):
      draw.line([(cx, cy + dy * t), (cx + dx * t, cy)], fill=(*gold, 200), width=2)
    for rad in (70, 110, 150):
      x0 = cx if dx > 0 else cx - rad
      y0 = cy if dy > 0 else cy - rad
      x1 = cx + rad if dx > 0 else cx
      y1 = cy + rad if dy > 0 else cy
      draw.arc((x0, y0, x1, y1), a0, a1, fill=(*gold, 190), width=2)
    bx, by = cx + dx * 36, cy + dy * 36
    draw.ellipse((bx - 6, by - 6, bx + 6, by + 6), outline=(*gold, 220), width=2)
  canvas.alpha_composite(overlay)


def prepare_cutouts() -> dict[str, Image.Image]:
  CUTOUTS.mkdir(parents=True, exist_ok=True)
  items: dict[str, Image.Image] = {}

  garment_sources = {
    "shirt": [SRC / "shirt-cutout.png", CURSOR_ASSETS / "yellow-shirt-cutout.png"],
    "jeans": [SRC / "jeans-cutout.png", CURSOR_ASSETS / "navy-jeans-cutout.png"],
  }

  for name in ("shirt", "jeans", "shoes", "bag", "glasses", "necklace", "earrings", "flower"):
    src = None
    if name in garment_sources:
      for candidate in garment_sources[name]:
        if candidate.exists():
          src = candidate
          break
    if src is None:
      src = SRC / f"{name}.jpg"
      if not src.exists():
        src = SRC / f"{name}.png"
    if not src.exists():
      continue
    try:
      items[name] = rembg_file(src, CUTOUTS / f"{name}.png", force=True)
    except Exception as exc:  # noqa: BLE001
      print("skip", name, exc)
  return items


def main() -> None:
  raw = prepare_cutouts()
  if "shirt" not in raw:
    raise SystemExit("Missing shirt.jpg — run scripts/_tmp_fetch2.py first")

  canvas = polka_background(1200, 1500)

  if "flower" in raw:
    # Skip if flower asset is tiny / not a real bloom (bad pin scrape)
    flower_src = SRC / "flower.jpg"
    if flower_src.exists() and flower_src.stat().st_size > 80000:
      paste_center(canvas, soft_shadow(scale(raw["flower"], 280, 280), blur=14, opacity=30), 560, 720)

  paste_center(canvas, soft_shadow(scale(raw["necklace"], 210, 210)), 380, 270)
  paste_center(canvas, soft_shadow(scale(raw["glasses"], 230, 140)), 395, 460)
  paste_center(canvas, soft_shadow(scale(raw["bag"], 380, 380)), 400, 700)
  paste_center(canvas, soft_shadow(scale(raw["shoes"], 400, 290)), 400, 1020)
  paste_center(canvas, soft_shadow(scale(raw["shirt"], 620, 680)), 720, 330)
  paste_center(canvas, soft_shadow(scale(raw["jeans"], 480, 900)), 720, 930)

  procedural_corners(canvas)

  final = canvas.convert("RGB")
  final.save(OUT, "PNG", optimize=True)
  preview = final.copy()
  preview.thumbnail((800, 1000), Image.Resampling.LANCZOS)
  preview.save(PREVIEW, "JPEG", quality=92)
  print("Wrote", OUT)


if __name__ == "__main__":
  main()
