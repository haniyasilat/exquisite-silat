"""Render extra Pinterest pins from existing looks and write a bulk-upload CSV.

    python scripts/make_pin_variants.py

Reads pinterest/plan.json (see its "_about") and links.json, renders every pin to
assets/pins/<id>.jpg (848x1264, roughly Pinterest's 2:3) and writes
pinterest/bulk-upload.csv in Pinterest's bulk-create format, one pin per day from the
plan's start date. Commit + push so the images are live on the site before uploading the
CSV in Pinterest (Create -> Create Pins in bulk -> Upload .csv).

Pin types:
    headline  the look's collage between a keyword headline band and a tap-to-shop band
    piece     one product, large, on the look's backdrop (needs the look's "collage" config)
    formula   four pieces in a 2x2 grid joined by plus signs (same)
"""

import csv
import json
import pathlib
import sys
from datetime import date, timedelta

from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import build_real_collages as brc  # noqa: E402
import build_site  # noqa: E402

ROOT = brc.ROOT
PLAN = ROOT / "pinterest" / "plan.json"
OUT_DIR = ROOT / "assets" / "pins"
CSV_PATH = ROOT / "pinterest" / "bulk-upload.csv"
W, H = brc.W, brc.H
TOP, BOT = 190, 118  # headline band / call-to-action band heights
CREAM = brc.CREAM


def fit(draw, text, font_path, size, max_w):
    """Largest font (<= size) at which text fits max_w."""
    while size > 14:
        f = ImageFont.truetype(str(font_path), size)
        if draw.textlength(text, font=f) <= max_w:
            return f
        size -= 2
    return ImageFont.truetype(str(font_path), size)


def centred(draw, y, text, font, fill):
    draw.text(((W - draw.textlength(text, font=font)) / 2, y), text, font=font, fill=fill)


def bands(canvas: Image.Image, ink, headline: str, subline: str, cta: str) -> None:
    """Headline band on top, tap-to-shop band at the bottom, both in the look's ink colour."""
    d = ImageDraw.Draw(canvas)
    ink = tuple(ink)
    d.rectangle((0, 0, W, TOP), fill=ink)
    d.rectangle((0, H - BOT, W, H), fill=ink)
    d.line((0, TOP, W, TOP), fill=CREAM, width=2)
    d.line((0, H - BOT, W, H - BOT), fill=CREAM, width=2)
    centred(d, 34, headline, fit(d, headline, brc.SERIF_BOLD, 60, W - 70), CREAM)
    centred(d, 124, subline, fit(d, subline, brc.SANS, 26, W - 90), CREAM)
    brc.spaced_text(d, H - BOT + 22, cta, ImageFont.truetype(str(brc.SERIF_BOLD), 34), CREAM, 3)
    centred(d, H - BOT + 74, "every piece linked  ·  exquisite.silat.ae",
            ImageFont.truetype(str(brc.SANS), 19), CREAM)


