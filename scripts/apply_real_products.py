"""Download the main Amazon product photo for every piece of the flat-lay looks.

    python scripts/apply_real_products.py                  # all looks, skip photos already on disk
    python scripts/apply_real_products.py <outfit-id> ...  # just those looks
    python scripts/apply_real_products.py --force ...      # re-download even if present

Reads links.json: every piece with an "image_url" (the listing's main image, i.e. the one
shoppers see first, so the collage matches the product page) is saved as
assets/products/<folder>/<slot>.jpg, which cut_garments.py and build_real_collages.py read,
plus a small thumbnail in <folder>/thumbs/<slot>.jpg for the look page's shop list.
The look's folder is the folder of its collage_image.
"""

import io
import json
import pathlib
import sys
import urllib.request

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
LINKS_JSON = ROOT / "links.json"

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
THUMB = 240


def download(url: str) -> bytes:
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def write_thumb(src: pathlib.Path, dest: pathlib.Path) -> None:
    im = Image.open(src).convert("RGB")
    im.thumbnail((THUMB, THUMB), Image.LANCZOS)
    dest.parent.mkdir(parents=True, exist_ok=True)
    im.save(dest, "JPEG", quality=82, optimize=True)


def main() -> None:
    args = sys.argv[1:]
    force = "--force" in args
    only = {a for a in args if not a.startswith("--")}

    data = json.loads(LINKS_JSON.read_text(encoding="utf-8"))
    for outfit in data["outfits"]:
        if only and outfit["id"] not in only:
            continue
        folder = ROOT / pathlib.Path(outfit["collage_image"].split("?")[0]).parent
        for piece in outfit["pieces"]:
            url = piece.get("image_url")
            if not url:
                continue
            name = f"{piece['slot'].lower()}.jpg"
            dest = folder / name
            if force or not dest.is_file():
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(download(url))
                Image.open(io.BytesIO(dest.read_bytes())).verify()
                print(f"[OK] {dest.relative_to(ROOT)} <- {piece.get('asin', url)}")
            thumb = folder / "thumbs" / name
            if force or not thumb.is_file():
                write_thumb(dest, thumb)


if __name__ == "__main__":
    main()
