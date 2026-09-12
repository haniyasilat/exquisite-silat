"""
Utility script to:
1. For the three new looks, resolve each piece's Amazon product URL (falling back to a
   search-URL lookup in `ae_links.json` if a piece has no direct /dp/ URL yet).
2. Fetch each product page and extract its main image (og:image, or the #landingImage
   <img> tag's src as a fallback) and download it under
   assets/products/<look-folder>/<slot>.jpg.
3. Assemble a 1000x1500 px Pinterest-size collage (3x2 grid) from those images.
4. Apply a "Shop the Look" CTA overlay (top banner + bottom button).
5. Save the collage as `collage_new.png` next to the existing `collage.png` (does not
   overwrite it) and update `links.json` with any newly-resolved direct URLs.
"""

import json
import pathlib
import re
import time
from typing import List, Optional

import requests
from PIL import Image, ImageDraw, ImageFont

# ---------- Configuration ----------
ROOT = pathlib.Path(__file__).resolve().parent.parent
ASSET_ROOT = ROOT / "assets" / "products"
LINKS_JSON = ROOT / "links.json"
AE_LINKS_JSON = ROOT / "ae_links.json"  # optional: slot name -> Amazon search URL

# Pinterest pin size (2:3 ratio)
PIN_WIDTH = 1000
PIN_HEIGHT = 1500

TARGET_SLUGS = {
    "cozy-autumn-coffee-look-01",
    "quiet-luxury-summer-look-01",
    "modest-pastel-spring-look-01",
}

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
ASIN_PATTERN = re.compile(r"/dp/([A-Z0-9]{10})")


# ---------- Helper functions ----------
def fetch_page(url: str) -> Optional[str]:
    """Return the HTML text of *url* or None on failure."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        if resp.status_code == 200:
            return resp.text
    except Exception as e:
        print(f"[WARN] Request failed for {url}: {e}")
    return None


def extract_asin_from_search(html: str) -> Optional[str]:
    """Amazon search pages usually contain the first product link `/dp/ASIN`."""
    m = ASIN_PATTERN.search(html)
    return m.group(1) if m else None


def extract_og_image(html: str) -> Optional[str]:
    """Parse the `<meta property="og:image" ...>` tag and return its URL."""
    match = re.search(r'<meta\s+property="og:image"\s+content="([^"]+)"', html)
    return match.group(1) if match else None


def extract_landing_image(html: str) -> Optional[str]:
    """Find the #landingImage <img> tag (regardless of attribute order) and return its src."""
    tag_match = re.search(r'<img[^>]+id=["\']landingImage["\'][^>]*>', html)
    if not tag_match:
        return None
    src_match = re.search(r'src=["\']([^"\']+)["\']', tag_match.group(0))
    return src_match.group(1) if src_match else None


def extract_product_image(html: str) -> Optional[str]:
    return extract_og_image(html) or extract_landing_image(html)


def download_image(url: str, dest: pathlib.Path) -> bool:
    """Download *url* to *dest* (creates parent directories)."""
    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        if r.status_code == 200:
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(r.content)
            return True
    except Exception as e:
        print(f"[WARN] Image download failed {url}: {e}")
    return False


def create_pinterest_collage(images: List[Image.Image], output_path: pathlib.Path) -> None:
    """Create a 3x2 grid collage of *images* sized to PIN_WIDTH x PIN_HEIGHT."""
    cols, rows = 3, 2
    thumb_w = PIN_WIDTH // cols
    thumb_h = PIN_HEIGHT // rows
    collage = Image.new("RGB", (PIN_WIDTH, PIN_HEIGHT), color=(255, 255, 255))
    for i, img in enumerate(images[: cols * rows]):
        r, c = divmod(i, cols)
        thumb = img.copy()
        thumb.thumbnail((thumb_w, thumb_h), Image.LANCZOS)
        x = c * thumb_w + (thumb_w - thumb.width) // 2
        y = r * thumb_h + (thumb_h - thumb.height) // 2
        collage.paste(thumb, (x, y))
    collage.save(output_path)


