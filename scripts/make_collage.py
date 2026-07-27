"""Build a Polyvore-style outfit collage from product cutouts."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter
from rembg import remove

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets" / "products" / "burgundy-look"
CURSOR_ASSETS = Path(
  r"C:\Users\hnsil\.cursor\projects\c-Users-hnsil-OneDrive-Middlesex-University-summer-26-projects-pinterest-wordpress\assets"
)
CUTOUTS = SRC / "cutouts"
OUT = SRC / "collage.png"
PREVIEW = SRC / "collage-preview.jpg"

# Soft blush canvas + dusty rose dots (fashion-board feel)
BG = (247, 240, 234)
DOT = (184, 120, 128)


def ensure_dirs() -> None:
  CUTOUTS.mkdir(parents=True, exist_ok=True)


def rembg_file(src: Path, dst: Path, force: bool = False) -> Image.Image:
  if dst.exists() and not force and dst.stat().st_size > 0:
    return Image.open(dst).convert("RGBA")
  data = src.read_bytes()
  out = remove(data)
  dst.write_bytes(out)
  return Image.open(dst).convert("RGBA")


def trim(img: Image.Image) -> Image.Image:
  # Drop near-white leftover fringe
  px = img.load()
  w, h = img.size
  for y in range(h):
    for x in range(w):
      r, g, b, a = px[x, y]
      if a < 12:
        px[x, y] = (0, 0, 0, 0)
      elif r > 248 and g > 248 and b > 248:
        px[x, y] = (255, 255, 255, 0)
  bbox = img.getbbox()
  return img.crop(bbox) if bbox else img


def scale(img: Image.Image, max_w: int, max_h: int) -> Image.Image:
  img = trim(img)
  img.thumbnail((max_w, max_h), Image.Resampling.LANCZOS)
  return img


def soft_shadow(img: Image.Image, blur: int = 18, opacity: int = 48) -> Image.Image:
  pad = blur * 3
  shadow = Image.new("RGBA", (img.width + pad * 2, img.height + pad * 2), (0, 0, 0, 0))
  mask = img.split()[-1]
  sh = Image.new("RGBA", img.size, (40, 28, 30, opacity))
  shadow.paste(sh, (pad, pad + 6), mask)
  shadow = shadow.filter(ImageFilter.GaussianBlur(blur))
  shadow.alpha_composite(img, (pad, pad))
  return shadow


def paste_center(canvas: Image.Image, img: Image.Image, cx: int, cy: int) -> None:
  x = int(cx - img.width / 2)
  y = int(cy - img.height / 2)
  canvas.alpha_composite(img, (x, y))


def polka_background(w: int, h: int) -> Image.Image:
  canvas = Image.new("RGBA", (w, h), (*BG, 255))
  draw = ImageDraw.Draw(canvas)
  spacing = 46
  radius = 5
  for y in range(-spacing, h + spacing, spacing):
    for x in range(-spacing, w + spacing, spacing):
      ox = x + (spacing // 2 if ((y // spacing) % 2) else 0)
      draw.ellipse((ox - radius, y - radius, ox + radius, y + radius), fill=(*DOT, 70))
  # soft vignette wash
  wash = Image.new("RGBA", (w, h), (0, 0, 0, 0))
  wd = ImageDraw.Draw(wash)
  for i, alpha in enumerate((18, 12, 6)):
    margin = 40 + i * 50
    wd.rounded_rectangle(
      (margin, margin, w - margin, h - margin),
      radius=80,
      outline=(255, 255, 255, alpha),
      width=40,
    )
  canvas = Image.alpha_composite(canvas, wash.filter(ImageFilter.GaussianBlur(30)))
  return canvas


def prepare_vine() -> Image.Image:
  """Load floral vine, key out white bg (no rembg), recolor to burgundy/cream scheme."""
  src = SRC / "vine-raw.png"
  if not src.exists():
    alt = CURSOR_ASSETS / (
      "c__Users_hnsil_AppData_Roaming_Cursor_User_workspaceStorage_empty-window_"
      "images_patter-78551104-536d-49c6-93ad-80ab0cd25d39.png"
    )
    src = alt

  img = Image.open(src).convert("RGBA")
  px = img.load()
  w, h = img.size
  for y in range(h):
    for x in range(w):
      r, g, b, a = px[x, y]
      # White / near-white background → transparent
      if r > 235 and g > 235 and b > 235:
        px[x, y] = (255, 255, 255, 0)
      elif r > 220 and g > 220 and b > 220:
        # Soft fringe — partial alpha
        fade = max(0, 255 - int((r + g + b) / 3))
        px[x, y] = (r, g, b, fade)

  img = trim(img)
  return recolor_vine(img)


def recolor_vine(img: Image.Image) -> Image.Image:
  """Map greens → dusty rose / muted burgundy; petals → cream / blush."""
  ruby = (122, 31, 43)
  dusty = (184, 120, 128)
  cream = (245, 240, 232)
  blush = (232, 200, 198)
  stem = (90, 40, 48)

  out = img.copy()
  px = out.load()
  w, h = out.size
  for y in range(h):
    for x in range(w):
      r, g, b, a = px[x, y]
      if a < 10:
        continue
      # luminance for shading
      lum = (0.299 * r + 0.587 * g + 0.114 * b) / 255.0
      # green foliage / stems
      if g > r + 8 and g > b + 5:
        # darker stem vs leaf
        if lum < 0.35:
          base = stem
        else:
          # blend dusty rose with a touch of muted olive-burgundy
          base = (
            int(dusty[0] * 0.75 + ruby[0] * 0.25),
            int(dusty[1] * 0.7 + 70 * 0.3),
            int(dusty[2] * 0.75 + ruby[2] * 0.25),
          )
        shade = 0.55 + lum * 0.55
        px[x, y] = (
          min(255, int(base[0] * shade)),
          min(255, int(base[1] * shade)),
          min(255, int(base[2] * shade)),
          a,
        )
      # cream / pink petals & buds
      elif r > 170 and g > 140 and b > 120:
        # pinker accents near centers (more saturated / darker)
        if r > g + 15:
          base = blush if lum > 0.55 else dusty
        else:
          base = cream if lum > 0.7 else blush
        shade = 0.7 + lum * 0.35
        px[x, y] = (
          min(255, int(base[0] * shade)),
          min(255, int(base[1] * shade)),
          min(255, int(base[2] * shade)),
          a,
        )
      # brownish centers / leftover midtones → ruby accents
      else:
        base = dusty if lum > 0.45 else ruby
        shade = 0.6 + lum * 0.5
        px[x, y] = (
          min(255, int(base[0] * shade)),
          min(255, int(base[1] * shade)),
          min(255, int(base[2] * shade)),
          a,
        )
  return out


def draw_border(canvas: Image.Image) -> Image.Image:
  """Floral vine borders on left and right (mirrored), brand-colored."""
  w, h = canvas.size
  framed = Image.new("RGBA", (w, h), (0, 0, 0, 0))
  framed.alpha_composite(canvas)

  vine = prepare_vine()
  # Scale vine to nearly full canvas height
  target_h = h - 24
  scale_factor = target_h / vine.height
  target_w = max(120, int(vine.width * scale_factor))
  vine = vine.resize((target_w, target_h), Image.Resampling.LANCZOS)

  left = vine.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
  right = vine

  y = (h - vine.height) // 2
  framed.alpha_composite(left, (0, y))
  framed.alpha_composite(right, (w - right.width, y))
  return framed


def prepare_cutouts() -> dict[str, Image.Image]:
  ensure_dirs()
  items: dict[str, Image.Image] = {}

  # Generated body-free garment cutouts (white bg → rembg)
  shirt_src = CURSOR_ASSETS / "shirt-cutout-prettygarden.png"
  if not shirt_src.exists():
    shirt_src = CURSOR_ASSETS / "shirt-cutout-new.png"
  if not shirt_src.exists():
    shirt_src = CURSOR_ASSETS / "shirt-cutout.png"
  jeans_src = CURSOR_ASSETS / "jeans-cutout-new.png"
  if not jeans_src.exists():
    jeans_src = CURSOR_ASSETS / "jeans-cutout.png"

  force_shirt = True
  shirt_out = CUTOUTS / "shirt.png"
  if shirt_out.exists() and shirt_src.exists():
    force_shirt = shirt_src.stat().st_mtime > shirt_out.stat().st_mtime
  items["shirt"] = rembg_file(shirt_src, shirt_out, force=force_shirt)
  items["jeans"] = rembg_file(jeans_src, CUTOUTS / "jeans.png")

  # Accessories from product photos
  for name in ("bag", "shoes", "watch", "earrings"):
    src = SRC / f"{name}.jpg"
    items[name] = rembg_file(src, CUTOUTS / f"{name}.png")

  # Lily accent — prefer generated/local file that is readable
  lily_candidates = []
  for pattern in ("*lily*", "*WhatsApp_Image_2026-07-27*"):
    for p in CURSOR_ASSETS.glob(pattern):
      try:
        if p.is_file() and p.stat().st_size > 0:
          p.read_bytes()[:16]
          lily_candidates.append(p)
      except OSError:
        continue
  if lily_candidates:
    try:
      items["lily"] = rembg_file(lily_candidates[0], CUTOUTS / "lily.png")
    except OSError as exc:
      print("Lily skipped:", exc)
  elif (CUTOUTS / "lily.png").exists():
    items["lily"] = Image.open(CUTOUTS / "lily.png").convert("RGBA")

  return items


def update_meta() -> None:
  meta_path = SRC / "meta.json"
  meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
  fetch = SRC / "_fetch.txt"
  data = {}
  if fetch.exists():
    for line in fetch.read_text(encoding="utf-8-sig").splitlines():
      if "=" in line:
        k, v = line.split("=", 1)
        data[k.strip()] = v.strip()

  meta["shirt"] = {
    "affiliate": "https://link.amazon/B08TSRX9K",
    "final_url": data.get("SHIRT_URL", meta.get("shirt", {}).get("final_url", "")),
    "title": data.get(
      "SHIRT_TITLE",
      "PRETTYGARDEN Long Sleeve Asymmetrical Tops Burgundy",
    ),
    "image_url": data.get("SHIRT_IMG", ""),
    "local": "assets/products/burgundy-look/shirt.jpg",
  }
  meta["bag"] = {
    "affiliate": "https://link.amazon/B0cvbClLk",
    "final_url": data.get("BAG_URL", meta.get("bag", {}).get("final_url", "")),
    "title": data.get("BAG_TITLE", "JW PEI Women's Harlee Shoulder Bag").replace("&#39;", "'"),
    "image_url": data.get("BAG_IMG", ""),
    "local": "assets/products/burgundy-look/bag.jpg",
  }
  meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
  print("Updated", meta_path)


def main() -> None:
  update_meta()
  raw = prepare_cutouts()

  canvas_w, canvas_h = 1200, 1500
  canvas = polka_background(canvas_w, canvas_h)

  shirt = soft_shadow(scale(raw["shirt"], 540, 600))
  jeans = soft_shadow(scale(raw["jeans"], 400, 780))
  bag = soft_shadow(scale(raw["bag"], 340, 340))
  shoes = soft_shadow(scale(raw["shoes"], 360, 250))
  watch = soft_shadow(scale(raw["watch"], 200, 200))
  earrings = soft_shadow(scale(raw["earrings"], 180, 200))
  lily = soft_shadow(scale(raw["lily"], 220, 220), blur=14, opacity=35) if "lily" in raw else None

  # Lily behind clothing/accessories (layer order only — original size/color)
  if lily is not None:
    paste_center(canvas, lily, 540, 680)

  # Tighter Polyvore layout — accessories + outfit pulled toward center
  paste_center(canvas, earrings, 320, 250)
  paste_center(canvas, watch, 340, 470)
  paste_center(canvas, bag, 360, 720)
  paste_center(canvas, shoes, 360, 1080)
  paste_center(canvas, shirt, 740, 340)
  paste_center(canvas, jeans, 740, 960)

  canvas = draw_border(canvas)
  final = canvas.convert("RGB")
  final.save(OUT, "PNG", optimize=True)
  preview = final.copy()
  preview.thumbnail((800, 1000), Image.Resampling.LANCZOS)
  preview.save(PREVIEW, "JPEG", quality=92)
  print("Wrote", OUT)
  print("Wrote", PREVIEW)


if __name__ == "__main__":
  main()
