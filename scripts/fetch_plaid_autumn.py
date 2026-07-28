"""Fetch plaid autumn look product titles from Amazon."""

from __future__ import annotations

import json
import re
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "products" / "plaid-autumn-look"
H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0.0.0"}

LINKS = {
  "shirt": "https://link.amazon/B0bQwE0Wp",
  "skirt": "https://link.amazon/B0bk2glQ1",
  "cardigan": "https://link.amazon/B01ejqyHj",
  "necklace": "https://link.amazon/B01I95woS",
  "earrings": "https://link.amazon/B0h2yihG9",
  "sunglasses": "https://link.amazon/B03xq88cj",
  "bag": "https://link.amazon/B036SFQ5I",
  "shoes": "https://link.amazon/B05eIJuvq",
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
  return None


def clean_title(raw: str) -> str:
  title = re.sub(r"&#x27;", "'", raw)
  title = re.sub(r"\s*:\s*Amazon\.ae.*$", "", title, flags=re.I)
  title = re.sub(r"\s*\|\s*Amazon\.ae.*$", "", title, flags=re.I)
  return title.strip()[:80]


def main() -> None:
  OUT.mkdir(parents=True, exist_ok=True)
  meta: dict = {}
  for name, url in LINKS.items():
    r = requests.get(url, headers=H, timeout=45, allow_redirects=True)
    html = r.text
    title_m = re.search(r"<title>([^<]+)</title>", html)
    title = clean_title(title_m.group(1)) if title_m else name.title()
    img = extract_image(html)
    entry = {"affiliate": url, "final_url": r.url, "title": title, "image_url": img}
    print(name, "->", title[:70])
    meta[name] = entry
  (OUT / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")


if __name__ == "__main__":
  main()