def render_headline(outfit, ink, pin) -> Image.Image:
    collage = Image.open(ROOT / outfit["collage_image"].split("?")[0]).convert("RGB")
    if pin.get("crop_top"):  # trim a heading baked into an older collage
        collage = collage.crop((0, int(collage.height * pin["crop_top"]), collage.width, collage.height))
    area_w, area_h = W, H - TOP - BOT
    # backdrop: the same collage enlarged to fill the area, blurred and softened, so the
    # strips beside the (contained) collage blend in instead of showing flat bars
    cover = max(area_w / collage.width, area_h / collage.height)
    bg = collage.resize((int(collage.width * cover) + 1, int(collage.height * cover) + 1), Image.LANCZOS)
    bg = bg.crop(((bg.width - area_w) // 2, (bg.height - area_h) // 2,
                  (bg.width - area_w) // 2 + area_w, (bg.height - area_h) // 2 + area_h))
    bg = Image.blend(bg.filter(ImageFilter.GaussianBlur(28)), Image.new("RGB", bg.size, (250, 246, 240)), 0.35)
    canvas = Image.new("RGB", (W, H))
    canvas.paste(bg, (0, TOP))
    scale = min(area_w / collage.width, area_h / collage.height)
    c = collage.resize((int(collage.width * scale), int(collage.height * scale)), Image.LANCZOS)
    canvas.paste(c, ((W - c.width) // 2, TOP + (area_h - c.height) // 2))
    bands(canvas, ink, pin["headline"], pin["subline"], "TAP TO SHOP THE LOOK")
    return canvas


def look_background(outfit) -> Image.Image:
    return brc.BACKGROUNDS[outfit["collage"]["background"]]()


def piece(outfit, slot):
    cut = outfit["collage"].get("cutout", {})
    return brc.piece_image(brc.asset_dir_for(outfit), slot, tuple(cut.get(slot, ())))


def render_piece(outfit, ink, pin) -> Image.Image:
    canvas = look_background(outfit)
    y0, y1 = (TOP + 40) / H, (H - BOT - 40) / H
    brc.place(canvas, piece(outfit, pin["slots"][0]), (0.14, y0, 0.86, y1))
    canvas = canvas.convert("RGB")
    bands(canvas, ink, pin["headline"], pin["subline"], "SHOP IT + THE FULL LOOK")
    return canvas


def render_formula(outfit, ink, pin) -> Image.Image:
    canvas = look_background(outfit)
    top, bot = (TOP + 30) / H, (H - BOT - 30) / H
    mid_y = (top + bot) / 2
    cells = [(0.13, top, 0.47, mid_y - 0.015), (0.53, top, 0.87, mid_y - 0.015),
             (0.13, mid_y + 0.015, 0.47, bot), (0.53, mid_y + 0.015, 0.87, bot)]
    for slot, box in zip(pin["slots"], cells):
        brc.place(canvas, piece(outfit, slot), box)
    d = ImageDraw.Draw(canvas)
    plus = ImageFont.truetype(str(brc.SERIF_BOLD), 64)
    for cx, cy in ((0.5, (top + mid_y) / 2), (0.5, (mid_y + bot) / 2), (0.5, mid_y)):
        x, y = W * cx, H * cy
        d.ellipse((x - 26, y - 26, x + 26, y + 26), fill=(*CREAM, 235))
        d.text((x - d.textlength("+", font=plus) / 2, y - 40), "+", font=plus, fill=tuple(ink))
    canvas = canvas.convert("RGB")
    bands(canvas, ink, pin["headline"], pin["subline"], "TAP TO SHOP THE LOOK")
    return canvas


RENDER = {"headline": render_headline, "piece": render_piece, "formula": render_formula}


def main() -> None:
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    looks = {o["id"]: o for o in json.loads(brc.LINKS_JSON.read_text(encoding="utf-8"))["outfits"]}
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    start = date.fromisoformat(plan["start"])
    rows = []
    for n, pin in enumerate(plan["pins"]):
        outfit = looks[pin["look"]]
        ink = (outfit.get("collage") or {}).get("ink") or plan["inks"][pin["look"]]
        img = RENDER[pin["type"]](outfit, ink, pin)
        out = OUT_DIR / f"{pin['id']}.jpg"
        img.save(out, "JPEG", quality=88, optimize=True, progressive=True)

        slug = outfit.get("url_slug") or build_site.slugify(outfit["title"])
        link = (f"{build_site.SITE_URL}/looks/{slug}/?utm_source=pinterest&utm_medium=social"
                f"&utm_campaign={plan['utm_campaign']}&utm_content={pin['id']}")
        day = pin.get("date") or (start + timedelta(days=n)).isoformat()
        assert len(pin["title"]) <= 100, (pin["id"], len(pin["title"]))
        assert len(pin["description"]) <= 500, (pin["id"], len(pin["description"]))
        rows.append({
            "Title": pin["title"],
            "Media URL": f"{build_site.SITE_URL}/assets/pins/{pin['id']}.jpg",
            "Pinterest board": pin["board"],
            "Thumbnail": "",
            "Description": pin["description"],
            "Link": link,
            "Publish date": f"{day}T{plan['time_utc']}",
            "Keywords": pin.get("keywords", ""),
        })
        print(f"[OK] {day} {pin['id']:22} {pin['type']:8} -> {out.relative_to(ROOT)}")

    with CSV_PATH.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"\n{len(rows)} pins -> {CSV_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
