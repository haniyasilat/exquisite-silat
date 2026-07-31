"""Fetch product images for teal elevate basic look."""

from __future__ import annotations

import json
import re
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "products" / "teal-elevate-look"
HEADERS = {
  "User-Agent": (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
  ),
  "Accept-Language": "en-US,en;q=0.9",
}

LINKS = {
  "skirt": "https://link.amazon/B0h2sv9CT",
  "shirt": "https://link.amazon/B0jlViWJq",
  "bag": "https://link.amazon/B0j4P8T2Q",
  "teal_shirt": "https://link.amazon/B07tPuDs1",
  "belt": "https://link.amazon/B0gvpdUeN",
  "earrings": "https://link.amazon/B0b8nLrrj",
  "bangle": "https://link.amazon/B0ejFsCDh",
  "heels": "https://link.amazon/B0dW22S1Q",
}


def extract_image(html: str) -> str | None:
  patterns = [
    r'"hiRes":"(https:[^"]+)"',
    r'data-old-hires="([^"]+)"',
    r'property="og:image"\s+content="([^"]+)"',
    r'content="([^"]+)"\s+property="og:image"',
    r'"large":"(https:[^"]+)"',
  ]
  for pat in patterns:
    m = re.search(pat, html)
    if m:
      return m.group(1).replace("\\u002F", "/")
  imgs = re.findall(r"https://m\.media-amazon\.com/images/I/[A-Za-z0-9+._%-]+_AC_SL1500_\.jpg", html)
  return imgs[0] if imgs else None


def clean_title(raw: str) -> str:
  title = re.sub(r"&#x27;", "'", raw)
  title = re.sub(r"\s*:\s*Buy Online.*$", "", title, flags=re.I)
  title = re.sub(r"\s*:\s*Amazon\.[^:]*$", "", title, flags=re.I)
  title = re.sub(r"\s*\|\s*Amazon\.[^|]*$", "", title, flags=re.I)
  return title.strip()


def main() -> None:
  OUT.mkdir(parents=True, exist_ok=True)
  meta: dict = {}
  for name, url in LINKS.items():
    r = requests.get(url, headers=HEADERS, timeout=45, allow_redirects=True)
    html = r.text
    title_m = re.search(r"<title>([^<]+)</title>", html)
    title = clean_title(title_m.group(1)) if title_m else name.replace("_", " ").title()
    img = extract_image(html)
    entry = {"affiliate": url, "final_url": r.url, "title": title, "image_url": img}
    print(name, "->", title[:85])
    if img:
      ir = requests.get(img, headers=HEADERS, timeout=45)
      ext = ".png" if ".png" in img.lower() else ".jpg"
      path = OUT / f"{name}{ext}"
      path.write_bytes(ir.content)
      entry["local"] = path.name
      print("  saved", path.name, len(ir.content))
    else:
      print("  NO IMAGE")
    meta[name] = entry
  (OUT / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")


if __name__ == "__main__":
  main()
