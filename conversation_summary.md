# Conversation Summary

Running log of assistant sessions on this repo, newest first.

## 2026-10-05 — Three fresh flat-lay looks from Amazon.ae (Claude Code)

### Starting point
- Local `main` was 4 commits behind `origin/main`; fast-forwarded with `git pull --ff-only`.
- The `landingImage` regex fix from the earlier session (below) was already done on the
  remote in `scripts/resolve_and_create_collages.py` (matches the `#landingImage` `<img>`
  tag first, then reads `src`, so attribute order doesn't matter).

### Old looks removed
- Cozy Autumn Coffee Run, Quiet Luxury Summer Dinner and Modest Pastel Spring Elegance were
  restyled once, then dropped at the user's request: removed from `links.json`, their asset
  folders and generated pages deleted, `update_links_ae.py` (one-off for those looks) deleted,
  Pinterest rows replaced.
- Their old URLs (`/looks/cozy-autumn-coffee-run/` etc.) now 404 — if those pins were
  published, they need updating on Pinterest.

### New looks (all products verified live on Amazon.ae, standard listings, in stock)
| Look | Categories | Collage style |
|---|---|---|
| Forest Green Knit & Denim Weekend | Casual, Autumn | cream paper with watercolour autumn leaves, scalloped rust border; clothes right, accessories left |
| Chocolate Bows & Cream Satin | Fancy, Autumn | blush linen with chocolate pin dots and scalloped chocolate lace down both edges; clothes right |
| Leopard Satin & Black Bell Sleeves | Fancy, Autumn | aged parchment, black double-rule frame with scrolled corner ornaments; clothes left |

- A first pass also had "Black Velvet & Mocha Satin Evening" and "Oat & Terracotta Modest
  Autumn"; the user didn't like them (bottoms looked too small next to the tops), so they were
  replaced (2026-10-07) by the chocolate and leopard looks, modelled on the site's older
  collages: large clothes, top over the bottom's waistband, decorative backdrops.
- Collages stack the top and bottom at true relative proportions (`stack` in `LOOKS`): the
  bottom's width is set relative to the top's, then the pair is scaled to fill the column, so
  maxi skirts and jeans stay long.
- Every piece uses the listing's **main** product photo (person-free), so the collage shows
  exactly what the shopper lands on. `scripts/cut_garments.py` (OpenCV GrabCut) is kept for
  garments that only have on-model photos; none of the current looks need it.
- Labels/descriptions written from the actual listings.

### Pipeline
```
python scripts/apply_real_products.py   # download main product photos per piece
python scripts/cut_garments.py          # garment cutouts for on-model photos
python scripts/build_real_collages.py   # per-look backdrops + layouts -> collage.png
python scripts/build_site.py            # regenerate pages from links.json
```
- `build_real_collages.py`: one entry per look in `LOOKS` (backdrop function, layout boxes,
  wordmark position, per-piece cutout tweaks for pearly/white products).
- Requirements now list Pillow, numpy, scipy, opencv-python. Local Python is 3.9 / Pillow 8.4;
  scripts include an `Image.Resampling` shim and a Windows font fallback.

### Link audit (site served on http://localhost:8080)
- All 21 "View on Amazon" links traced from the local pages: correct product, photo matches
  the collage piece, `tag=exquisitesila-21` + `rel="sponsored nofollow"` present.
- Low stock to watch ("only 1–2 left" for the default size): jeans, loafers, belt, cognac bag,
  cream satin skirt, glossy brown bag, leopard skirt.
- `pinterest_schedule.csv` now holds pins for the three new looks (8–10 Oct 2026).

## Earlier session (other platform)

- Tried to fix the `landingImage` regex in `resolve_and_create_collages.py`; edits failed to
  apply there. (Since fixed on `origin/main`, see above.)
- Later ran `git push` (remote up to date); background tasks were stopped by a server restart.
