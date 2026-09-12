"""Apply verified real Amazon product picks to links.json and download images."""

import json
import pathlib
import re
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
LINKS_JSON = ROOT / "links.json"
ASSET_ROOT = ROOT / "assets" / "products"

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

# (outfit slug, piece slot, asin, image_url)
PICKS = [
    ("cozy-autumn-coffee-look-01", "Sweater", "B0FQBMQBW8", "https://m.media-amazon.com/images/I/81voSrWrOHL._AC_SY445_.jpg"),
    ("cozy-autumn-coffee-look-01", "Trousers", "B0FQJPB4FP", "https://m.media-amazon.com/images/I/61UpAQ-QTcL._AC_SY445_.jpg"),
    ("cozy-autumn-coffee-look-01", "Bag", "B0FZ7K9G9Y", "https://m.media-amazon.com/images/I/61KeYdGiZBL._AC_SX385_.jpg"),
    ("cozy-autumn-coffee-look-01", "Shoes", "B08Z7KMD2F", "https://m.media-amazon.com/images/I/71bkxmdcZSL._AC_SY500_.jpg"),
    ("cozy-autumn-coffee-look-01", "Watch", "B008UVVL9K", "https://m.media-amazon.com/images/I/61VqwetbFcL._AC_SX522_.jpg"),
    ("cozy-autumn-coffee-look-01", "Earrings", "B0GSZKM9KX", "https://m.media-amazon.com/images/I/41+pwQW9QKL._AC_SX522_.jpg"),
    ("cozy-autumn-coffee-look-01", "Sunglasses", "B0FZ9M3RN5", "https://m.media-amazon.com/images/I/61xwPQpHIwL._AC_SX385_.jpg"),

    ("quiet-luxury-summer-look-01", "Vest", "B0F5J1Z8DN", "https://m.media-amazon.com/images/I/71+yadXYjnL._AC_SY445_.jpg"),
    ("quiet-luxury-summer-look-01", "Skirt", "B0CR7G84BS", "https://m.media-amazon.com/images/I/61WjBbd189L._AC_SY445_.jpg"),
    ("quiet-luxury-summer-look-01", "Heels", "B0CQYK21GJ", "https://m.media-amazon.com/images/I/61+6-J8W-gL._AC_SY500_.jpg"),
    ("quiet-luxury-summer-look-01", "Clutch", "B0G5JW7M3R", "https://m.media-amazon.com/images/I/81rqWNm26kL._AC_SX679_.jpg"),
    ("quiet-luxury-summer-look-01", "Earrings", "B0H36NZ8KF", "https://m.media-amazon.com/images/I/511Lbc21ZEL._AC_SX425_.jpg"),
    ("quiet-luxury-summer-look-01", "Cuff", "B0FPWR65HQ", "https://m.media-amazon.com/images/I/61jtwFMmXkL._AC_SX385_.jpg"),
    ("quiet-luxury-summer-look-01", "Necklace", "B0G4QYGZWK", "https://m.media-amazon.com/images/I/51WHxSPUsCL._AC_SX385_.jpg"),

    ("modest-pastel-spring-look-01", "Blouse", "B0FD3VRM2W", "https://m.media-amazon.com/images/I/71H22sFxJHL._AC_SY445_.jpg"),
    ("modest-pastel-spring-look-01", "Skirt", "B0C99DQ9S5", "https://m.media-amazon.com/images/I/71qZHrMcZ8L._AC_SX385_.jpg"),
    ("modest-pastel-spring-look-01", "Shoes", "B0GJK15XDF", "https://m.media-amazon.com/images/I/61PAaZRvAAL._AC_SY500_.jpg"),
    ("modest-pastel-spring-look-01", "Handbag", "B0FDG5HNYL", "https://m.media-amazon.com/images/I/81AnLQExYyL._AC_SX385_.jpg"),
    ("modest-pastel-spring-look-01", "Earrings", "B0FDKNHR84", "https://m.media-amazon.com/images/I/61kepMzRh2L._AC_SX385_.jpg"),
    ("modest-pastel-spring-look-01", "Bangles", "B0G81TSR63", "https://m.media-amazon.com/images/I/815IhEk5OTL._AC_SX425_.jpg"),
    ("modest-pastel-spring-look-01", "Scarf", "B0GC5DYJ3V", "https://m.media-amazon.com/images/I/51tFInXYKUL._AC_SX385_.jpg"),
]

FOLDER_BY_SLUG = {
    "cozy-autumn-coffee-look-01": "cozy-autumn-coffee-look",
    "quiet-luxury-summer-look-01": "quiet-luxury-summer-look",
    "modest-pastel-spring-look-01": "modest-pastel-spring-look",
}


def hires(url: str) -> str:
    """Strip the Amazon size-modifier suffix (e.g. ._AC_SY445_) for a larger image."""
    return re.sub(r"\._[A-Z0-9_,]+_\.", ".", url)


def download(url: str, dest: pathlib.Path) -> None:
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as r:
        dest.write_bytes(r.read())


def main() -> None:
    data = json.loads(LINKS_JSON.read_text(encoding="utf-8"))
    by_slug = {o["slug"]: o for o in data["outfits"]}

    for slug, slot, asin, img_url in PICKS:
        outfit = by_slug[slug]
        piece = next(p for p in outfit["pieces"] if p["slot"] == slot)
        piece["amazon_url"] = f"https://www.amazon.ae/dp/{asin}?tag=exquisitesila-21"

        folder = FOLDER_BY_SLUG[slug]
        dest = ASSET_ROOT / folder / f"{slot.lower()}.jpg"
        dest.parent.mkdir(parents=True, exist_ok=True)
        try:
            download(hires(img_url), dest)
            print(f"[OK] {slug} {slot} -> {dest} ({dest.stat().st_size} bytes)")
        except Exception as e:
            print(f"[WARN] {slug} {slot} hi-res failed ({e}), trying original URL")
            download(img_url, dest)
            print(f"[OK-fallback] {slug} {slot} -> {dest} ({dest.stat().st_size} bytes)")

    LINKS_JSON.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print("[INFO] links.json updated.")


if __name__ == "__main__":
    main()
