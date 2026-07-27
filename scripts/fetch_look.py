"""Fetch Amazon product images for a look folder."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
HEADERS = {
  "User-Agent": (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
  ),
  "Accept-Language": "en-US,en;q=0.9",
}


def extract_image(html: str) -> str | None:
  patterns = [
    r'property="og:image"\s+content="([^"]+)"',
    r'content="([^"]+)"\s+property="og:image"',
    r'"hiRes":"(https:[^"]+)"',
    r'data-old-hires="([^"]+)"',
    r'"large":"(https:[^"]+)"',
  ]
  for pat in patterns:
    m = re.search(pat, html)
    if m:
      return m.group(1).replace("\\u002F", "/")
  return None


def fetch_look(out_dir: Path, links: dict[str, str]) -> None:
  out_dir.mkdir(parents=True, exist_ok=True)
  meta: dict = {}

  for name, url in links.items():
    print(f"\n=== {name} ===")
    try:
      r = requests.get(url, headers=HEADERS, timeout=45, allow_redirects=True)
      html = r.text
      img = extract_image(html)
      title_m = re.search(r"<title>([^<]+)</title>", html)
      title = title_m.group(1).strip() if title_m else name
      print("status", r.status_code)
      print("final", r.url[:140])
      print("img", (img or "")[:120])
      entry = {
        "affiliate": url,
        "final_url": r.url,
        "title": title,
        "image_url": img,
      }
      if img:
        ir = requests.get(img, headers=HEADERS, timeout=45)
        ext = ".png" if ".png" in img.lower() else ".jpg"
        path = out_dir / f"{name}{ext}"
        path.write_bytes(ir.content)
        entry["local"] = str(path.relative_to(ROOT)).replace("\\", "/")
        print("saved", path, len(ir.content))
      meta[name] = entry
    except Exception as exc:  # noqa: BLE001
      print("ERR", exc)
      meta[name] = {"affiliate": url, "error": str(exc)}

  (out_dir / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
  print("\nWrote", out_dir / "meta.json")


if __name__ == "__main__":
  look = sys.argv[1] if len(sys.argv) > 1 else "blue-yellow-look"
  out = ROOT / "assets" / "products" / look
  links = {
    "shirt": "https://link.amazon/B0d72SrXR",
    "jeans": "https://link.amazon/B00JGpsVj",
    "shoes": "https://link.amazon/B00jfHP4y",
    "bag": "https://link.amazon/B03vk2Ulu",
    "glasses": "https://link.amazon/B0i13rp9X",
    "necklace": "https://link.amazon/B0flGicUX",
    "earrings": "https://link.amazon/B0flGicUX",
  }
  fetch_look(out, links)
