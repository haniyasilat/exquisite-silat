"""Lift garments off on-model Amazon product photos -> transparent PNG cutouts.

Some linked products only have photos of the piece being worn. For the flat-lay
collages we need the garment alone, so this runs a colour-seeded GrabCut
(OpenCV) per photo:

  * pixels close (in Lab) to sampled garment colours start as probable-foreground
  * pixels close to sampled "reject" colours (skin, hair, other clothes) and the
    white studio background start as background
  * everything outside the garment's bounding box is definite background

GrabCut refines the boundary, then we drop specks, fill holes, smooth the
contour and feather the edge. Output: assets/products/<folder>/<slot>_cut.png,
which build_real_collages.py prefers over its own white-background cutout.

    python scripts/cut_garments.py            # all
    python scripts/cut_garments.py ql_vest    # one
"""

import pathlib
import sys

import cv2
import numpy as np
from scipy import ndimage

ROOT = pathlib.Path(__file__).resolve().parent.parent
ASSET_ROOT = ROOT / "assets" / "products"

# key: (folder, slot, box, keep seeds, reject seeds, mode-or-threshold, margin, smooth)
#   box / seeds are fractions of the photo's width/height
#   mode: number = Lab distance threshold for keep seeds; "rect" = classic
#   box-initialised GrabCut (garment on a plain non-white wall); "chroma" =
#   key on gold yellow (jewellery on a coloured backdrop)
#   smooth: contour smoothing radius in px at 1000px working size
# Empty while every current look uses person-free product photos; add an entry
# here when a linked garment only has on-model photos.
SPECS = {}

# Explicit background zones per photo, forced to definite background:
#   (x0, y0, x1, y1, predicate(L, b) or None)  - rectangle, optionally filtered
#   ("poly", [(x, y), ...])                     - polygon traced on the photo
BG_ZONES = {}

# Use a different gallery photo of the same listing when the main one hides the
# garment: key -> file name in the look's asset folder.
SOURCE_OVERRIDE = {}


def patch_lab(lab, x, y, r=6):
    h, w = lab.shape[:2]
    cx, cy = int(x * w), int(y * h)
    p = lab[max(cy - r, 0):cy + r, max(cx - r, 0):cx + r].reshape(-1, 3)
    return np.median(p, axis=0)


def min_dist(lab, colours):
    d = np.full(lab.shape[:2], 1e9, np.float32)
    for c in colours:
        d = np.minimum(d, np.linalg.norm(lab - c, axis=2))
    return d


def border_white(img, thr):
    """Near-white pixels connected to the image border (the studio backdrop)."""
    near = img.min(axis=2) > thr
    lbl, _ = ndimage.label(near)
    ids = set(np.unique(np.concatenate([lbl[0], lbl[-1], lbl[:, 0], lbl[:, -1]]))) - {0}
    return np.isin(lbl, list(ids))


