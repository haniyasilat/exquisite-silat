"""Download the main Amazon product photo for every piece of the flat-lay looks.

Each piece's photo is saved as assets/products/<folder>/<slot>.jpg, which is what
cut_garments.py and build_real_collages.py read. The image URL is the listing's
main image (the one shoppers see first), so the collage matches the product page.
links.json holds the product URLs; this only fetches the pictures.
"""

import pathlib
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
ASSET_ROOT = ROOT / "assets" / "products"

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

# folder -> [(slot, asin, main image url)]
PICKS = {
    "forest-knit-denim-look": [
        ("Sweater", "B0HC2L47KW", "https://m.media-amazon.com/images/I/71iXKjSoTIL._AC_SL1500_.jpg"),
        ("Jeans", "B0F4N668QT", "https://m.media-amazon.com/images/I/61Uqzn-1OML._AC_SL1500_.jpg"),
        ("Loafers", "B0CRDQ853T", "https://m.media-amazon.com/images/I/716uWlCsR5L._AC_SL1500_.jpg"),
        ("Bag", "B0GGH8F9BX", "https://m.media-amazon.com/images/I/61qkbE+2UtL._AC_SL1500_.jpg"),
        ("Earrings", "B09QPPLRHP", "https://m.media-amazon.com/images/I/61oXJg5YpAL._AC_SL1500_.jpg"),
        ("Clip", "B088FFHGTP", "https://m.media-amazon.com/images/I/7138eN-kWEL._AC_SL1500_.jpg"),
        ("Belt", "B0F4C6DB3Y", "https://m.media-amazon.com/images/I/61B7GpqIxfL._AC_SL1500_.jpg"),
    ],
    "chocolate-bow-satin-look": [
        ("Cardigan", "B0DNMVH6HF", "https://m.media-amazon.com/images/I/7121QUVGlcL._AC_SL1500_.jpg"),
        ("Skirt", "B0CQRN8YLF", "https://m.media-amazon.com/images/I/51z40nSjNKL._AC_SL1500_.jpg"),
        ("Flats", "B0GX7T8MXZ", "https://m.media-amazon.com/images/I/81i5xRVNknL._AC_SL1500_.jpg"),
        ("Bag", "B0D2WDZ6K5", "https://m.media-amazon.com/images/I/51IQps4xLLL._AC_SL1500_.jpg"),
        ("Earrings", "B0DGSGSXYX", "https://m.media-amazon.com/images/I/51eQXXrmezL._AC_SL1500_.jpg"),
        ("Bows", "B0H4GRS2CB", "https://m.media-amazon.com/images/I/71GTTYjASRL._AC_SL1500_.jpg"),
        ("Perfume", "B0DSLDVF85", "https://m.media-amazon.com/images/I/61-5GcYgwoL._AC_SL1500_.jpg"),
    ],
    "leopard-black-look": [
        ("Top", "B0GF1RGDGX", "https://m.media-amazon.com/images/I/61EKGhvPiUL._AC_SL1500_.jpg"),
        ("Skirt", "B0FRSPR49T", "https://m.media-amazon.com/images/I/71uHAdbKGlL._AC_SL1500_.jpg"),
        ("Heels", "B09L4SV6T1", "https://m.media-amazon.com/images/I/51f2elFTWjL._AC_SL1500_.jpg"),
        ("Bag", "B0BNZ9MNKG", "https://m.media-amazon.com/images/I/61JyY8q93hL._AC_SL1000_.jpg"),
        ("Sunglasses", "B0GHDKFP69", "https://m.media-amazon.com/images/I/41fdnDZ3TfL._AC_SL1248_.jpg"),
        ("Earrings", "B0CGV9ZNLX", "https://m.media-amazon.com/images/I/61RY1Zv+TjL._AC_SL1500_.jpg"),
        ("Watch", "B0DBHG7DBP", "https://m.media-amazon.com/images/I/61EU0vMqbFL._AC_SL1500_.jpg"),
    ],
}


def download(url: str, dest: pathlib.Path) -> None:
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as r:
        dest.write_bytes(r.read())


def main() -> None:
    for folder, pieces in PICKS.items():
        for slot, asin, url in pieces:
            dest = ASSET_ROOT / folder / f"{slot.lower()}.jpg"
            dest.parent.mkdir(parents=True, exist_ok=True)
            download(url, dest)
            print(f"[OK] {folder}/{dest.name} <- {asin} ({dest.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
