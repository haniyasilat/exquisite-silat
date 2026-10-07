"""Amazon.ae research helpers for putting a new look together.

    python scripts/amazon_research.py search <name> "<query>"   # numbered contact sheet of results
    python scripts/amazon_research.py gallery <ASIN> [...]       # every gallery photo of a listing
    python scripts/amazon_research.py verify <ASIN> [...]        # live check + main photo + sheet

Output goes to content/generated/research/ (gitignored):
    search_<name>.jpg/.json   results 0-23 with ASIN, price, title
    gallery_<ASIN>.jpg        the listing's photos (look for a person-free main photo)
    verify.json               title, price, colour, availability, Add to Cart, main image URL
    verify_<first ASIN>.jpg   contact sheet of the verified main photos

Open the .jpg sheets to judge photos by eye: a usable product's MAIN photo (index 0 in
the gallery, the one verify downloads) must show the item alone, no person.
"""

import html
import io
import json
import pathlib
import re
import sys
import time
import urllib.parse
import urllib.request

from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "content" / "generated" / "research"
UA = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/128.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}


def font(size: int, bold: bool = False):
    for name in (("arialbd.ttf" if bold else "arial.ttf"), "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def get(url: str) -> bytes:
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
        return r.read()


def text(fragment: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", fragment))).strip()


def thumb(url: str, size: int) -> Image.Image:
    try:
        im = Image.open(io.BytesIO(get(url))).convert("RGB")
    except Exception:
        im = Image.new("RGB", (size, size), (200, 0, 0))
    im.thumbnail((size, size))
    return im


def sheet(images, labels, out: pathlib.Path, size=220, cols=6) -> None:
    rows = max(1, (len(images) + cols - 1) // cols)
    s = Image.new("RGB", (cols * size, rows * (size + 20)), (128, 128, 128))
    d = ImageDraw.Draw(s)
    f = font(16, bold=True)
    for i, (im, lab) in enumerate(zip(images, labels)):
        x, y = (i % cols) * size, (i // cols) * (size + 20)
        s.paste(im, (x + (size - im.width) // 2, y + (size - im.height) // 2))
        d.rectangle((x, y + size, x + size, y + size + 20), fill=(0, 0, 0))
        d.text((x + 4, y + size + 1), lab, fill=(255, 255, 0), font=f)
    out.parent.mkdir(parents=True, exist_ok=True)
    s.save(out, quality=85)
    print(f"sheet: {out.relative_to(ROOT)}")


def cmd_search(name: str, query: str) -> None:
    page = get("https://www.amazon.ae/s?k=" + urllib.parse.quote_plus(query)).decode("utf-8", "replace")
    items, seen = [], set()
    for block in re.split(r'(?=<div[^>]+data-asin="[A-Z0-9]{10}")', page):
        m = re.match(r'<div[^>]+data-asin="([A-Z0-9]{10})"', block)
        if not m or m.group(1) in seen or 'data-component-type="s-search-result"' not in block[:8000]:
            continue
        img = re.search(r'class="s-image"[^>]*src="([^"]+)"', block)
        title = re.search(r'<h2[^>]*aria-label="([^"]+)"', block) or re.search(r"<h2.*?<span[^>]*>(.*?)</span>", block, re.S)
        price = re.search(r'class="a-price-whole">([\d,]+)', block)
        if not img:
            continue
        seen.add(m.group(1))
        items.append({
            "asin": m.group(1),
            "img": img.group(1),
            "title": text(title.group(1)) if title else "",
            "price": price.group(1) if price else None,
            "sponsored": "Sponsored" in block[:6000],
        })
    items = items[:24]
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"search_{name}.json").write_text(json.dumps(items, indent=2, ensure_ascii=False), encoding="utf-8")
    for i, it in enumerate(items):
        print(i, it["asin"], it["price"], "SP" if it["sponsored"] else "", it["title"][:90])
    sheet([thumb(it["img"], 220) for it in items], [f"{i} {it['asin']}" for i, it in enumerate(items)],
          OUT / f"search_{name}.jpg")


def product(asin: str) -> dict:
    page = get(f"https://www.amazon.ae/dp/{asin}").decode("utf-8", "replace")
    title = re.search(r'id="productTitle"[^>]*>\s*(.*?)\s*</span>', page, re.S)
    av = re.search(r'<div id="availability".*?</div>', page, re.S)
    price = re.search(r'class="a-price-whole">([\d,]+)', page)
    colour = (re.search(r'id="inline-twister-expanded-dimension-text-color_name"[^>]*>\s*(.*?)\s*<', page, re.S)
              or re.search(r'id="variation_color_name".*?class="selection">\s*(.*?)\s*<', page, re.S))
    main = (re.search(r'id="landingImage"[^>]*data-old-hires="(https://[^"]+)"', page)
            or re.search(r'data-old-hires="(https://[^"]+)"[^>]*id="landingImage"', page)
            or re.search(r'"hiRes":"(https://[^"]+)"', page)
            or re.search(r'id="landingImage"[^>]*src="(https://[^"]+)"', page))
    init = re.search(r"""['"]colorImages['"]\s*:\s*\{\s*['"]initial['"]\s*:\s*(\[.*?\])\s*\}""", page, re.S)
    scope = init.group(1) if init else page
    gallery = list(dict.fromkeys(re.findall(r'"hiRes":"(https://[^"]+)"', scope) or
                                 re.findall(r'"large":"(https://[^"]+)"', scope)))
    return {
        "asin": asin,
        "title": text(title.group(1)) if title else None,
        "price": price.group(1) if price else None,
        "colour": text(colour.group(1)) if colour else None,
        "availability": (text(av.group(0))[:80].split("{")[0].strip() if av else None),
        "cart": 'id="add-to-cart-button"' in page,
        "main_image": main.group(1) if main else None,
        "gallery": gallery,
        "url": f"https://www.amazon.ae/dp/{asin}?tag=exquisitesila-21",
    }


def cmd_gallery(asins) -> None:
    for asin in asins:
        p = product(asin)
        print(asin, "|", p["price"], "|", p["colour"], "|", p["availability"], "| cart" if p["cart"] else "| NO CART",
              "|", (p["title"] or "NO TITLE")[:90])
        urls = p["gallery"][:12]
        sheet([thumb(re.sub(r"\.jpg$", "._AC_SX300_.jpg", u), 200) for u in urls],
              [str(i) for i in range(len(urls))], OUT / f"gallery_{asin}.jpg", size=200)
        time.sleep(1)


def cmd_verify(asins) -> None:
    db_path = OUT / "verify.json"
    db = json.loads(db_path.read_text(encoding="utf-8")) if db_path.exists() else {}
    images = []
    for asin in asins:
        p = product(asin)
        p.pop("gallery")
        db[asin] = p
        print(asin, "|", p["price"], "|", p["colour"], "|", p["availability"], "| cart" if p["cart"] else "| NO CART",
              "|", (p["title"] or "NO TITLE")[:80])
        print("   main:", p["main_image"])
        images.append(thumb(p["main_image"], 220) if p["main_image"] else Image.new("RGB", (220, 220), (200, 0, 0)))
        time.sleep(1)
    OUT.mkdir(parents=True, exist_ok=True)
    db_path.write_text(json.dumps(db, indent=2, ensure_ascii=False), encoding="utf-8")
    sheet(images, list(asins), OUT / f"verify_{asins[0]}.jpg", cols=5)


def main() -> None:
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(2)
    cmd, args = sys.argv[1], sys.argv[2:]
    if cmd == "search" and len(args) == 2:
        cmd_search(*args)
    elif cmd == "gallery":
        cmd_gallery(args)
    elif cmd == "verify":
        cmd_verify(args)
    else:
        print(__doc__)
        sys.exit(2)


if __name__ == "__main__":
    main()
