# Weekly look playbook

The weekly scheduled task follows this file. Goal: one new, genuinely shoppable outfit look
every week → auto-pinned to Pinterest via RSS → visitors click through to the look page → buy
on Amazon.ae through `exquisitesila-21` links.

Run everything from the repo root on the local machine (amazon.ae answers reliably from the
UAE connection). Never push a look that fails a check; stop and report instead.

## 0. Start clean

```
git pull --ff-only
git status            # must be clean apart from .claude/; if not, stop and report
```

## 1. Health-check the existing catalogue

```
python scripts/check_links.py
```

Read `content/generated/link-report.md`.
- **OOS / DEAD** on a look that has `image_url`s (the newer flat-lay looks): find a close
  replacement on amazon.ae (same colour, same kind of item, person-free main photo), update
  that piece's `amazon_url`, `asin`, `image_url` and `label` in `links.json`, then
  `python scripts/apply_real_products.py <outfit-id> --force` and
  `python scripts/build_real_collages.py <outfit-id>`.
- **OOS / DEAD** on an older look (hand-made collage, no `image_url`): don't change the link
  silently. List it in the final report so the owner can decide.
- **CHECK** (robot check): re-run `python scripts/check_links.py <outfit-id>` once later; if
  still inconclusive, mention it in the report.
- **LOW**: just mention it.

## 2. Choose this week's look

Read `links.json` (newest looks are first) so the new look doesn't repeat recent colours,
garments or themes. Use the season (UAE-based audience; northern-hemisphere fashion calendar)
and Pinterest trends: e.g. autumn knits, coquette bows, leopard, burgundy, denim, satin
skirts, modest layering, Ramadan/Eid edits in season, summer linen, holiday sparkle.

Rotate across categories so every board keeps getting pins: aim for roughly one **Modest**
look in every three or four weeks, and alternate **Casual** and **Fancy**. Seasons used by
the site: Spring, Summer, Autumn, Winter.

House style (matches the site's existing collages):
- One top + one bottom (or a dress as "top" with no bottom only if the layout is adjusted),
  plus 4–6 accessories: shoes, bag, jewellery, and optionally a lifestyle item (perfume,
  sunglasses, hair bow, watch, phone case).
- Feminine, trend-aware, wearable; colours that work together.

## 3. Source the products

```
python scripts/amazon_research.py search <name> "<query>"
python scripts/amazon_research.py gallery <ASIN> ...
python scripts/amazon_research.py verify <ASIN> ...
```

Open the generated `.jpg` contact sheets in `content/generated/research/` and judge by eye.
Every pick must pass all of these:
- **Main photo is person-free** (flat lay, ghost mannequin or product shot on white). This
  is what keeps the collage clean; most clothing listings show a model, so search widely
  (skirts, jeans, trousers, knits, cardigans and jackets are often shot flat).
  If a garment you really want only has on-model photos, `scripts/cut_garments.py` can lift
  it out, but it needs per-photo tuning; prefer a flat-shot alternative.
- `verify` shows **Add to Cart** and a real availability ("In Stock" or "Only N left").
- The **default colour variant** (the one the link opens) is the colour you want; check the
  `colour` field and the downloaded main photo, not just the search thumbnail.
- Sold as a normal Amazon.ae listing.
- Price sensible for the look.

## 4. Add the look to links.json

Insert the new outfit at the **top** of `outfits` (home page shows newest first):

```json
{
  "id": "<short-kebab>-look-01",
  "title": "<Title Case, 3-6 words, unique>",
  "slug": "<same as id>",
  "url_slug": "<slugified title: lowercase, & -> and, hyphens>",
  "published": "<YYYY-MM-DD today>",
  "description": "<one sentence listing the key pieces, ~200 chars>",
  "styling_note": "<3 sentences: why it works, how to wear it, where to wear it>",
  "collage_image": "assets/products/<folder>/collage.png",
  "categories": ["Casual|Fancy|Modest", "Spring|Summer|Autumn|Winter"],
  "pin": {
    "title": "<keyword-rich, <=100 chars, e.g. '... Outfit | Casual Fall Style'>",
    "description": "Tap to shop every piece (affiliate links). <what people search for + every key piece> <4-5 hashtags>  (always START with that exact tap-to-shop sentence; <=500 chars)"
  },
  "pieces": [
    {"slot": "<Top slot e.g. Sweater>", "label": "<Colour + material + item, as the listing really is>",
     "amazon_url": "https://www.amazon.ae/dp/<ASIN>?tag=exquisitesila-21",
     "asin": "<ASIN>", "image_url": "<main_image from verify>"}
  ],
  "collage": { ... see step 5 ... },
  "publish": true,
  "status": "publish"
}
```

Also schedule one **follow-up pin** for the look (Pinterest favours fresh pins, and this
spreads pins across the week: new looks go out Thursdays, follow-ups the following-but-one
Monday):

```json
"followup_pins": [
  {"date": "<published + 11 days, a Monday>",
   "title": "<a different angle: 'Outfit idea: …', 'How to style …', '<colour> + <colour> outfit for …'>",
   "description": "Tap to shop every piece (affiliate links). <fresh wording, different keywords> <4-5 different hashtags>"}
]
```

Before picking the date, check no other look already has a follow-up on that day; if one
does, use the next free day that week. The daily site build releases each pin on its date.

Rules:
- Labels and descriptions must match the actual listing (colour name, material, item type).
- `slot` names are single words (they become file names): Sweater, Jeans, Skirt, Bag, Earrings…
- `url_slug` must be new (not used by any other look). Never change an existing look's
  `url_slug`: live pins point at it.

## 5. Design the collage

`collage` keys (see the comment block in `scripts/build_real_collages.py`):
- `background`: one of `BACKGROUNDS` (`autumn_leaves`, `coquette_lace`, `vintage_parchment`).
  Don't reuse last week's. Roughly once a month add a **new** backdrop function to
  `BACKGROUNDS` in the same spirit as the site's older collages (decorative, textured: lace,
  florals, gingham, polka dots, marble with gold ornament, parchment with corner flourishes,
  stripes…), keeping the clothes readable on it.
