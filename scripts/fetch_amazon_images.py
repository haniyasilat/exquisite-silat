"""Download Amazon product images from affiliate short links."""

from __future__ import annotations

import json
import re
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "products" / "burgundy-look"

HEADERS = {
  "User-Agent": (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
  ),
  "Accept-Language": "en-US,en;q=0.9",
}

LINKS = {
  "shirt": "https://link.amazon/B0a2Skmk2",
  "jeans": "https://link.amazon/B0hdpJOr3",
  "watch": "https://link.amazon/B0cYvoLpG",
  "bag": "https://link.amazon/B0awbhkV9",
  "shoes": "https://link.amazon/B0drwncy3",
  "earrings": "https://link.amazon/B0104bp0b",
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


def main() -> None:
  OUT.mkdir(parents=True, exist_ok=True)
  meta: dict = {}

  for name, url in LINKS.items():
    print(f"\n=== {name} ===")
    try:
      r = requests.get(url, headers=HEADERS, timeout=45, allow_redirects=True)
      html = r.text
      img = extract_image(html)
      title_m = re.search(r"<title>([^<]+)</title>", html)
      title = title_m.group(1).strip() if title_m else name
      print("status", r.status_code)
      print("final", r.url[:120])
      print("img", img[:120] if img else None)
      entry = {
        "affiliate": url,
        "final_url": r.url,
        "title": title,
        "image_url": img,
      }
      if img:
        ir = requests.get(img, headers=HEADERS, timeout=45)
        ext = ".png" if ".png" in img.lower() else ".jpg"
        path = OUT / f"{name}{ext}"
        path.write_bytes(ir.content)
        entry["local"] = str(path.relative_to(ROOT)).replace("\\", "/")
        print("saved", path, len(ir.content))
      meta[name] = entry
    except Exception as exc:  # noqa: BLE001
      print("ERR", exc)
      meta[name] = {"affiliate": url, "error": str(exc)}

  (OUT / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
  print("\nWrote", OUT / "meta.json")


if __name__ == "__main__":
  main()
