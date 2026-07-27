"""Batch-remove backgrounds from product photos and zip the cutouts.

Usage:
  python scripts/batch_cutouts.py path/to/images/
  python scripts/batch_cutouts.py shirt.jpg jeans.png bag.webp
  python scripts/batch_cutouts.py path/to/images/ --out my-look-cutouts.zip

Drop your pics in a folder (or pass files directly). Each image becomes a
transparent PNG cutout named after the original file.
"""

from __future__ import annotations

import argparse
import zipfile
from io import BytesIO
from pathlib import Path

from PIL import Image
from rembg import remove

ROOT = Path(__file__).resolve().parent.parent
SUPPORTED = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif"}


def strip_near_white(img: Image.Image) -> Image.Image:
  px = img.load()
  w, h = img.size
  for y in range(h):
    for x in range(w):
      r, g, b, a = px[x, y]
      if r > 240 and g > 240 and b > 240:
        px[x, y] = (255, 255, 255, 0)
  return img


def cutout(src: Path) -> Image.Image:
  base = Image.open(src).convert("RGBA")
  base = strip_near_white(base)
  buf = BytesIO()
  base.save(buf, format="PNG")
  out = remove(buf.getvalue())
  img = Image.open(BytesIO(out)).convert("RGBA")
  bbox = img.getbbox()
  return img.crop(bbox) if bbox else img


def collect_inputs(paths: list[Path]) -> list[Path]:
  files: list[Path] = []
  for path in paths:
    if path.is_dir():
      files.extend(sorted(p for p in path.iterdir() if p.suffix.lower() in SUPPORTED))
    elif path.suffix.lower() in SUPPORTED:
      files.append(path)
  return files


def main() -> None:
  parser = argparse.ArgumentParser(description="Remove backgrounds and zip cutouts.")
  parser.add_argument("inputs", nargs="+", type=Path, help="Image files or folders")
  parser.add_argument(
    "--out",
    type=Path,
    help="Output zip path (default: cutouts/<folder-name>-cutouts.zip)",
  )
  parser.add_argument(
    "--dir",
    type=Path,
    default=ROOT / "cutouts",
    help="Folder for PNG cutouts before zipping",
  )
  args = parser.parse_args()

  sources = collect_inputs(args.inputs)
  if not sources:
    raise SystemExit("No images found. Use jpg, png, or webp files.")

  out_dir = args.dir
  out_dir.mkdir(parents=True, exist_ok=True)

  written: list[Path] = []
  for src in sources:
    name = f"{src.stem}-cutout.png"
    dst = out_dir / name
    print(f"Processing {src.name} -> {dst.name}")
    cutout(src).save(dst, "PNG", optimize=True)
    written.append(dst)

  if args.out:
    zip_path = args.out
  else:
    label = args.inputs[0].stem if len(args.inputs) == 1 and args.inputs[0].is_file() else "batch"
    zip_path = out_dir / f"{label}-cutouts.zip"

  zip_path.parent.mkdir(parents=True, exist_ok=True)
  with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
    for path in written:
      zf.write(path, arcname=path.name)

  print(f"Wrote {len(written)} cutouts")
  print(f"Zip: {zip_path}")


if __name__ == "__main__":
  main()
