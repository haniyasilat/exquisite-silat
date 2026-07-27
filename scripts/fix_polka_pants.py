"""Pants cutout with natural leg drape from Amazon product photo."""

from __future__ import annotations

import zipfile
from io import BytesIO
from pathlib import Path

from PIL import Image
from rembg import remove

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets" / "products" / "polka-dot-look" / "raw" / "pants.jpg"
OUT = ROOT / "assets" / "products" / "polka-dot-look" / "cutouts" / "final" / "pants.png"
ZIP = ROOT / "assets" / "products" / "polka-dot-look" / "polka-dot-cutouts.zip"


def is_skin(r: int, g: int, b: int) -> bool:
  return r > 90 and g > 50 and b > 30 and r > g and r > b and (r - g) > 12


def is_white(r: int, g: int, b: int) -> bool:
  return r > 210 and g > 210 and b > 210


def is_shoe(r: int, g: int, b: int) -> bool:
  return r > 160 and g > 140 and b > 100 and b < 200


def main() -> None:
  base = Image.open(SRC).convert("RGBA")
  buf = BytesIO()
  base.save(buf, format="PNG")
  cut = Image.open(BytesIO(remove(buf.getvalue()))).convert("RGBA")

  w, h = cut.size
  leg = cut.crop((int(w * 0.05), int(h * 0.12), int(w * 0.95), int(h * 0.82)))
  px = leg.load()
  lw, lh = leg.size

  for y in range(lh):
    for x in range(lw):
      r, g, b, a = px[x, y]
      if a < 20:
        continue
      if is_skin(r, g, b):
        px[x, y] = (0, 0, 0, 0)
      elif y < int(lh * 0.06) and is_white(r, g, b):
        px[x, y] = (0, 0, 0, 0)
      elif y > int(lh * 0.9) and (is_shoe(r, g, b) or is_white(r, g, b)):
        px[x, y] = (0, 0, 0, 0)

  bbox = leg.getbbox()
  if bbox:
    leg = leg.crop(bbox)

  OUT.parent.mkdir(parents=True, exist_ok=True)
  leg.save(OUT, "PNG", optimize=True)
  print("Wrote", OUT, leg.size)

  with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as zf:
    for p in sorted(OUT.parent.glob("*.png")):
      zf.write(p, p.name)
  print("Updated", ZIP)


if __name__ == "__main__":
  main()
