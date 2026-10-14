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
    still     product-only still life: pin["boxes"] {slot: [x0,y0,x1,y1(,deg)]}, optional
              pin["tray"] [slots] for a soft gold tray, optional pin["background"]
    palette   hero piece + named colour chips: pin["slots"][0] is the hero, pin["chips"]
              [[name, slot-or-[r,g,b]], ...] (a slot's colour is measured from its photo)

    python scripts/make_pin_variants.py --only <pin-id> ...   # render just those (no CSV)
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


def minimal_text(canvas: Image.Image, ink, headline: str, subline: str) -> None:
    """Editorial-style text straight on the backdrop (no bands): spaced serif headline with a
    short rule, and a quiet tap-to-shop line at the foot."""
    # knock-out: a feathered patch of the backdrop's own colour behind each text block, so
    # frame lines / arches / veins never run through the words
    for y0, y1 in ((26, 166), (H - 106, H - 40)):
        region = canvas.crop((0, y0, W, y1)).resize((1, 1), Image.LANCZOS).getpixel((0, 0))[:3]
        patch = Image.new("L", canvas.size, 0)
        ImageDraw.Draw(patch).rounded_rectangle((70, y0, W - 70, y1), radius=40, fill=235)
        patch = patch.filter(ImageFilter.GaussianBlur(14))
        canvas.paste(Image.new("RGB", canvas.size, region), (0, 0), patch)
    d = ImageDraw.Draw(canvas)
    ink = tuple(ink)
    hf = fit(d, headline, brc.SERIF_BOLD, 50, W - 120)
    brc.spaced_text(d, 46, headline, hf, ink, 4)
    centred(d, 112, subline, fit(d, subline, brc.SANS, 24, W - 140), ink)
    d.line((W / 2 - 70, 152, W / 2 + 70, 152), fill=ink, width=2)
    d.line((W / 2 - 70, H - 92, W / 2 + 70, H - 92), fill=ink, width=2)
    brc.spaced_text(d, H - 76, "TAP TO SHOP  ·  EXQUISITE.SILAT.AE", ImageFont.truetype(str(brc.SANS), 20), ink, 2)


def backdrop(outfit, pin) -> Image.Image:
    return brc.BACKGROUNDS[pin.get("background") or outfit["collage"]["background"]]()


def render_still(outfit, ink, pin) -> Image.Image:
    """Product-only still life: the pieces in pin["boxes"] (optionally tilted) on the backdrop,
    with soft trays under the slots in pin["tray"]."""
    canvas = backdrop(outfit, pin)
    trays = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    td = ImageDraw.Draw(trays)
    for slot in pin.get("tray", []):
        x0, y0, x1, y1 = pin["boxes"][slot][:4]
        cx, cy, rx, ry = (x0 + x1) / 2 * W, y1 * H - 18, (x1 - x0) * W * 0.62, 34
        td.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=(214, 182, 120, 120), outline=(176, 140, 84, 230), width=3)
    canvas.alpha_composite(trays.filter(ImageFilter.GaussianBlur(1)))
    for slot, box in pin["boxes"].items():
        brc.place(canvas, piece(outfit, slot), box)
    canvas = canvas.convert("RGB")
    minimal_text(canvas, ink, pin["headline"], pin["subline"])
    return canvas


def dominant(img: Image.Image):
    """Median colour of a cutout's opaque pixels (for palette chips)."""
    import numpy as np
    a = np.asarray(img.convert("RGBA"))
    px = a[a[..., 3] > 200][:, :3]
    return tuple(int(v) for v in np.median(px, axis=0)) if len(px) else (128, 128, 128)


def render_palette(outfit, ink, pin) -> Image.Image:
    """Hero piece large, with a column of named colour chips taken from the products."""
    canvas = backdrop(outfit, pin)
    brc.place(canvas, piece(outfit, pin["slots"][0]), pin.get("hero_box", (0.07, 0.17, 0.64, 0.86)))
    d = ImageDraw.Draw(canvas)
    chips = pin["chips"]
    lab = ImageFont.truetype(str(brc.SANS), 19)
    top, bot = 0.22 * H, 0.80 * H
    for i, (name, src) in enumerate(chips):
        colour = tuple(src) if isinstance(src, list) else dominant(piece(outfit, src))
        cx, cy = 0.82 * W, top + (bot - top) * i / max(len(chips) - 1, 1)
        r = 50
        d.ellipse((cx - r + 3, cy - r + 6, cx + r + 3, cy + r + 6), fill=(60, 40, 35, 40))
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=colour, outline=(255, 255, 255), width=4)
        d.text((cx - d.textlength(name, font=lab) / 2, cy + r + 8), name, font=lab, fill=tuple(ink))
    canvas = canvas.convert("RGB")
    minimal_text(canvas, ink, pin["headline"], pin["subline"])
    return canvas


RENDER = {"headline": render_headline, "piece": render_piece, "formula": render_formula,
          "still": render_still, "palette": render_palette}


def main() -> None:
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    looks = {o["id"]: o for o in json.loads(brc.LINKS_JSON.read_text(encoding="utf-8"))["outfits"]}
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    start = date.fromisoformat(plan["start"])
    only = set(sys.argv[sys.argv.index("--only") + 1:]) if "--only" in sys.argv else None
    rows = []
    for n, pin in enumerate(plan["pins"]):
        outfit = looks[pin["look"]]
        ink = (outfit.get("collage") or {}).get("ink") or plan["inks"][pin["look"]]
        out = OUT_DIR / f"{pin['id']}.jpg"
        if only is None or pin["id"] in only:
            img = RENDER[pin["type"]](outfit, ink, pin)
            img.save(out, "JPEG", quality=88, optimize=True, progressive=True)
            if only is not None:
                print(f"[OK] {pin['id']} -> {out.relative_to(ROOT)}")
                continue
        elif only is not None:
            continue

        slug = outfit.get("url_slug") or build_site.slugify(outfit["title"])
        link = (f"{build_site.SITE_URL}/looks/{slug}/?utm_source=pinterest&utm_medium=social"
                f"&utm_campaign={plan['utm_campaign']}&utm_content={pin['id']}")
        # "post_first_now": the first pin has no date, so Pinterest publishes it on upload;
        # the rest follow one a day from "start"
        first_now = plan.get("post_first_now")
        day = pin.get("date") or (start + timedelta(days=n - 1 if first_now else n)).isoformat()
        if first_now and n == 0:
            day = ""
        assert len(pin["title"]) <= 100, (pin["id"], len(pin["title"]))
        assert len(pin["description"]) <= 500, (pin["id"], len(pin["description"]))
        rows.append({
            "Title": pin["title"],
            "Media URL": f"{build_site.SITE_URL}/assets/pins/{pin['id']}.jpg",
            "Pinterest board": pin["board"],
            "Thumbnail": "",
            "Description": pin["description"],
            "Link": link,
            "Publish date": f"{day}T{plan['time_utc']}" if day else "",
            "Keywords": pin.get("keywords", ""),
        })
        print(f"[OK] {day or 'on upload':10} {pin['id']:22} {pin['type']:8} -> {out.relative_to(ROOT)}")

    if only is not None:
        return
    with CSV_PATH.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"\n{len(rows)} pins -> {CSV_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