- `stack`: top + bottom in one column at real proportions. Start from an existing look:
  clothes right `cx≈0.64-0.70`, or left `cx≈0.36`; `max_w 0.44-0.48`; `ratio` = bottom width
  vs top width (jeans/straight trousers ≈0.58, A-line/midi ≈0.70, flared maxi ≈0.80);
  `overlap` 0.05-0.13 so the top's hem covers the waistband with no gap.
- `boxes`: 4-6 accessory boxes in the other column, non-overlapping, inside the frame/border.
- `cutout`: `[250, 236, false]` for pale/pearly/cream products on white, `[242, 205, false]`
  for watches with white dials.
- `ink` / `wordmark`: wordmark colour and position in an empty corner.

Then:

```
python scripts/apply_real_products.py <outfit-id>
python scripts/build_real_collages.py <outfit-id>
```

This writes `collage.png` (used on the site) and `pin.png` (the Pinterest image: the same
collage with a "TAP TO SHOP THE LOOK" band underneath in the look's `ink` colour; the RSS
feeds use it automatically). Check the band text is readable on the chosen `ink`.

Open `assets/products/<folder>/collage.png` and look at it critically:
- Bottom garment is long and full-size relative to the top (never smaller than the top).
- Top overlaps the waistband with no gap; nothing overlaps an accessory; nothing crosses the
  border/frame.
- No white boxes, holes, halos or missing parts in cutouts (pale items: adjust `cutout`).
- It would look at home next to the site's existing collages.
Iterate on the numbers until it does.

## 6. Build, check, publish

```
python scripts/build_site.py
python scripts/check_links.py <outfit-id>     # must exit 0 (all OK/LOW)
```

Check `feeds/all.xml` contains the new look, then:

```
git add -A -- . ":!.claude"
git commit -m "Add weekly look: <title>"
git push origin main
```

GitHub Pages deploys in a few minutes; Pinterest picks the new feed item up within ~24h and
pins it to each board whose feed it appears in (all + its category feeds).

## 7. Report

Finish with a short report for the owner:
- The new look's title, page URL (`https://exquisite.silat.ae/looks/<url_slug>/`) and the
  collage path `assets/products/<folder>/collage.png`.
- Pieces with prices.
- Link-health results: anything replaced, anything that needs a decision, low stock.
- Anything that failed or was skipped.
