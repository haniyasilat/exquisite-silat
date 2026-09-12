"""Build outfit collages from real product photos, each placed on a clean
rounded white card (no ML background removal - lightweight, Pillow-only).

Generic layout used for every outfit (7 pieces: 2 garments + 5 accessories,
piece order taken from links.json):

    pieces[0] -> top/main garment      (center, upper)
    pieces[1] -> bottom/second garment (center, lower)
    pieces[2] -> mid-left accessory
    pieces[3] -> bottom-right accessory
    pieces[4] -> mid-right accessory
    pieces[5] -> top-right accessory
    pieces[6] -> top-left accessory
"""

import json
import pathlib

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
ASSET_ROOT = ROOT / "assets" / "products"
LINKS_JSON = ROOT / "links.json"

W, H = 848, 1264
BEIGE = (245, 240, 232)
CHARCOAL = (42, 36, 34)
RUBY = (122, 31, 43)
MUTED = (107, 99, 92)

FONT_DIR = pathlib.Path("/usr/share/fonts/truetype/liberation")
SERIF_BOLD = FONT_DIR / "LiberationSerif-Bold.ttf"
SANS = FONT_DIR / "LiberationSans-Regular.ttf"
SANS_BOLD = FONT_DIR / "LiberationSans-Bold.ttf"

SLUG_TO_FOLDER = {
    "cozy-autumn-coffee-look-01": "cozy-autumn-coffee-look",
    "quiet-luxury-summer-look-01": "quiet-luxury-summer-look",
    "modest-pastel-spring-look-01": "modest-pastel-spring-look",
}

# "cutout": background-free, floats on the canvas (matches the original AI-art
# collages) - use only where every piece photo is on a plain white/light studio
# background. "card": photo placed on a white rounded card (safe fallback for
# on-model photos with a real background, which a cutout would not clean up).
SLUG_STYLE = {
    "cozy-autumn-coffee-look-01": "cutout",
    "quiet-luxury-summer-look-01": "card",
    "modest-pastel-spring-look-01": "card",
}

# (slot index) -> (center_x_frac, center_y_frac, max_w, max_h)
LAYOUT = {
    0: (0.50, 0.34, 380, 400),  # top garment
    1: (0.50, 0.70, 340, 460),  # bottom garment
    2: (0.16, 0.54, 220, 220),  # mid-left accessory
    3: (0.80, 0.775, 220, 160),  # bottom-right accessory
    4: (0.84, 0.54, 200, 200),  # mid-right accessory
    5: (0.80, 0.155, 200, 160),  # top-right accessory
    6: (0.20, 0.155, 200, 160),  # top-left accessory
}


def load_rgba(src: pathlib.Path) -> Image.Image:
    return Image.open(src).convert("RGBA")


def rounded_mask(size, radius):
    mask = Image.new("L", size, 0)
    d = ImageDraw.Draw(mask)
    d.rounded_rectangle((0, 0, size[0] - 1, size[1] - 1), radius=radius, fill=255)
    return mask


def cutout_white_bg(img: Image.Image, white: int = 240, colored: int = 205) -> Image.Image:
    """Turn a near-white studio background transparent (no ML model needed).

    Pixels brighter than *white* on every channel become fully transparent;
    pixels darker than *colored* stay fully opaque; the band between the two
    fades linearly so cutout edges stay soft instead of jagged.
    """
    arr = np.array(img.convert("RGBA")).astype(np.float32)
    min_channel = arr[..., :3].min(axis=2)
    fade_range = max(white - colored, 1)
    alpha = np.clip((white - min_channel) / fade_range, 0.0, 1.0) * 255.0
    alpha = np.where(min_channel >= white, 0.0, alpha)
    alpha = np.where(min_channel < colored, 255.0, alpha)
    arr[..., 3] = np.minimum(arr[..., 3], alpha)
    return Image.fromarray(arr.astype(np.uint8), "RGBA")


def trim_alpha(img: Image.Image) -> Image.Image:
    bbox = img.getbbox()
    return img.crop(bbox) if bbox else img


def cutout(img: Image.Image, max_w: int, max_h: int) -> Image.Image:
    """Fit *img* as a background-free cutout (garment floats directly on the canvas)."""
    photo = cutout_white_bg(img)
    photo = trim_alpha(photo)
    photo.thumbnail((max_w, max_h), Image.Resampling.LANCZOS)
    return photo


