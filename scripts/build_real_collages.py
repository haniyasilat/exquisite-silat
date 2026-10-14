"""Build flat-lay outfit collages from the real linked product photos.

    python scripts/build_real_collages.py                 # every look with a "collage" config
    python scripts/build_real_collages.py <outfit-id> ... # just those looks
    ... --repin   also regenerate pin.png for looks that already have one (Pinterest will
                  post the changed image again as a new pin)

Each look gets its own composition and its own hand-made backdrop (layout in
links.json under "collage", backdrops in BACKGROUNDS),
in the spirit of the site's earlier collages: background-free product cutouts
on a decorative backdrop, the outfit's top and bottom stacked large in one
column at true-to-life proportions (the bottom is sized relative to the top,
so long skirts and trousers stay long), and the accessories arranged in the
other column with breathing room so nothing overlaps.

Each piece image comes from assets/products/<folder>/:
    <slot>_cut.png  - pre-cut garment from scripts/cut_garments.py (on-model photos)
    <slot>.jpg      - plain studio photo; its white backdrop is removed here
"""

import json
import math
import pathlib
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from scipy import ndimage

if not hasattr(Image, "Resampling"):  # Pillow < 9.1
    Image.Resampling = Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
ASSET_ROOT = ROOT / "assets" / "products"
LINKS_JSON = ROOT / "links.json"

W, H = 848, 1264
SS = 2  # supersampling for line art


def _font(*candidates: str) -> pathlib.Path:
    for c in candidates:
        p = pathlib.Path(c)
        if p.is_file():
            return p
    raise FileNotFoundError(candidates[0])


SERIF_BOLD = _font("/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf", r"C:\Windows\Fonts\timesbd.ttf")
SANS = _font("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", r"C:\Windows\Fonts\arial.ttf")

PIN_BAND = 150  # height of the call-to-action band under the collage on the Pinterest image
CREAM = (250, 243, 232)


# ---------- shared texture helpers ----------

