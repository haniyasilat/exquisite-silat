"""Fetch red floral look products and style assets."""

from __future__ import annotations

import json
import re
from pathlib import Path

import requests
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "products" / "red-floral-look"
CURSOR = Path(
  r"C:\Users\hnsil\.cursor\projects\c-Users-hnsil-OneDrive-Middlesex-University-summer-26-projects-pinterest-wordpress\assets"
)
H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0.0.0"}

LINKS = {
  "shirt": "https://link.amazon/B0ahpzR7z",
  "skirt": "https://link.amazon/B0dF0T4jL",
  "bag": "https://link.amazon/B03SLr3nF",
  "shoes": "https://link.amazon/B0fO82l8Z",
  "earrings": "https://link.amazon/B0bWLrfPy",
  "perfume": "https://link.amazon/B07xS1km3",
}


def extract_image(html: str) -> str | None:
  for pat in (
    r'"hiRes":"(https:[^"]+)"',
    r'data-old-hires="([^"]+)"',
    r'property="og:image"\s+content="([^"]+)"',
  ):
    m = re.search(pat, html)
    if m:
      return m.group(1).replace("\\u002F", "/")
  imgs = re.findall(r"https://m\.media-amazon\.com/images/I/[A-Za-z0-9+._%-]+_AC_SL1500_\.jpg", html)
  return imgs[0] if imgs else None


def copy_style_assets() -> None:
  OUT.mkdir(parents=True, exist_ok=True)
  # Assets may only exist in chat workspace; skip missing files gracefully.
  for pattern, name in (
    ("*6a2fde7a93fa*", "bow.png"),
    ("*backgro-c9935bdb*", "bg-hibiscus.png"),
    ("*backgro-a66eb8f0*", "bg-flowers-left.png"),
  ):
    dst = OUT / name
    if dst.exists():
      continue
    for p in CURSOR.glob(pattern):
      try:
        Image.open(p).save(dst)
        print("style", name)
        break
      except OSError:
        continue


def main() -> None:
  copy_style_assets()
  meta: dict = {}
  for name, url in LINKS.items():
    r = requests.get(url, headers=H, timeout=45, allow_redirects=True)
    html = r.text
    img = extract_image(html)
    title_m = re.search(r"<title>([^<]+)</title>", html)
    title = title_m.group(1).strip() if title_m else name
    entry = {"affiliate": url, "final_url": r.url, "title": title, "image_url": img}
    if img:
      data = requests.get(img, headers=H, timeout=45).content
      (OUT / f"{name}.jpg").write_bytes(data)
      entry["local"] = f"assets/products/red-floral-look/{name}.jpg"
      print(name, len(data))
    else:
      print(name, "NO IMAGE")
    meta[name] = entry
  (OUT / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")


if __name__ == "__main__":
  main()
