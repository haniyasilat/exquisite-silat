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
| `looks/<slug>/index.html` | One page per outfit (16) |
| `about.html` | About page |
| `assets/js/outfits.js` | Data for the legacy `?id=` / `?cat=` redirects |
| `sitemap.xml`, `robots.txt` | Crawl files |
| `look.html`, `hub.html` | Redirect shims for old query-string URLs |

Slugs are derived from each outfit's `title`, so **renaming a title changes its
URL**. The `looks/` folder is wiped and rebuilt each run so renames don't leave
orphaned pages behind.

## Adding a look

1. Add an entry to the `outfits` array in `links.json` — `id`, `title`,
   `description`, `categories`, `collage_image`, and the `pieces` list.
2. Drop the collage into `assets/products/<look-name>/collage.png`.
3. Run `python scripts/build_site.py`.
4. Commit and push — GitHub Pages picks it up automatically.

Set `"publish": false` on an entry to keep it out of the build.

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

Colors: light beige + dark ruby red.
