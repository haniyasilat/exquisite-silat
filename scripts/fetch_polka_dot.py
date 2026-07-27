"""Fetch polka dot look product images from Amazon affiliate links."""

from __future__ import annotations

import json
import re
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "products" / "polka-dot-look"
H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0.0.0"}

LINKS = {
  "shirt": "https://link.amazon/B09AW8fJE",
  "pants": "https://link.amazon/B0jdFdrDa",
  "shoes": "https://link.amazon/B0gvUPJei",
  "bag": "https://link.amazon/B0gfFXWdx",
  "earrings": "https://link.amazon/B02T3U6iL",
}


def extract_image(html: str) -> str | None:
  for pat in (
    r'"hiRes":"(https:[^"]+)"',
    r'data-old-hires="([^"]+)"',
    r'property="og:image"\s+content="([^"]+)"',
    r'"large":"(https:[^"]+)"',
  ):
    m = re.search(pat, html)
    if m:
      return m.group(1).replace("\\u002F", "/")
  imgs = re.findall(r"https://m\.media-amazon\.com/images/I/[A-Za-z0-9+._%-]+\.jpg", html)
  return imgs[0] if imgs else None


def main() -> None:
  raw = OUT / "raw"
  raw.mkdir(parents=True, exist_ok=True)
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
      path = raw / f"{name}.jpg"
      path.write_bytes(data)
      entry["local"] = str(path.relative_to(ROOT)).replace("\\", "/")
      print(name, len(data), title[:60])
    else:
      print(name, "NO IMAGE")
    meta[name] = entry
  (OUT / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")


if __name__ == "__main__":
  main()