def smooth_noise(shape, scale, seed):
    """Low-frequency noise in [0, 1] (upsampled random grid)."""
    rng = np.random.default_rng(seed)
    gh, gw = max(2, shape[0] // scale + 2), max(2, shape[1] // scale + 2)
    grid = Image.fromarray((rng.random((gh, gw)) * 255).astype(np.uint8))
    up = grid.resize((shape[1], shape[0]), Image.Resampling.BICUBIC)
    return np.asarray(up, np.float32) / 255.0


def paper(base, seed) -> np.ndarray:
    """Flat colour with subtle paper grain and wash variation (float RGB array)."""
    grain = 0.97 + 0.06 * smooth_noise((H, W), 5, seed)
    wash = 0.98 + 0.04 * smooth_noise((H, W), 90, seed + 1)
    return np.array(base, np.float32) * (grain * wash)[..., None]


def tint(rgb: np.ndarray, colour, strength: np.ndarray) -> np.ndarray:
    s = np.clip(strength, 0, 1)[..., None]
    return rgb * (1 - s) + np.array(colour, np.float32) * s


def to_image(rgb: np.ndarray) -> Image.Image:
    return Image.fromarray(rgb.clip(0, 255).astype(np.uint8)).convert("RGBA")


def line_layer(draw_fn, colour, alpha=235, seed=0, unevenness=0.25) -> Image.Image:
    """Render line art at 2x via draw_fn(draw, scale), return a soft RGBA layer."""
    mask = Image.new("L", (W * SS, H * SS), 0)
    draw_fn(ImageDraw.Draw(mask), SS)
    mask = mask.resize((W, H), Image.Resampling.LANCZOS)
    a = np.asarray(mask, np.float32) / 255.0
    a *= (1 - unevenness) + unevenness * smooth_noise((H, W), 40, seed)
    out = np.zeros((H, W, 4), np.uint8)
    out[..., :3] = colour
    out[..., 3] = (a * alpha).astype(np.uint8)
    return Image.fromarray(out, "RGBA")


def dot_grid(step, radius, seed, jitter=1.2) -> np.ndarray:
    """Offset-row polka-dot mask in [0, 1]."""
    dots = Image.new("L", (W * SS, H * SS), 0)
    d = ImageDraw.Draw(dots)
    rng = np.random.default_rng(seed)
    st, r = step * SS, radius * SS
    for row, y in enumerate(range(-st, H * SS + st, st)):
        off = st // 2 if row % 2 else 0
        for x in range(-st + off, W * SS + st, st):
            jx, jy = rng.normal(0, jitter * SS, 2)
            d.ellipse((x + jx - r, y + jy - r, x + jx + r, y + jy + r), fill=255)
    dots = dots.resize((W, H), Image.Resampling.LANCZOS)
    return np.asarray(dots, np.float32) / 255.0


# ---------- backdrops ----------

def bg_autumn_leaves(seed=3) -> Image.Image:
    """Cream paper scattered with soft watercolour leaves, scalloped rust border."""
    rgb = paper((248, 241, 229), seed)
    rng = np.random.default_rng(seed)
    palette = [(186, 96, 54), (206, 152, 66), (132, 128, 74), (164, 74, 48)]
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for _ in range(46):
        cx, cy = rng.uniform(0, W), rng.uniform(0, H)
        length, ang = rng.uniform(46, 96), rng.uniform(0, 2 * math.pi)
        colour = palette[rng.integers(len(palette))]
        alpha = int(rng.uniform(40, 85))
        half = length * rng.uniform(0.22, 0.32)
        pts_l, pts_r = [], []
        for i in range(21):
            t = i / 20
            w = half * math.sin(math.pi * t) ** 0.9
            along = (t - 0.5) * length
            for side, pts in ((1, pts_l), (-1, pts_r)):
                x, y = along, side * w
                pts.append((cx + x * math.cos(ang) - y * math.sin(ang), cy + x * math.sin(ang) + y * math.cos(ang)))
        d = ImageDraw.Draw(layer)
        d.polygon(pts_l + pts_r[::-1], fill=(*colour, alpha))
        tip0, tip1 = pts_l[0], pts_l[-1]
        d.line([tip0, tip1], fill=(*colour, min(255, alpha + 40)), width=1)
        stem = (tip0[0] - (tip1[0] - tip0[0]) * 0.12, tip0[1] - (tip1[1] - tip0[1]) * 0.12)
        d.line([tip0, stem], fill=(*colour, min(255, alpha + 40)), width=2)
    layer = layer.filter(ImageFilter.GaussianBlur(0.8))
    img = to_image(rgb)
    img.alpha_composite(layer)

    def scallops(d, s):
        m, r = 30 * s, 13 * s
        x0, y0, x1, y1 = m, m, W * s - m, H * s - m
        nx, ny = int((x1 - x0) / (2 * r)), int((y1 - y0) / (2 * r))
        sx, sy = (x1 - x0) / nx, (y1 - y0) / ny
        for i in range(nx):
            cx = x0 + sx * (i + 0.5)
            d.arc((cx - sx / 2, y0 - r, cx + sx / 2, y0 + r), 180, 360, fill=255, width=4 * s)
            d.arc((cx - sx / 2, y1 - r, cx + sx / 2, y1 + r), 0, 180, fill=255, width=4 * s)
        for j in range(ny):
            cy = y0 + sy * (j + 0.5)
            d.arc((x0 - r, cy - sy / 2, x0 + r, cy + sy / 2), 90, 270, fill=255, width=4 * s)
            d.arc((x1 - r, cy - sy / 2, x1 + r, cy + sy / 2), 270, 450, fill=255, width=4 * s)
        d.rectangle((x0 + 10 * s, y0 + 10 * s, x1 - 10 * s, y1 - 10 * s), outline=255, width=2 * s)

    img.alpha_composite(line_layer(scallops, (168, 84, 50), seed=seed))
    return img


def bg_coquette_lace(seed=12) -> Image.Image:
    """Blush linen with chocolate pin dots and scalloped chocolate lace down both edges."""
    rgb = paper((242, 226, 218), seed)
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    weave = 0.99 + 0.012 * np.sin(x * 2.2) * np.sin(y * 2.2)  # faint linen cross-weave
    rgb *= weave[..., None]
    rgb = tint(rgb, (110, 70, 54), dot_grid(34, 2.2, seed) * 0.42)
    img = to_image(rgb)

    def lace(d, s):
        band, rad, period = 58 * s, 20 * s, 40 * s
        for side in (0, 1):
            def X(v):  # mirror for the right-hand strip
                return v if side == 0 else W * s - v

            def ell(cx, cy, rx, ry, fill):
                xa, xb = sorted((X(cx - rx), X(cx + rx)))
                d.ellipse((xa, cy - ry, xb, cy + ry), fill=fill)

            xa, xb = sorted((X(0), X(band)))
            d.rectangle((xa, 0, xb, H * s), fill=255)
            for yc in range(period // 2, H * s + period, period):  # scallops + picots
                ell(band, yc, rad, rad, 255)
                for k in range(5):
                    a = math.radians(-60 + 30 * k)
                    ell(band + (rad + 5 * s) * math.cos(a), yc + (rad + 5 * s) * math.sin(a), 2.6 * s, 2.6 * s, 255)
            for row, yy in enumerate(range(0, H * s, 12 * s)):  # net mesh
                for xx in range(8 * s + (6 * s if row % 2 else 0), band - 4 * s, 12 * s):
                    ell(xx, yy, 3.4 * s, 3.4 * s, 0)
            for yc in range(period // 2, H * s + period, period):  # scallop eyelets
                ell(band + 7 * s, yc, 6 * s, 6 * s, 0)
            for yc in range(period, H * s, period * 3):  # rosettes
                cx = band / 2 - 2 * s
                ell(cx, yc, 17 * s, 17 * s, 255)
                for k in range(6):
                    a = math.radians(60 * k)
                    ell(cx + 10 * s * math.cos(a), yc + 10 * s * math.sin(a), 4 * s, 4 * s, 0)
                ell(cx, yc, 3 * s, 3 * s, 0)

    img.alpha_composite(line_layer(lace, (92, 56, 42), alpha=240, seed=seed, unevenness=0.08))
    return img


def bg_vintage_parchment(seed=21) -> Image.Image:
    """Aged parchment with a black double-rule frame and scrolled corner ornaments."""
    base = paper((232, 213, 184), seed)
    blotch = smooth_noise((H, W), 110, seed + 3) * 0.6 + smooth_noise((H, W), 35, seed + 4) * 0.4
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    vign = np.clip(np.hypot((x - W / 2) / (W / 2), (y - H / 2) / (H / 2)) - 0.55, 0, 1)
    rgb = tint(base, (176, 140, 98), blotch * 0.28 + vign * 0.55)
    img = to_image(rgb)

    def ornaments(d, s):
        m1, m2 = 34 * s, 46 * s
        d.rectangle((m1, m1, W * s - m1, H * s - m1), outline=255, width=4 * s)
        d.rectangle((m2, m2, W * s - m2, H * s - m2), outline=255, width=2 * s)

        def poly(pts, width):
            d.line(pts, fill=255, width=int(width), joint="curve")

        def curl(cx, cy, dx, dy, along_x):
            # a flourish running along one edge of the corner, ending in a spiral curl
            length, amp = 150 * s, 15 * s
            pts = []
            for i in range(60):
                u = i / 59
                a, b = u * length, amp * math.sin(u * math.pi) * 0.9
                pts.append((cx + dx * (a if along_x else b), cy + dy * (b if along_x else a)))
            poly(pts, 2.5 * s)
            ex, ey = pts[-1]
            spiral = []
            for i in range(80):
                t = i / 79 * 2.2 * math.pi
                r = 13 * s * (1 - t / (2.6 * math.pi))
                ang = (math.pi if along_x else math.pi / 2) + t
                ox, oy = r * math.cos(ang), r * math.sin(ang)
                spiral.append((ex + dx * (13 * s + ox if along_x else oy),
                               ey + dy * (oy if along_x else 13 * s + ox)))
            poly(spiral, 2.2 * s)
            for u in (0.3, 0.55):  # little leaves along the flourish
                px, py = pts[int(u * 59)]
                lx, ly = (0, dy * 10 * s) if along_x else (dx * 10 * s, 0)
                d.ellipse((px + lx - 5 * s, py + ly - 3 * s, px + lx + 5 * s, py + ly + 3 * s), fill=255)

        for cx, cy, dx, dy in ((m2, m2, 1, 1), (W * s - m2, m2, -1, 1), (m2, H * s - m2, 1, -1),
                               (W * s - m2, H * s - m2, -1, -1)):
            ox, oy = cx + dx * 12 * s, cy + dy * 12 * s
            curl(ox, oy, dx, dy, True)
            curl(ox, oy, dx, dy, False)
            q = 7 * s
            d.polygon([(ox, oy - q), (ox + q, oy), (ox, oy + q), (ox - q, oy)], fill=255)

    img.alpha_composite(line_layer(ornaments, (40, 30, 24), alpha=225, seed=seed, unevenness=0.18))
    return img


def marble(base, vein, seed, strength=0.40) -> np.ndarray:
    """Soft marble: warped sine veins over a pale base (float RGB array)."""
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    warp = (smooth_noise((H, W), 160, seed) - 0.5) * 150 + (smooth_noise((H, W), 45, seed + 1) - 0.5) * 30
    v1 = np.abs(np.sin((x * 0.55 + y * 0.85 + warp) / 95.0)) ** 90
    v2 = np.abs(np.sin((x * -0.7 + y * 0.6 + warp * 0.8) / 60.0)) ** 140 * 0.55
    veins = np.clip(v1 + v2, 0, 1) * (0.45 + 0.55 * smooth_noise((H, W), 70, seed + 2))
    rgb = paper(base, seed + 3)
    return tint(rgb, vein, ndimage.gaussian_filter(veins, 1.1) * strength)


def bg_marble_gold(seed=31) -> Image.Image:
    """White marble with grey veining and a thin gold art-deco frame (stepped corners)."""
    img = to_image(marble((246, 244, 241), (150, 146, 142), seed))
    gold = (182, 146, 82)

    def deco(d, s):
        m, st = 30 * s, 26 * s
        for inset, wdt in ((0, 3), (10, 1.5)):
            a = m + inset * s
            b = st - inset * s * 0.4
            pts = [(a + b, a), (W * s - a - b, a), (W * s - a - b, a + b * 0.0), (W * s - a, a + b),
                   (W * s - a, H * s - a - b), (W * s - a - b, H * s - a), (a + b, H * s - a), (a, H * s - a - b),
                   (a, a + b), (a + b, a)]
            d.line(pts, fill=255, width=int(wdt * s), joint="curve")
        for cx, cy in ((m, m), (W * s - m, m), (m, H * s - m), (W * s - m, H * s - m)):  # corner fans
            for r in (14, 22):
                d.arc((cx - r * s, cy - r * s, cx + r * s, cy + r * s), 0, 360, fill=255, width=int(1.5 * s))

    img.alpha_composite(line_layer(deco, gold, alpha=230, seed=seed, unevenness=0.1))
    return img


def bg_desert_dunes(seed=41) -> Image.Image:
    """Warm Dubai desert: soft peach sky fading into layered sand dunes, with sand ripples."""
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    t = y / H
    sky_top, sky_low = np.array((247, 228, 210), np.float32), np.array((251, 240, 226), np.float32)
    rgb = sky_top * (1 - t[..., None]) + sky_low * t[..., None]
    layers = [(0.30, (238, 214, 182)), (0.48, (232, 202, 164)), (0.66, (226, 191, 150)), (0.84, (221, 183, 140))]
    for i, (yy, col) in enumerate(layers):
        crest = H * yy + 34 * np.sin(x / W * math.pi * (1.3 + i * 0.35) + i * 1.7) \
            + (smooth_noise((1, W), 90, seed + i)[0] - 0.5) * 40
        mask = np.clip((y - crest) / 6.0, 0, 1)
        shade = 0.96 + 0.08 * np.clip((y - crest) / 260.0, 0, 1)  # lighter crest, deeper base
        rgb = rgb * (1 - mask[..., None]) + (np.array(col, np.float32) * shade[..., None]) * mask[..., None]
    ripples = (np.sin((y + 18 * np.sin(x / 70.0)) / 5.5) * 0.5 + 0.5) * (t > 0.3)
    rgb *= (1 - 0.025 * ripples)[..., None]
    rgb *= (0.985 + 0.03 * smooth_noise((H, W), 6, seed + 9))[..., None]  # sand grain
    img = to_image(rgb)

    def sun(d, s):
        cx, cy, r = W * s * 0.82, H * s * 0.12, 46 * s
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=255)

    img.alpha_composite(line_layer(sun, (250, 214, 168), alpha=170, seed=seed, unevenness=0.05))
    return img


def bg_linen_arch(seed=51) -> Image.Image:
    """Warm linen with a large Arabesque arch window (lighter panel, double gold outline)."""
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    weave = 0.985 + 0.02 * np.sin(x * 1.9) * np.sin(y * 1.9) + 0.012 * np.sin(y * 0.9)
    rgb = paper((236, 225, 210), seed) * weave[..., None]
    img = to_image(rgb)
    cx, top, half, bot = W / 2, H * 0.06, W * 0.40, H * 0.92

    def arch_path(d, s, inset, fill=None, width=0):
        hw = (half - inset) * s
        c, t, b = cx * s, (top + inset) * s, (bot - inset * 0.3) * s
        shoulder = t + hw * 1.05
        pts = [(c - hw, b), (c - hw, shoulder)]
        for i in range(41):  # pointed (ogee-ish) arch: two arcs meeting at the apex
            u = i / 40
            ang = math.pi * (1 - u)
            px = c + hw * math.cos(ang)
            py = shoulder - hw * 1.05 * math.sin(ang) * (1 + 0.22 * (1 - abs(1 - 2 * u)))
            pts.append((px, py))
        pts += [(c + hw, shoulder), (c + hw, b)]
        if fill is not None:
            d.polygon(pts, fill=fill)
        else:
            d.line(pts, fill=255, width=width, joint="curve")

    panel = Image.new("L", (W * SS, H * SS), 0)
    arch_path(ImageDraw.Draw(panel), SS, 0, fill=255)
    panel = panel.resize((W, H), Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(2))
    light = Image.new("RGBA", (W, H), (250, 244, 234, 0))
    light.putalpha(panel.point(lambda v: int(v * 0.85)))
    img.alpha_composite(light)
    img.alpha_composite(line_layer(lambda d, s: (arch_path(d, s, 0, width=4 * s), arch_path(d, s, 12, width=2 * s)),
                                   (176, 140, 84), alpha=225, seed=seed, unevenness=0.12))
    return img


# ---------- looks ----------
# Each look's layout lives in links.json under the outfit's "collage" key:
#   background  name from BACKGROUNDS below
#   ink         [r, g, b] for the wordmark
#   wordmark    [x, y] canvas fractions (centre-x, top-y)
#   stack       the outfit's top + bottom, stacked in one column at real proportions:
#     top, bottom  piece slots
#     cx           column centre (canvas fraction)
#     y0, y1       vertical span the pair is fitted into
#     max_w        widest the top may be
#     ratio        bottom width relative to top width (top width includes its sleeves)
#     overlap      how far the top's hem sits over the bottom's waistband (fraction of top height)
#               (optional: leave it out to place the garments with "boxes" too, e.g. a long
#               coat and trousers side by side)
#   boxes       slot -> [x0, y0, x1, y1] or [x0, y0, x1, y1, degrees]; each piece is fitted
#               inside its box (after the optional tilt) and centred, so non-overlapping boxes
#               mean non-overlapping pieces
#   cutout      optional slot -> [white, colored, pockets] args for cutout_white_bg
#               (pale/pearly products: [250, 236, false]; white watch dials: [242, 205, false])
# The look's asset folder is the folder of its collage_image.
BACKGROUNDS = {
    "autumn_leaves": bg_autumn_leaves,
    "coquette_lace": bg_coquette_lace,
    "vintage_parchment": bg_vintage_parchment,
    "marble_gold": bg_marble_gold,
    "desert_dunes": bg_desert_dunes,
    "linen_arch": bg_linen_arch,
}


# ---------- product cutouts ----------

def cutout_white_bg(img: Image.Image, white: int = 242, colored: int = 205, pockets: bool = True) -> Image.Image:
    """Remove a near-white studio backdrop (and its soft drop shadow).

    Only light pixels *connected to the photo border* are treated as backdrop,
    so white or cream areas inside the product (pearls, a cream bag) stay
    opaque; sizeable pure-white pockets (seen through bag handles, hoops) are
    backdrop too. Within the backdrop, alpha fades from 0 (white) to 1
    (colored) so the edge stays soft.
    """
    arr = np.array(img.convert("RGBA")).astype(np.float32)
    min_c = arr[..., :3].min(axis=2)
    light = min_c > colored
    lbl, _ = ndimage.label(light)
    edge_ids = set(np.unique(np.concatenate([lbl[0], lbl[-1], lbl[:, 0], lbl[:, -1]]))) - {0}
    backdrop = np.isin(lbl, list(edge_ids))

    pure = (min_c >= 247) & ~backdrop
    plbl, pn = ndimage.label(pure)
    if pockets and pn:
        sizes = ndimage.sum(pure, plbl, range(1, pn + 1))
        min_px = arr.shape[0] * arr.shape[1] * 0.0015
        backdrop |= np.isin(plbl, [i + 1 for i, s in enumerate(sizes) if s >= min_px])

    fade = np.clip((white - min_c) / max(white - colored, 1), 0.0, 1.0)
    alpha = np.where(backdrop, fade, 1.0)
    alpha = ndimage.gaussian_filter(alpha, 0.6)
    arr[..., 3] = np.minimum(arr[..., 3], alpha * 255.0)
    return Image.fromarray(arr.astype(np.uint8), "RGBA")


def trim_alpha(img: Image.Image) -> Image.Image:
    bbox = img.split()[-1].point(lambda v: 255 if v > 12 else 0).getbbox()
    return img.crop(bbox) if bbox else img


def piece_image(asset_dir: pathlib.Path, slot: str, cutout_args=()) -> Image.Image:
    pre = asset_dir / f"{slot.lower()}_cut.png"
    if pre.is_file():
        return trim_alpha(Image.open(pre).convert("RGBA"))
    return trim_alpha(cutout_white_bg(Image.open(asset_dir / f"{slot.lower()}.jpg"), *cutout_args))


def soft_shadow(img: Image.Image, blur: int = 10, opacity: int = 50) -> Image.Image:
    pad = blur * 3
    canvas = Image.new("RGBA", (img.width + pad * 2, img.height + pad * 2), (0, 0, 0, 0))
    sh = Image.new("RGBA", img.size, (60, 40, 35, opacity))
    canvas.paste(sh, (pad + 3, pad + 6), img.split()[-1])
    canvas = canvas.filter(ImageFilter.GaussianBlur(blur))
    canvas.alpha_composite(img, (pad, pad))
    return canvas


def paste_at(canvas: Image.Image, img: Image.Image, cx: int, top_y: int) -> None:
    shadowed = soft_shadow(img)
    pad = (shadowed.width - img.width) // 2
    canvas.alpha_composite(shadowed, (cx - img.width // 2 - pad, top_y - pad))


def place(canvas: Image.Image, img: Image.Image, box) -> None:
    """Fit img inside box [x0, y0, x1, y1(, degrees)] and centre it; optional tilt."""
    x0, y0, x1, y1 = (int(box[0] * W), int(box[1] * H), int(box[2] * W), int(box[3] * H))
    img = img.copy()
    if len(box) > 4 and box[4]:
        img = img.rotate(box[4], expand=True, resample=Image.Resampling.BICUBIC)
    img.thumbnail((x1 - x0, y1 - y0), Image.Resampling.LANCZOS)
    paste_at(canvas, img, (x0 + x1) // 2, (y0 + y1) // 2 - img.height // 2)


def place_stack(canvas: Image.Image, top: Image.Image, bottom: Image.Image, st: dict) -> None:
    """Stack top over bottom at true relative proportions, filling the column."""
    a_top, a_bot = top.height / top.width, bottom.height / bottom.width
    unit_h = a_top + st["ratio"] * a_bot - st["overlap"] * a_top  # total height when top width = 1
    avail = (st["y1"] - st["y0"]) * H
    tw = min(st["max_w"] * W, avail / unit_h)
    th, bw = tw * a_top, tw * st["ratio"]
    bh = bw * a_bot
    total = th + bh - st["overlap"] * th
    start = st["y0"] * H + (avail - total) / 2
    cx = int(st["cx"] * W)
    top_img = top.resize((int(tw), int(th)), Image.Resampling.LANCZOS)
    bot_img = bottom.resize((int(bw), int(bh)), Image.Resampling.LANCZOS)
    paste_at(canvas, bot_img, cx, int(start + th * (1 - st["overlap"])))
    paste_at(canvas, top_img, cx, int(start))  # top's hem sits over the waistband


def draw_wordmark(canvas: Image.Image, colour, at) -> None:
    """Small, quiet brand mark."""
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.truetype(str(SERIF_BOLD), 21)
    text = "EXQUISITE SILAT"
    tb = draw.textbbox((0, 0), text, font=font)
    draw.text((int(W * at[0]) - (tb[2] - tb[0]) // 2, int(H * at[1])), text, font=font, fill=(*colour, 255))


def spaced_text(draw: ImageDraw.ImageDraw, y: int, text: str, font, fill, spacing: int) -> None:
    """Centred text with extra letter spacing."""
    widths = [draw.textbbox((0, 0), ch, font=font)[2] for ch in text]
    x = (W - (sum(widths) + spacing * (len(text) - 1))) / 2
    for ch, w in zip(text, widths):
        draw.text((x, y), ch, font=font, fill=fill)
        x += w + spacing


def make_pin(collage: Image.Image, ink) -> Image.Image:
    """Pinterest version: the collage with a call-to-action band underneath.

    The band sits below the collage (it covers nothing) in the look's ink colour. The
    site keeps the clean collage, since its Shop buttons sit right beside it.
    """
    pin = Image.new("RGB", (W, H + PIN_BAND), tuple(ink))
    pin.paste(collage.convert("RGB"), (0, 0))
    draw = ImageDraw.Draw(pin)
    draw.line((0, H, W, H), fill=CREAM, width=2)
    spaced_text(draw, H + 36, "TAP TO SHOP THE LOOK", ImageFont.truetype(str(SERIF_BOLD), 40), CREAM, 4)
    spaced_text(draw, H + 96, "every piece linked  Â·  exquisite.silat.ae",
                ImageFont.truetype(str(SANS), 20), CREAM, 1)
    return pin


# ---------- build ----------

def asset_dir_for(outfit: dict) -> pathlib.Path:
    return ROOT / pathlib.Path(outfit["collage_image"].split("?")[0]).parent


def build_outfit_collage(outfit: dict) -> None:
    look = outfit["collage"]
    asset_dir = asset_dir_for(outfit)
    cut = look.get("cutout", {})

    def image(slot):
        return piece_image(asset_dir, slot, tuple(cut.get(slot, ())))

    canvas = BACKGROUNDS[look["background"]]()
    st = look.get("stack")  # optional: without it, every piece (garments too) uses "boxes"
    if st:
        place_stack(canvas, image(st["top"]), image(st["bottom"]), st)
    for piece in outfit["pieces"]:
        slot = piece["slot"]
        if st and slot in (st["top"], st["bottom"]):
            continue
        box = look["boxes"].get(slot)
        if not box:
            print(f"[WARN] {outfit['slug']}: no layout box for {slot}, skipped")
            continue
        place(canvas, image(slot), box)

    draw_wordmark(canvas, tuple(look["ink"]), look["wordmark"])
    out_path = asset_dir / "collage.png"
    canvas.convert("RGB").save(out_path, "PNG", optimize=True)
    pin_path = asset_dir / "pin.png"
    if is_committed(pin_path) and not REPIN:
        # Pinterest re-pins a feed item whose image changes, so a published (committed)
        # look's pin.png is left alone, e.g. after swapping a sold-out product. A new look's
        # pin.png isn't committed yet, so it is regenerated while the look is being refined.
        print(f"[OK] wrote {out_path.relative_to(ROOT)} (kept existing pin.png)")
        return
    pin_copy = outfit.get("pin") or {}
    if pin_copy.get("headline"):
        # same design as the bulk pins: keyword headline banner on top, tap-to-shop below
        import make_pin_variants  # local import: it imports this module
        pin_img = make_pin_variants.render_headline(outfit, look["ink"], pin_copy)
    else:
        pin_img = make_pin(canvas, look["ink"])
    pin_img.save(pin_path, "PNG", optimize=True)
    print(f"[OK] wrote {out_path.relative_to(ROOT)} + pin.png")


REPIN = "--repin" in sys.argv


def is_committed(path: pathlib.Path) -> bool:
    """True if git already tracks this file (i.e. it has been published)."""
    import subprocess
    r = subprocess.run(["git", "ls-files", "--error-unmatch", str(path.relative_to(ROOT))],
                       cwd=ROOT, capture_output=True)
    return r.returncode == 0


def main() -> None:
    """Build collages for every look with a "collage" config, or only the ids given."""
    only = {a for a in sys.argv[1:] if not a.startswith("--")}
    data = json.loads(LINKS_JSON.read_text(encoding="utf-8"))
    for outfit in data["outfits"]:
        if "collage" in outfit and (not only or outfit["id"] in only):
            build_outfit_collage(outfit)


if __name__ == "__main__":
    main()