def card(img: Image.Image, max_w: int, max_h: int, pad: int = 14, radius: int = 18) -> Image.Image:
    """Fit *img* into a padded white rounded card (no cutout needed)."""
    photo = img.copy()
    photo.thumbnail((max_w - pad * 2, max_h - pad * 2), Image.Resampling.LANCZOS)
    card_w, card_h = photo.width + pad * 2, photo.height + pad * 2

    base = Image.new("RGBA", (card_w, card_h), (255, 255, 255, 255))
    base.paste(photo.convert("RGBA"), (pad, pad), photo.convert("RGBA"))
    mask = rounded_mask((card_w, card_h), radius)
    rounded = Image.new("RGBA", (card_w, card_h), (0, 0, 0, 0))
    rounded.paste(base, (0, 0), mask)
    return rounded


def soft_shadow(img: Image.Image, blur: int = 12, opacity: int = 70) -> Image.Image:
    pad = blur * 3
    canvas = Image.new("RGBA", (img.width + pad * 2, img.height + pad * 2), (0, 0, 0, 0))
    mask = img.split()[-1]
    sh = Image.new("RGBA", img.size, (40, 28, 30, opacity))
    canvas.paste(sh, (pad, pad + 5), mask)
    canvas = canvas.filter(ImageFilter.GaussianBlur(blur))
    canvas.alpha_composite(img, (pad, pad))
    return canvas


def paste_center(canvas: Image.Image, img: Image.Image, cx: int, cy: int) -> None:
    canvas.alpha_composite(img, (int(cx - img.width / 2), int(cy - img.height / 2)))


def rounded_pill(size, fill):
    w, h = size
    pill = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(pill)
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=h // 2, fill=fill)
    return pill


def draw_top_banner(canvas: Image.Image) -> None:
    pill_w, pill_h = int(W * 0.66), 96
    pill = rounded_pill((pill_w, pill_h), (255, 255, 255, 235))
    canvas.alpha_composite(pill, ((W - pill_w) // 2, 28))

    draw = ImageDraw.Draw(canvas)
    title_font = ImageFont.truetype(str(SERIF_BOLD), 34)
    sub_font = ImageFont.truetype(str(SANS), 15)

    title = "EXQUISITE SILAT"
    tb = draw.textbbox((0, 0), title, font=title_font)
    draw.text(((W - (tb[2] - tb[0])) / 2, 28 + 18), title, font=title_font, fill=RUBY)

    sub = "OUTFIT CURATION  ·  TAP TO SHOP"
    sb = draw.textbbox((0, 0), sub, font=sub_font)
    draw.text(((W - (sb[2] - sb[0])) / 2, 28 + 60), sub, font=sub_font, fill=MUTED)


def draw_bottom_cta(canvas: Image.Image) -> None:
    pill_w, pill_h = int(W * 0.78), 110
    pill = rounded_pill((pill_w, pill_h), (*RUBY, 255))
    x0 = (W - pill_w) // 2
    y0 = H - pill_h - 26
    canvas.alpha_composite(pill, (x0, y0))

    draw = ImageDraw.Draw(canvas)
    title_font = ImageFont.truetype(str(SANS_BOLD), 30)
    sub_font = ImageFont.truetype(str(SANS), 14)

    title = "SHOP THIS LOOK"
    tb = draw.textbbox((0, 0), title, font=title_font)
    draw.text(((W - (tb[2] - tb[0])) / 2, y0 + 18), title, font=title_font, fill=(255, 255, 255))

    sub = "Tap link to shop exact pieces on Amazon"
    sb = draw.textbbox((0, 0), sub, font=sub_font)
    draw.text(((W - (sb[2] - sb[0])) / 2, y0 + 62), sub, font=sub_font, fill=(255, 235, 236))


def build_outfit_collage(outfit: dict) -> None:
    slug = outfit["slug"]
    folder = SLUG_TO_FOLDER[slug]
    asset_dir = ASSET_ROOT / folder
    style = SLUG_STYLE.get(slug, "card")
    frame = cutout if style == "cutout" else card

    canvas = Image.new("RGBA", (W, H), (*BEIGE, 255))

    for i, piece in enumerate(outfit["pieces"][:7]):
        slot = piece["slot"].lower()
        src = asset_dir / f"{slot}.jpg"
        if not src.is_file():
            continue
        raw = load_rgba(src)
        cx_f, cy_f, max_w, max_h = LAYOUT[i]
        img = soft_shadow(frame(raw, max_w, max_h))
        paste_center(canvas, img, int(W * cx_f), int(H * cy_f))

    draw_top_banner(canvas)
    draw_bottom_cta(canvas)

    out_path = asset_dir / "collage.png"
    canvas.convert("RGB").save(out_path, "PNG", optimize=True)
    print(f"[OK] wrote {out_path}")


def main() -> None:
    data = json.loads(LINKS_JSON.read_text(encoding="utf-8"))
    targets = set(SLUG_TO_FOLDER)
    for outfit in data["outfits"]:
        if outfit["slug"] in targets:
            build_outfit_collage(outfit)


if __name__ == "__main__":
    main()
