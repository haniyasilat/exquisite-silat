# Exquisite Silat — Outfit Collage Blog

Outfit collages with shoppable Amazon links. Browse by style (Casual / Fancy / Modest) and season.

Live at **https://exquisite.silat.ae**

## How this site is built

`links.json` is the **single source of truth**. Everything else is generated —
don't hand-edit generated files, they get overwritten.

```bash
python scripts/build_site.py
```

That reads `links.json` and writes:

| Output | What it is |
|--------|------------|
| `index.html` | Home — split hero, category tiles, latest looks |
| `<category>/index.html` | One page per category (7) |
| `looks/<slug>/index.html` | One page per outfit |
| `about.html` | About page |
| `rss/all.xml`, `rss/<category>.xml` | RSS for Pinterest auto-publish |
| `assets/js/outfits.js` | Data for the legacy `?id=` / `?cat=` redirects |
| `sitemap.xml`, `robots.txt` | Crawl files |
| `look.html`, `hub.html` | Redirect shims for old query-string URLs |

A look's URL is its `url_slug` when set; otherwise it's derived from the `title`
(older looks), so **renaming such a title changes its URL**. Newer looks pin
`url_slug` so pins keep working. The `looks/` folder is wiped and rebuilt each
run so renames don't leave orphaned pages behind.

## Adding a look

New looks are made weekly by a scheduled task that follows
[`docs/weekly-look-playbook.md`](docs/weekly-look-playbook.md). By hand, the
same pipeline is:

```bash
python scripts/amazon_research.py search <name> "<query>"   # find products (contact sheets)
python scripts/amazon_research.py verify <ASIN> ...          # live check + main photo
# add the outfit (pieces with asin + image_url, collage layout, url_slug, published, pin) to links.json
python scripts/apply_real_products.py <outfit-id>            # download product photos + thumbnails
python scripts/build_real_collages.py <outfit-id>            # render the collage
python scripts/build_site.py
python scripts/check_links.py <outfit-id>                    # every link buyable?
```

Then commit and push; GitHub Pages deploys automatically.

Set `"publish": false` on an entry to keep it out of the build.

## Pinterest (RSS auto-publish)

Looks with a `published` date appear in the RSS feeds (`pin.title` /
`pin.description` become the pin text, the collage the pin image, and the link
carries `utm_source=pinterest`). One-time setup in a Pinterest **business**
account with `exquisite.silat.ae` claimed: *Create → Create Pins in bulk →
Auto-publish → Connect RSS feed*, once per board, e.g.

| Feed | Board |
|------|-------|
| `https://exquisite.silat.ae/rss/autumn.xml` | Autumn Outfits |
| `https://exquisite.silat.ae/rss/fancy.xml` | Evening & Dinner Outfits |
| `https://exquisite.silat.ae/rss/modest.xml` | Modest Fashion |
| `https://exquisite.silat.ae/rss/all.xml` | an "All looks" board |

Pinterest checks feeds daily and pins new items within ~24h.

**Scheduling:** the feeds are the pin schedule. A look's first pin appears on its
`published` date and each `followup_pins` entry (`date`, optional `title` /
`description`, uses the look's `pin.png`) on its own date. The site is built and
deployed by GitHub Actions (`.github/workflows/pages.yml`) on every push and every
morning at 08:00 UAE, so scheduled pins go out on their day even if no one pushes.
Pages must be set to *Settings → Pages → Source: GitHub Actions*.

To see Pinterest sales separately in Amazon Associates, create a second
tracking ID there and put it in `links.json` → `settings.pinterest_amazon_tag`;
look pages then swap the tag for visitors arriving from Pinterest.

## Link health

`python scripts/check_links.py` checks every product link and writes
`content/generated/link-report.md` (OOS/DEAD links exit non-zero). The weekly
task runs it before adding a new look.

## Local preview

```bash
python -m http.server 8080
```

Open http://localhost:8080/

## SEO notes

Every generated page carries a unique `<title>`, meta description, canonical
URL, Open Graph and Twitter card tags, and JSON-LD (`BreadcrumbList` +
`ItemList` on looks, `CollectionPage` on categories).

Affiliate links are emitted with `rel="sponsored nofollow noopener"` and the
Amazon Associates disclosure renders directly above the product list on every
look page — both are required by the Associates Operating Agreement, so leave
them in place.

Category copy (page titles, descriptions, intro text) lives in `CATEGORY_COPY`
near the top of `scripts/build_site.py`.

## Other scripts

`scripts/generate.py` and `scripts/make_wxr.py` are a separate WordPress export
pipeline that also reads `links.json`. They're unrelated to the static site.

`scripts/cut_garments.py` lifts a garment off an on-model product photo
(OpenCV GrabCut) for the rare piece that has no person-free photo.

Colors: light beige + dark ruby red.