def add_cta_overlay(image_path: pathlib.Path) -> None:
    """Add a top banner and bottom button saying "Shop the Look"."""
    img = Image.open(image_path).convert("RGB")
    draw = ImageDraw.Draw(img)

    banner_h = int(img.height * 0.08)
    draw.rectangle([0, 0, img.width, banner_h], fill=(0, 0, 0))
    try:
        font = ImageFont.truetype("arial.ttf", size=int(banner_h * 0.45))
    except Exception:
        font = ImageFont.load_default()
    draw.text((10, banner_h // 4), "Shop the Look", fill=(255, 255, 255), font=font)

    btn_h = int(img.height * 0.10)
    btn_y = img.height - btn_h
    draw.rectangle([0, btn_y, img.width, img.height], fill=(255, 255, 255))
    try:
        btn_font = ImageFont.truetype("arial.ttf", size=int(btn_h * 0.4))
    except Exception:
        btn_font = ImageFont.load_default()
    btn_text = "Shop this look"
    left, top, right, bottom = draw.textbbox((0, 0), btn_text, font=btn_font)
    text_w, text_h = right - left, bottom - top
    draw.text(
        ((img.width - text_w) // 2, btn_y + (btn_h - text_h) // 2),
        btn_text,
        fill=(0, 0, 0),
        font=btn_font,
    )
    img.save(image_path)


def resolve_piece_url(piece: dict, search_map: dict) -> Optional[str]:
    """Return a usable Amazon product-page URL for *piece*, resolving via search if needed."""
    existing_url = (piece.get("amazon_url") or "").strip()
    if existing_url and "/dp/" in existing_url:
        return existing_url

    search_url = search_map.get(piece.get("slot", ""))
    if not search_url:
        return existing_url or None

    html = fetch_page(search_url)
    if not html:
        return existing_url or None
    asin = extract_asin_from_search(html)
    if not asin:
        print(f"[WARN] No ASIN found for {piece.get('slot')} via {search_url}")
        return existing_url or None

    direct_url = f"https://www.amazon.ae/dp/{asin}?tag=exquisitesila-21"
    piece["amazon_url"] = direct_url
    return direct_url


def asset_dir_for(outfit: dict) -> pathlib.Path:
    return ASSET_ROOT / pathlib.Path(outfit["collage_image"]).parent.name


# ---------- Main workflow ----------
def main() -> None:
    search_map = {}
    if AE_LINKS_JSON.is_file():
        with open(AE_LINKS_JSON, "r", encoding="utf-8") as f:
            search_map = json.load(f)

    with open(LINKS_JSON, "r", encoding="utf-8") as f:
        links_data = json.load(f)

    target_outfits = [o for o in links_data.get("outfits", []) if o.get("slug") in TARGET_SLUGS]

    for outfit in target_outfits:
        asset_dir = asset_dir_for(outfit)
        for piece in outfit.get("pieces", []):
            slot = piece.get("slot", "piece")
            product_url = resolve_piece_url(piece, search_map)
            if not product_url:
                print(f"[WARN] No Amazon URL for {slot}")
                continue

            prod_html = fetch_page(product_url)
            if not prod_html:
                continue

            img_url = extract_product_image(prod_html)
            if not img_url:
                print(f"[WARN] No product image found for {slot} at {product_url}")
                continue

            img_path = asset_dir / f"{slot.lower()}.jpg"
            if download_image(img_url, img_path):
                print(f"[OK] Downloaded image for {slot} -> {img_path}")
            else:
                print(f"[WARN] Failed to download image for {slot}")

            time.sleep(0.5)  # be gentle to Amazon

    with open(LINKS_JSON, "w", encoding="utf-8") as f:
        json.dump(links_data, f, indent=2, ensure_ascii=False)
    print("[INFO] links.json updated with any newly-resolved direct URLs.")

    # ---------- Collage generation ----------
    for outfit in target_outfits:
        asset_dir = asset_dir_for(outfit)
        img_paths = [
            p
            for p in (asset_dir / f"{piece.get('slot', 'piece').lower()}.jpg" for piece in outfit.get("pieces", []))
            if p.is_file()
        ]
        if len(img_paths) < 2:
            print(f"[WARN] Not enough images for {outfit['slug']}, skipping collage.")
            continue
        pil_images = [Image.open(p).convert("RGB") for p in img_paths[:6]]
        collage_path = asset_dir / "collage_new.png"
        create_pinterest_collage(pil_images, collage_path)
        add_cta_overlay(collage_path)
        print(f"[OK] Created collage with CTA for {outfit['slug']} -> {collage_path}")

    print("[INFO] Finished - new collages are stored as `collage_new.png` under each look's folder.")


if __name__ == "__main__":
    main()