def initial_mask(key, small, lab, box, keep, reject, mode, margin):
    sh, sw = small.shape[:2]
    mask = np.full((sh, sw), cv2.GC_PR_BGD, np.uint8)
    x0, y0, x1, y1 = int(box[0] * sw), int(box[1] * sh), int(box[2] * sw), int(box[3] * sh)
    inbox = np.zeros_like(mask, bool)
    inbox[y0:y1, x0:x1] = True
    white = border_white(small, 238)

    if mode == "chroma":
        b = lab[..., 2] - 128
        L = lab[..., 0]
        mask[(b > 28) | ((L < 120) & (b > 12))] = cv2.GC_PR_FGD
        mask[ndimage.binary_erosion(b > 45, iterations=2)] = cv2.GC_FGD
        mask[(b < 14) & (L > 150)] = cv2.GC_BGD
    elif mode == "rect":
        # classic GrabCut: tight box on a plain (non-white) wall; reject colours
        # (skin, shoes) start as probable background, keep colours as definite FG
        d_rej = min_dist(lab, [patch_lab(lab, x, y) for x, y in reject])
        d_keep = min_dist(lab, [patch_lab(lab, x, y) for x, y in keep])
        mask[inbox] = cv2.GC_PR_FGD
        mask[inbox & (d_rej < margin) & (d_keep > d_rej)] = cv2.GC_PR_BGD
        for x, y in keep:
            cx, cy = int(x * sw), int(y * sh)
            mask[cy - 12:cy + 12, cx - 12:cx + 12] = cv2.GC_FGD
        mask[~inbox] = cv2.GC_BGD
    else:
        d_keep = min_dist(lab, [patch_lab(lab, x, y) for x, y in keep])
        d_rej = min_dist(lab, [patch_lab(lab, x, y) for x, y in reject])
        mask[(d_keep < mode) & (d_keep + margin < d_rej) & inbox] = cv2.GC_PR_FGD
        core = (d_keep < mode * 0.6) & (d_keep + margin * 2 < d_rej) & inbox
        mask[ndimage.binary_erosion(core, iterations=4)] = cv2.GC_FGD
        mask[white | ~inbox] = cv2.GC_BGD
        mask[(d_rej + margin < d_keep) & (d_rej < mode * 0.8)] = cv2.GC_BGD

    L, b = lab[..., 0], lab[..., 2] - 128
    for z in BG_ZONES.get(key, []):
        if z[0] == "poly":
            pts = np.array([[int(x * sw), int(y * sh)] for x, y in z[1]], np.int32)
            zone = np.zeros_like(mask)
            cv2.fillPoly(zone, [pts], 1)
            mask[zone.astype(bool)] = cv2.GC_BGD
            continue
        rx0, ry0, rx1, ry1, pred = z
        zone = np.zeros_like(mask, bool)
        zone[int(ry0 * sh):int(ry1 * sh), int(rx0 * sw):int(rx1 * sw)] = True
        mask[zone & (pred(L, b) if pred else True)] = cv2.GC_BGD
    return mask


def cut(key: str) -> pathlib.Path:
    folder, slot, box, keep, reject, mode, margin, smooth = SPECS[key]
    src = ASSET_ROOT / folder / SOURCE_OVERRIDE.get(key, f"{slot}.jpg")
    bgr = cv2.imread(str(src))
    h, w = bgr.shape[:2]
    scale = 1000 / max(h, w)
    small = cv2.resize(bgr, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)
    lab = cv2.cvtColor(small, cv2.COLOR_BGR2LAB).astype(np.float32)

    mask = initial_mask(key, small, lab, box, keep, reject, mode, margin)
    bgd, fgd = np.zeros((1, 65), np.float64), np.zeros((1, 65), np.float64)
    cv2.grabCut(small, mask, None, bgd, fgd, 6, cv2.GC_INIT_WITH_MASK)
    fg = np.isin(mask, (cv2.GC_FGD, cv2.GC_PR_FGD))

    # drop specks (keep blobs >= 4% of the largest), fill holes
    fg = ndimage.binary_opening(fg, iterations=2)
    lbl, n = ndimage.label(fg)
    if n:
        sizes = ndimage.sum(fg, lbl, range(1, n + 1))
        fg = np.isin(lbl, [i + 1 for i, s in enumerate(sizes) if s >= max(sizes) * 0.04])
    fg = ndimage.binary_fill_holes(fg)
    fg = ndimage.binary_closing(fg, iterations=3)

    # smooth the contour: blur the mask and re-threshold (removes ragged hair/skin edges)
    soft = fg.astype(np.float32)
    if smooth:
        soft = cv2.GaussianBlur(soft, (0, 0), smooth)
        soft = (soft > 0.5).astype(np.float32)
    alpha = cv2.GaussianBlur(soft, (0, 0), 1.2)
    alpha = cv2.resize(alpha, (w, h), interpolation=cv2.INTER_LINEAR)
    alpha = np.clip((alpha - 0.15) / 0.7, 0, 1)

    rgba = cv2.cvtColor(bgr, cv2.COLOR_BGR2BGRA)
    rgba[..., 3] = (alpha * 255).astype(np.uint8)
    ys, xs = np.where(alpha > 0.05)
    rgba = rgba[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    out = ASSET_ROOT / folder / f"{slot}_cut.png"
    cv2.imwrite(str(out), rgba)
    print(f"[OK] {key} -> {out.relative_to(ROOT)}  (crop origin x={xs.min() / w:.3f}, y={ys.min() / h:.3f} of source)")
    return out


def main() -> None:
    for key in sys.argv[1:] or SPECS:
        cut(key)


if __name__ == "__main__":
    main()
