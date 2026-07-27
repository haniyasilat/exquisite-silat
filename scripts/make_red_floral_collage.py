"""Red floral look collage — hibiscus bg, bow accent, darker shirt."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path

from PIL import Image, ImageEnhance, ImageFilter
from rembg import remove

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets" / "products" / "red-floral-look"
CUTOUTS = SRC / "cutouts"
OUT = SRC / "collage.png"
PREVIEW = SRC / "collage-preview.jpg"
CANVAS_W, CANVAS_H = 1200, 1500
CURSOR_ASSETS = Path(
  r"C:\Users\hnsil\.cursor\projects\c-Users-hnsil-OneDrive-Middlesex-University-summer-26-projects-pinterest-wordpress\assets"
)


def rembg_file(src: Path, dst: Path, force: bool = False) -> Image.Image:
  if dst.exists() and not force and dst.stat().st_size > 0:
    return Image.open(dst).convert("RGBA")
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


def darken_shirt(img: Image.Image) -> Image.Image:
  """User asked for shirt color a little darker."""
  rgb = img.convert("RGB")
  rgb = ImageEnhance.Brightness(rgb).enhance(0.78)
  rgb = ImageEnhance.Color(rgb).enhance(1.08)
  rgb = ImageEnhance.Contrast(rgb).enhance(1.12)
  out = rgb.convert("RGBA")
  out.putalpha(img.split()[-1])
  return out


def soft_shadow(img: Image.Image, blur: int = 16, opacity: int = 40) -> Image.Image:
  pad = blur * 3
  shadow = Image.new("RGBA", (img.width + pad * 2, img.height + pad * 2), (0, 0, 0, 0))
  mask = img.split()[-1]
  sh = Image.new("RGBA", img.size, (40, 20, 25, opacity))
  shadow.paste(sh, (pad, pad + 5), mask)
  shadow = shadow.filter(ImageFilter.GaussianBlur(blur))
  shadow.alpha_composite(img, (pad, pad))
  return shadow


def paste_center(canvas: Image.Image, img: Image.Image, cx: int, cy: int) -> None:
  canvas.alpha_composite(img, (int(cx - img.width / 2), int(cy - img.height / 2)))


def build_background() -> Image.Image:
  bg_path = SRC / "bg-hibiscus.png"
  if bg_path.exists():
    bg = Image.open(bg_path).convert("RGBA")
    return bg.resize((CANVAS_W, CANVAS_H), Image.Resampling.LANCZOS)
  return Image.new("RGBA", (CANVAS_W, CANVAS_H), (250, 246, 240, 255))


def add_left_flower_border(canvas: Image.Image) -> None:
  path = SRC / "bg-flowers-left.png"
  if not path.exists():
    return
  strip = Image.open(path).convert("RGBA")
  target_h = CANVAS_H
  target_w = int(strip.width * (target_h / strip.height) * 0.55)
  strip = strip.resize((target_w, target_h), Image.Resampling.LANCZOS)
  canvas.alpha_composite(strip, (0, 0))


def add_bow(canvas: Image.Image) -> None:
  path = SRC / "bow.png"
  if not path.exists():
    return
  bow = trim_white(Image.open(path).convert("RGBA"))
  bow = bow.resize((110, 110), Image.Resampling.LANCZOS)
  paste_center(canvas, bow, 880, 165)


def prepare_cutouts() -> dict[str, Image.Image]:
  CUTOUTS.mkdir(parents=True, exist_ok=True)
  items: dict[str, Image.Image] = {}

  cutout_sources = {
    "shirt": [SRC / "shirt-cutout.png", CURSOR_ASSETS / "shirt-cutout-red-floral.png"],
    "skirt": [SRC / "skirt-cutout.png", CURSOR_ASSETS / "skirt-cutout-red-floral.png"],
  }

  for name in ("shirt", "skirt", "bag", "shoes", "earrings", "perfume"):
    src = None
    if name in cutout_sources:
      for candidate in cutout_sources[name]:
        if candidate.exists():
          src = candidate
          break
    if src is None:
      src = SRC / f"{name}.jpg"
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
    raise SystemExit("Missing shirt image")

  canvas = build_background()
  # Use hibiscus linen bg only — do not layer left flower strip (double-background).

  shirt_img = darken_shirt(scale(raw["shirt"], 560, 620))
  skirt_img = scale(raw["skirt"], 680, 1280)
  bag_img = scale(raw["bag"], 290, 290)
  shoes_img = scale(raw["shoes"], 340, 240)
  earrings_img = scale(raw["earrings"], 160, 160)
  perfume_img = scale(raw["perfume"], 125, 190)

  paste_center(canvas, soft_shadow(earrings_img), 300, 250)
  paste_center(canvas, soft_shadow(perfume_img), 300, 430)
  paste_center(canvas, soft_shadow(bag_img), 310, 690)
  paste_center(canvas, soft_shadow(shoes_img), 310, 1050)

  # Bigger outfit pieces, pulled together at the waist
  paste_center(canvas, soft_shadow(shirt_img), 700, 320)
  paste_center(canvas, soft_shadow(skirt_img), 700, 820)

  add_bow(canvas)

  final = canvas.convert("RGB")
  final.save(OUT, "PNG", optimize=True)
  preview = final.copy()
  preview.thumbnail((800, 1000), Image.Resampling.LANCZOS)
  preview.save(PREVIEW, "JPEG", quality=92)
  print("Wrote", OUT)


if __name__ == "__main__":
  main()
