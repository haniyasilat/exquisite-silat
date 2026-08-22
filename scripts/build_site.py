"""Build the static site from links.json.

links.json is the single source of truth. This script generates:

  index.html                     home page
  <category>/index.html          one page per category (7)
  looks/<slug>/index.html        one page per outfit (16)
  assets/js/outfits.js           data for the legacy ?id= / ?cat= pages
  sitemap.xml, robots.txt

Run:  python scripts/build_site.py
"""

from __future__ import annotations

import html
import json
import re
import shutil
from datetime import date
from pathlib import Path
from string import Template

ROOT = Path(__file__).resolve().parent.parent
LINKS_FILE = ROOT / "links.json"

SITE_URL = "https://exquisite.silat.ae"
SITE_NAME = "Exquisite Silat"
TAGLINE = "Outfit collages with every piece linked"

# Order matters: this is the order hubs appear on the home page.
STYLE_CATEGORIES = ["Casual", "Fancy", "Modest"]
SEASON_CATEGORIES = ["Spring", "Summer", "Autumn", "Winter"]

# Per-category copy. `blurb` is the short line on the hub tile; `title` and
# `description` are what search engines and social cards actually show.
CATEGORY_COPY = {
  "Casual": {
    "blurb": "Everyday mixes",
    "title": "Casual Outfit Ideas — Everyday Looks, Every Piece Linked",
    "description": (
      "Casual outfit ideas for everyday wear — jeans, knits, maxi skirts and sneakers "
      "styled into complete looks. Shop each piece straight from the collage."
    ),
    "intro": (
      "Easy, repeatable casual outfits — the kind you can actually put on a Tuesday. "
      "Every collage below breaks down into individual pieces you can shop."
    ),
    "faq": [
      (
        "What's a good casual outfit idea for everyday wear?",
        "Start with a neutral base — jeans or a maxi skirt with a fitted top — then layer "
        "in one statement piece like a bold cardigan or jacket. Keep jewelry simple and let "
        "one accent color do the work.",
      ),
      (
        "How do I make a casual outfit look put-together?",
        "Stick to two or three colors, add one structured piece — a jacket, a belt, or a bag "
        "with clean lines — and repeat a metal tone across your jewelry and hardware.",
      ),
      (
        "What shoes work best with casual looks?",
        "Sneakers keep it relaxed; kitten heels or ankle boots dress it up slightly without "
        "losing the everyday feel.",
      ),
    ],
  },
  "Fancy": {
    "blurb": "Dresses & dressier",
    "title": "Dressy Outfit Ideas — Evening & Occasion Looks | Exquisite Silat",
    "description": (
      "Dressy outfit ideas for weddings, dinners and occasions — evening dresses, heels, "
      "clutches and jewellery styled into full looks with every piece linked."
    ),
    "intro": (
      "Occasion dressing without the guesswork — evening looks, brunch outfits and "
      "wedding-guest options, each one built piece by piece."
    ),
    "faq": [
      (
        "What's a good outfit idea for a dressy occasion?",
        "Lean on one elevated fabric — satin, lace, or a tiered maxi skirt — paired with "
        "polished accessories like pearl jewelry or a structured clutch.",
      ),
      (
        "How do I dress up a casual piece for an evening look?",
        "Swap sneakers for heels, trade a tote for a clutch, and add one metallic or pearl "
        "accent to lift the whole outfit.",
      ),
      (
        "What accessories complete a fancy outfit?",
        "A clutch, delicate jewelry, and a signature perfume finish an occasion look without "
        "overpowering it.",
      ),
    ],
  },
  "Modest": {
    "blurb": "Covered & elegant",
    "title": "Modest Outfit Ideas — Covered, Elegant & Shoppable",
    "description": (
      "Modest outfit ideas that stay covered without losing the styling — long sleeves, "
      "maxi skirts and layered pieces put together into complete, shoppable looks."
    ),
    "intro": (
      "Modest outfits built around longer hems, fuller sleeves and thoughtful layering — "
      "elegant first, covered by design."
    ),
    "faq": [
      (
        "What makes an outfit modest but still stylish?",
        "Longer hemlines, fuller sleeves, and layering — a cardigan over a top, or a maxi "
        "skirt instead of a mini — while still following current color and silhouette trends.",
      ),
      (
        "How do I layer a modest outfit without looking bulky?",
        "Choose one fitted layer and one looser layer, and keep the palette tonal so the "
        "silhouette reads as intentional, not accidental.",
      ),
      (
        "What are good modest outfit pieces to start with?",
        "A maxi skirt, a long cardigan, and a boat-neck top are an easy modest base you can "
        "restyle with different accessories each season.",
      ),
    ],
  },
  "Spring": {
    "blurb": "Light layers",
    "title": "Spring Outfit Ideas — Light Layers & Transitional Looks",
    "description": (
      "Spring outfit ideas built on light layers — cardigans, midi skirts and soft colour "
      "for transitional weather. Every piece in the collage is linked."
    ),
    "intro": "Light layers for the in-between weather, when one jacket decides the whole outfit.",
    "faq": [
      (
        "What's a good spring outfit idea?",
        "Light layers you can add or remove — a cropped cardigan over a fitted top — in "
        "soft colors like blush, cream, or pastel accents.",
      ),
      (
        "How do I transition my wardrobe into spring?",
        "Swap heavy knits for lighter cardigans, bring in pastel accessories, and add one "
        "warm-weather shoe like a block heel or a flat.",
      ),
    ],
  },
  "Summer": {
    "blurb": "Warm-weather looks",
    "title": "Summer Outfit Ideas — Warm Weather Looks, Every Piece Linked",
    "description": (
      "Summer outfit ideas for hot weather — maxi skirts, linen, sandals and breathable "
      "layers styled into complete looks you can shop piece by piece."
    ),
    "intro": "Warm-weather outfits that survive real heat — breathable fabrics, easy shapes, no fuss.",
    "faq": [
      (
        "What's a good summer outfit for hot weather?",
        "Breathable fabrics like linen or satin, a maxi skirt or wide-leg jeans, and sandals "
        "— keep layers minimal and let one accessory, like a tote or sunglasses, do the styling.",
      ),
      (
        "What shoes work best for summer outfits?",
        "Sandals, espadrilles, or kitten heels — anything open and breathable that still "
        "pairs with a dressier top if the day calls for it.",
      ),
    ],
  },
  "Autumn": {
    "blurb": "Cozy transitions",
    "title": "Autumn Outfit Ideas — Cozy Layered Looks for Fall",
    "description": (
      "Autumn outfit ideas with knitwear, plaid, boots and warm neutrals layered into "
      "complete fall looks. Shop each piece directly from the collage."
    ),
    "intro": "Layering season — plaid, knitwear and boots, in the warmer end of the palette.",
    "faq": [
      (
        "What's a good autumn outfit idea?",
        "Knitwear, plaid, and warm neutrals — layer a cardigan or bomber jacket over a "
        "simple top, and bring in boots and a structured bag.",
      ),
      (
        "How do I layer for autumn without overheating?",
        "Choose one heavier piece — a jacket or a chunky cardigan — and keep everything "
        "underneath lightweight, so you can remove a layer indoors.",
      ),
    ],
  },
  "Winter": {
    "blurb": "Layered warmth",
    "title": "Winter Outfit Ideas — Layered Looks That Stay Warm",
    "description": (
      "Winter outfit ideas that layer properly — coats, knits and boots put together into "
      "complete looks with every piece linked."
    ),
    "intro": "Cold-weather outfits that layer properly, so warmth isn't the thing you compromise on.",
    "faq": [
      (
        "What's a good winter outfit that stays warm?",
        "Proper layering — a base top, a mid layer like a sweater, and an outer coat — plus "
        "boots and accessories in rich, warm tones.",
      ),
      (
        "How do I keep a winter outfit from looking bulky?",
        "Stick to one silhouette per layer, fitted under looser or vice versa, and keep the "
        "palette tonal so the layers read as one look rather than several.",
      ),
    ],
  },
}

DISCLOSURE = (
  f"As an Amazon Associate, {SITE_NAME} earns from qualifying purchases. "
  "Links below are affiliate links."
)


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------


def slugify(text: str) -> str:
  text = text.lower().strip()
  text = text.replace("&", " and ")
  text = re.sub(r"[^\w\s-]", "", text)
  return re.sub(r"[-\s]+", "-", text).strip("-")


def esc(text: str) -> str:
  return html.escape(str(text or ""), quote=True)


def jsonld(data: dict) -> str:
  """Serialise JSON-LD so it can't break out of the <script> block."""
  raw = json.dumps(data, ensure_ascii=False, indent=2)
  raw = raw.replace("<", "\\u003c").replace(">", "\\u003e")
  return f'<script type="application/ld+json">\n{raw}\n</script>'


def clamp(text: str, limit: int = 155) -> str:
  text = " ".join(str(text or "").split())
  if len(text) <= limit:
    return text
  return text[: limit - 1].rsplit(" ", 1)[0] + "…"


def abs_url(path: str) -> str:
  path = str(path or "").split("?")[0].lstrip("/")
  return f"{SITE_URL}/{path}" if path else f"{SITE_URL}/"


# --------------------------------------------------------------------------
# page shell
# --------------------------------------------------------------------------

SHELL = Template(
  """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>$title</title>
  <meta name="description" content="$description" />
  <link rel="canonical" href="$canonical" />

  <meta property="og:type" content="$og_type" />
  <meta property="og:site_name" content="$site_name" />
  <meta property="og:title" content="$og_title" />
  <meta property="og:description" content="$description" />
  <meta property="og:url" content="$canonical" />
  <meta property="og:image" content="$image" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="$og_title" />
  <meta name="twitter:description" content="$description" />
  <meta name="twitter:image" content="$image" />

  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500&family=DM+Sans:wght@400;500;600&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="/assets/css/styles.css?v=4" />

  <link rel="icon" href="/assets/img/favicon.ico" sizes="any" />
  <link rel="icon" type="image/png" sizes="32x32" href="/assets/img/favicon32x32.png" />
  <link rel="icon" type="image/png" sizes="512x512" href="/assets/img/favicon512.png" />
  <link rel="apple-touch-icon" href="/assets/img/appletouchicon.png" />

$structured_data
</head>
<body>
  <header class="nav">
    <div class="container nav__inner">
      <a class="brand" href="/">Exquisite <em>Silat</em></a>
      <nav class="nav__links" id="navLinks" aria-label="Primary">
        <a href="/casual/">Casual</a>
        <a href="/fancy/">Fancy</a>
        <a href="/modest/">Modest</a>
        <a href="/summer/">Summer</a>
        <a href="/about.html">About</a>
      </nav>
      <button class="nav__toggle" id="navToggle" aria-label="Toggle menu" aria-expanded="false">
        <span></span><span></span><span></span>
      </button>
    </div>
  </header>

$body

  <footer class="footer">
    <div class="container">
      <nav class="footer__cats" aria-label="All categories">
$footer_cats
      </nav>
      <div class="footer__inner">
        <p>© $year $site_name. As an Amazon Associate we earn from qualifying purchases.</p>
        <p><a href="/about.html">About</a></p>
      </div>
    </div>
  </footer>

  <script src="/assets/js/main.js"></script>
</body>
</html>
"""
)


def footer_categories() -> str:
  links = [
    f'        <a href="/{slugify(c)}/">{esc(c)}</a>'
    for c in STYLE_CATEGORIES + SEASON_CATEGORIES
  ]
  return "\n".join(links)


def render_shell(
  *,
  title: str,
  description: str,
  canonical: str,
  body: str,
  image: str,
  og_type: str = "website",
  og_title: str | None = None,
  structured_data: str = "",
) -> str:
  return SHELL.substitute(
    title=esc(title),
    description=esc(clamp(description)),
    canonical=canonical,
    og_type=og_type,
    og_title=esc(og_title or title),
    image=image,
    site_name=SITE_NAME,
    structured_data=structured_data,
    body=body,
    footer_cats=footer_categories(),
    year=date.today().year,
  )


# --------------------------------------------------------------------------
# components
# --------------------------------------------------------------------------


def collage_img(outfit: dict, *, sizes: str, eager: bool = False) -> str:
  """Collage image, or the dashed placeholder when there's no image yet."""
  src = outfit.get("collage_image")
  if not src:
    return (
      '<div class="collage-frame__empty">'
      "<strong>Collage coming soon</strong>"
      "<span>Top · Bottom · Accessories · Shoes</span>"
      "</div>"
    )
  alt = f"{outfit['title']} — outfit collage"
  loading = 'loading="eager" fetchpriority="high"' if eager else 'loading="lazy"'
  return (
    f'<img src="/{esc(src.lstrip("/"))}" alt="{esc(alt)}" {loading} decoding="async" '
    f'sizes="{sizes}" width="682" height="1024" '
    f'data-pin-description="{esc(clamp(outfit["title"] + " — " + outfit.get("description", ""), 400))}" />'
  )


def outfit_card(outfit: dict, *, eager: bool = False) -> str:
  has_image = bool(outfit.get("collage_image"))
  frame_cls = "collage-frame collage-frame--has-image" if has_image else "collage-frame"
  return f"""
        <article class="outfit-card">
          <a class="outfit-card__link" href="/looks/{outfit['slug']}/">
            <div class="{frame_cls}">
              {collage_img(outfit, sizes="(max-width: 900px) 100vw, 33vw", eager=eager)}
            </div>
            <h3 class="outfit-card__title">{esc(outfit['title'])}</h3>
          </a>
          <p class="outfit-card__desc">{esc(clamp(outfit.get('description', ''), 120))}</p>
          <p class="outfit-card__tags">{
    " ".join(f'<a href="/{slugify(c)}/">{esc(c)}</a>' for c in outfit.get('categories', []))
  }</p>
        </article>"""


def hub_tile(cat: str, outfits: list[dict], *, count: int) -> str:
  """Category tile backed by a representative collage."""
  copy = CATEGORY_COPY[cat]
  hero = next((o for o in outfits if o.get("collage_image")), None)
  style = ""
  cls = "hub-card"
  if hero:
    cls += " hub-card--has-image"
    style = f' style="--tile-image: url(&quot;/{esc(hero["collage_image"].lstrip("/"))}&quot;)"'
  label = f"{count} look{'s' if count != 1 else ''}"
  return f"""          <a class="{cls}" href="/{slugify(cat)}/"{style}>
            <span class="hub-card__body">
              <span class="hub-card__name">{esc(cat)}</span>
              <span class="hub-card__meta">{esc(copy['blurb'])} · {label}</span>
            </span>
          </a>"""


def shop_list(outfit: dict) -> str:
  rows = []
  for piece in outfit.get("pieces", []):
    url = (piece.get("amazon_url") or "").strip()
    has_link = url.startswith("http")
    if has_link:
      link = (
        f'<a class="shop-link" href="{esc(url)}" target="_blank" '
        f'rel="sponsored nofollow noopener">View on Amazon →</a>'
      )
    else:
      link = '<span class="shop-link is-placeholder">Link coming soon</span>'
    rows.append(
      f"""          <li>
            <div>
              <span class="shop-slot">{esc(piece.get('slot', 'Item'))}</span>
              <span class="shop-label">{esc(piece.get('label', ''))}</span>
            </div>
            {link}
          </li>"""
    )
  return "\n".join(rows)


# --------------------------------------------------------------------------
# pages
# --------------------------------------------------------------------------


def build_home(outfits: list[dict], by_cat: dict[str, list[dict]]) -> str:
  featured = [o for o in outfits if o.get("collage_image")][:3]
  hero_images = "".join(
    f"""
          <a class="hero__tile" href="/looks/{o['slug']}/" aria-label="{esc(o['title'])}">
            {collage_img(o, sizes="(max-width: 900px) 40vw, 22vw", eager=(i == 0))}
          </a>"""
    for i, o in enumerate(featured)
  )

  style_tiles = "\n".join(
    hub_tile(c, by_cat.get(c, []), count=len(by_cat.get(c, []))) for c in STYLE_CATEGORIES
  )
  season_tiles = "\n".join(
    hub_tile(c, by_cat.get(c, []), count=len(by_cat.get(c, []))) for c in SEASON_CATEGORIES
  )
  latest = "\n".join(outfit_card(o) for o in outfits[:6])

  body = f"""  <main>
    <section class="hero hero--split">
      <div class="container hero__inner">
        <div class="hero__copy">
          <p class="hero__eyebrow">Outfit collages · shoppable looks</p>
          <h1>One look.<br />Every piece linked.</h1>
          <p class="hero__lead">
            Browse outfit collages by style or season — then shop each piece
            below the image when you're ready.
          </p>
          <p class="hero__actions">
            <a class="btn" href="/casual/">Browse looks</a>
            <a class="btn btn--ghost" href="/summer/">Shop by season</a>
          </p>
        </div>
        <div class="hero__gallery" aria-hidden="false">{hero_images}
        </div>
      </div>
    </section>

    <section class="section">
      <div class="container">
        <p class="section__label">Style</p>
        <h2 class="section__title">Pick a vibe</h2>
        <div class="hub-grid hub-grid--3">
{style_tiles}
        </div>
      </div>
    </section>

    <section class="section">
      <div class="container">
        <p class="section__label">Season</p>
        <h2 class="section__title">Shop by weather</h2>
        <div class="hub-grid">
{season_tiles}
        </div>
      </div>
    </section>

    <section class="section">
      <div class="container">
        <p class="section__label">Latest</p>
        <h2 class="section__title">Newest looks</h2>
        <div class="outfit-row">
{latest}
        </div>
      </div>
    </section>
  </main>"""

  data = [
    {
      "@context": "https://schema.org",
      "@type": "WebSite",
      "name": SITE_NAME,
      "url": f"{SITE_URL}/",
      "description": TAGLINE,
    },
    {
      "@context": "https://schema.org",
      "@type": "ItemList",
      "name": "Latest outfit collages",
      "itemListElement": [
        {
          "@type": "ListItem",
          "position": i + 1,
          "url": f"{SITE_URL}/looks/{o['slug']}/",
          "name": o["title"],
        }
        for i, o in enumerate(outfits[:6])
      ],
    },
  ]

  return render_shell(
    title=f"{SITE_NAME} — Outfit Collages with Every Piece Linked",
    description=(
      "Outfit collages for casual, dressy and modest looks across every season. "
      "See the whole outfit, then shop each piece individually."
    ),
    canonical=f"{SITE_URL}/",
    image=abs_url(featured[0]["collage_image"]) if featured else f"{SITE_URL}/assets/img/favicon512.png",
    body=body,
    structured_data="\n".join(jsonld(d) for d in data),
  )


def build_category(cat: str, outfits: list[dict]) -> str:
  copy = CATEGORY_COPY[cat]
  cards = "\n".join(outfit_card(o, eager=(i == 0)) for i, o in enumerate(outfits))
  hero = next((o for o in outfits if o.get("collage_image")), None)

  empty = (
    ""
    if outfits
    else '<p class="empty-note">New looks are being added to this hub — check back soon.</p>'
  )

  faq = copy.get("faq", [])
  faq_items = "\n".join(
    f"""          <details class="faq-item">
            <summary>{esc(q)}</summary>
            <p>{esc(a)}</p>
          </details>"""
    for q, a in faq
  )
  faq_block = (
    f"""
    <section class="section">
      <div class="container container--narrow">
        <p class="section__label">FAQ</p>
        <h2 class="section__title">{esc(cat)} outfit questions</h2>
        <div class="faq-list">
{faq_items}
        </div>
      </div>
    </section>"""
    if faq
    else ""
  )

  body = f"""  <main>
    <div class="container page-head">
      <nav class="crumbs" aria-label="Breadcrumb">
        <a href="/">Home</a> · <span>{esc(cat)}</span>
      </nav>
      <p class="hero__eyebrow">Browse</p>
      <h1>{esc(cat)} outfits</h1>
      <p class="page-head__lead">{esc(copy['intro'])}</p>
    </div>
    <section class="section">
      <div class="container">
        {empty}
        <div class="outfit-row">
{cards}
        </div>
      </div>
    </section>
{faq_block}
  </main>"""

  data = [
    {
      "@context": "https://schema.org",
      "@type": "CollectionPage",
      "name": f"{cat} outfits",
      "description": copy["description"],
      "url": f"{SITE_URL}/{slugify(cat)}/",
    },
    {
      "@context": "https://schema.org",
      "@type": "BreadcrumbList",
      "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE_URL}/"},
        {
          "@type": "ListItem",
          "position": 2,
          "name": cat,
          "item": f"{SITE_URL}/{slugify(cat)}/",
        },
      ],
    },
    {
      "@context": "https://schema.org",
      "@type": "ItemList",
      "name": f"{cat} outfit collages",
      "numberOfItems": len(outfits),
      "itemListElement": [
        {
          "@type": "ListItem",
          "position": i + 1,
          "url": f"{SITE_URL}/looks/{o['slug']}/",
          "name": o["title"],
        }
        for i, o in enumerate(outfits)
      ],
    },
  ]

  if faq:
    data.append(
      {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
          {
            "@type": "Question",
            "name": q,
            "acceptedAnswer": {"@type": "Answer", "text": a},
          }
          for q, a in faq
        ],
      }
    )

  return render_shell(
    title=copy["title"],
    description=copy["description"],
    canonical=f"{SITE_URL}/{slugify(cat)}/",
    image=abs_url(hero["collage_image"]) if hero else f"{SITE_URL}/assets/img/favicon512.png",
    body=body,
    structured_data="\n".join(jsonld(d) for d in data),
  )


def build_look(outfit: dict, related: list[dict]) -> str:
  cats = outfit.get("categories", [])
  has_image = bool(outfit.get("collage_image"))
  frame_cls = (
    "collage-frame collage-frame--large collage-frame--has-image"
    if has_image
    else "collage-frame collage-frame--large"
  )
  crumb_cats = " · ".join(
    f'<a href="/{slugify(c)}/">{esc(c)}</a>' for c in cats
  )
  related_cards = "\n".join(outfit_card(o) for o in related)
  related_block = (
    f"""
    <section class="section">
      <div class="container">
        <p class="section__label">More like this</p>
        <h2 class="section__title">You might also like</h2>
        <div class="outfit-row">
{related_cards}
        </div>
      </div>
    </section>"""
    if related
    else ""
  )

  pin_url = (
    f"https://pinterest.com/pin/create/button/?url={SITE_URL}/looks/{outfit['slug']}/"
    f"&media={abs_url(outfit['collage_image'])}"
    if has_image
    else ""
  )
  pin_btn = (
    f"""
          <a class="btn btn--pin" href="{esc(pin_url)}" target="_blank"
             rel="noopener nofollow" data-pin-do="none">Save to Pinterest</a>"""
    if pin_url
    else ""
  )

  styling_note = outfit.get("styling_note", "")
  styling_block = (
    f"""
      <div class="look-styling">
        <p class="section__label">Styling notes</p>
        <p>{esc(styling_note)}</p>
      </div>"""
    if styling_note
    else ""
  )

  body = f"""  <main class="container">
    <div class="look-hero">
      <nav class="crumbs" aria-label="Breadcrumb">
        <a href="/">Home</a> · {crumb_cats}
      </nav>
      <h1>{esc(outfit['title'])}</h1>
      <p>{esc(outfit.get('description', ''))}</p>
    </div>

    <div class="look-layout">
      <div class="{frame_cls}">
        {collage_img(outfit, sizes="(max-width: 860px) 100vw, 50vw", eager=True)}
      </div>

      <aside class="shop">
        <h2>Shop the look</h2>
        <p class="shop__intro">Every piece shown in the collage, linked below.</p>
        <p class="disclosure disclosure--top">{esc(DISCLOSURE)}</p>
        <ul class="shop-list">
{shop_list(outfit)}
        </ul>{pin_btn}
      </aside>
    </div>{styling_block}
  </main>
{related_block}"""

  products = [
    {
      "@type": "ListItem",
      "position": i + 1,
      "item": {
        "@type": "Product",
        "name": p.get("label") or p.get("slot", "Item"),
        "category": p.get("slot", ""),
        **(
          {"offers": {"@type": "Offer", "url": p["amazon_url"], "availability": "https://schema.org/InStock"}}
          if (p.get("amazon_url") or "").startswith("http")
          else {}
        ),
      },
    }
    for i, p in enumerate(outfit.get("pieces", []))
  ]

  data = [
    {
      "@context": "https://schema.org",
      "@type": "BreadcrumbList",
      "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE_URL}/"},
        *(
          [
            {
              "@type": "ListItem",
              "position": 2,
              "name": cats[0],
              "item": f"{SITE_URL}/{slugify(cats[0])}/",
            }
          ]
          if cats
          else []
        ),
        {
          "@type": "ListItem",
          "position": 3 if cats else 2,
          "name": outfit["title"],
          "item": f"{SITE_URL}/looks/{outfit['slug']}/",
        },
      ],
    },
    {
      "@context": "https://schema.org",
      "@type": "ItemList",
      "name": f"Shop the look — {outfit['title']}",
      "numberOfItems": len(products),
      "itemListElement": products,
    },
  ]

  return render_shell(
    title=f"{outfit['title']} — Shop the Look | {SITE_NAME}",
    og_title=outfit["title"],
    description=outfit.get("description", ""),
    canonical=f"{SITE_URL}/looks/{outfit['slug']}/",
    image=abs_url(outfit["collage_image"]) if has_image else f"{SITE_URL}/assets/img/favicon512.png",
    body=body,
    og_type="article",
    structured_data="\n".join(jsonld(d) for d in data),
  )


def build_static_page(*, slug: str, eyebrow: str, heading: str, title: str, description: str, paragraphs: list[str]) -> str:
  """About / disclosure — same shell, so nav, meta and footer stay in sync."""
  body_paras = "\n".join(f"      <p>{p}</p>" for p in paragraphs)
  body = f"""  <main class="container prose">
    <p class="hero__eyebrow">{esc(eyebrow)}</p>
    <h1>{esc(heading)}</h1>
{body_paras}
  </main>"""

  return render_shell(
    title=title,
    description=description,
    canonical=f"{SITE_URL}/{slug}",
    image=f"{SITE_URL}/assets/img/favicon512.png",
    body=body,
    structured_data=jsonld(
      {
        "@context": "https://schema.org",
        "@type": "WebPage",
        "name": heading,
        "description": description,
        "url": f"{SITE_URL}/{slug}",
      }
    ),
  )


# --------------------------------------------------------------------------
# generated data + crawl files
# --------------------------------------------------------------------------


def build_outfits_js(outfits: list[dict]) -> str:
  """Regenerate the data file the legacy ?id= / ?cat= pages still read."""
  payload = json.dumps(
    [
      {
        "id": o["id"],
        "slug": o["slug"],
        "title": o["title"],
        "description": o.get("description", ""),
        "categories": o.get("categories", []),
        "collage_image": o.get("collage_image", ""),
        "pieces": o.get("pieces", []),
      }
      for o in outfits
    ],
    ensure_ascii=False,
    indent=2,
  )
  return f"""// GENERATED by scripts/build_site.py — do not edit by hand.
// Source of truth is links.json. Run: python scripts/build_site.py

const OUTFITS = {payload};

function getOutfitById(id) {{
  return OUTFITS.find((o) => o.id === id || o.slug === id);
}}

function outfitsForCategory(cat) {{
  return OUTFITS.filter((o) =>
    o.categories.some((c) => c.toLowerCase() === String(cat).toLowerCase())
  );
}}
"""


def build_sitemap(outfits: list[dict], cats: list[str]) -> str:
  today = date.today().isoformat()
  urls = [(f"{SITE_URL}/", "1.0")]
  urls += [(f"{SITE_URL}/{slugify(c)}/", "0.8") for c in cats]
  urls += [(f"{SITE_URL}/looks/{o['slug']}/", "0.7") for o in outfits]
  urls += [(f"{SITE_URL}/about.html", "0.3")]

  entries = "\n".join(
    f"""  <url>
    <loc>{loc}</loc>
    <lastmod>{today}</lastmod>
    <priority>{pri}</priority>
  </url>"""
    for loc, pri in urls
  )
  return f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{entries}
</urlset>
"""


def build_robots() -> str:
  return f"""User-agent: *
Allow: /

# Legacy query-string pages — canonical versions live at /looks/ and /<category>/
Disallow: /look.html
Disallow: /hub.html

Sitemap: {SITE_URL}/sitemap.xml
"""


def build_redirect(kind: str) -> str:
  """Client-side redirect from the old ?id= / ?cat= URLs to the new paths."""
  if kind == "look":
    logic = """
      const id = params.get("id");
      const match = OUTFITS.find((o) => o.id === id || o.slug === id);
      location.replace(match ? "/looks/" + match.slug + "/" : "/");"""
  else:
    logic = """
      const cat = params.get("cat");
      const known = ["Casual","Fancy","Modest","Spring","Summer","Autumn","Winter"];
      const hit = known.find((c) => c.toLowerCase() === String(cat).toLowerCase());
      location.replace(hit ? "/" + hit.toLowerCase() + "/" : "/");"""

  return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="robots" content="noindex, follow" />
  <title>Redirecting… — {SITE_NAME}</title>
  <link rel="stylesheet" href="/assets/css/styles.css?v=4" />
</head>
<body>
  <main class="container" style="padding: 4rem 0">
    <p>Taking you to the new page… <a href="/">Go to the home page</a>.</p>
  </main>
  <script src="/assets/js/outfits.js"></script>
  <script>
    (function () {{
      const params = new URLSearchParams(location.search);{logic}
    }})();
  </script>
</body>
</html>
"""


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------


def main() -> None:
  data = json.loads(LINKS_FILE.read_text(encoding="utf-8"))
  outfits = [o for o in data.get("outfits", []) if o.get("publish", True)]

  seen: set[str] = set()
  for o in outfits:
    slug = slugify(o["title"])
    while slug in seen:
      slug = f"{slug}-2"
    seen.add(slug)
    o["slug"] = slug

  all_cats = STYLE_CATEGORIES + SEASON_CATEGORIES
  by_cat = {
    c: [o for o in outfits if c in o.get("categories", [])] for c in all_cats
  }

  written: list[str] = []

  def write(rel: str, content: str) -> None:
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    written.append(rel)

  write("index.html", build_home(outfits, by_cat))

  for cat in all_cats:
    write(f"{slugify(cat)}/index.html", build_category(cat, by_cat[cat]))

  # Wipe stale look folders so renamed titles don't leave orphans behind.
  looks_dir = ROOT / "looks"
  if looks_dir.exists():
    shutil.rmtree(looks_dir)

  for outfit in outfits:
    related = [
      o
      for o in outfits
      if o["id"] != outfit["id"]
      and set(o.get("categories", [])) & set(outfit.get("categories", []))
    ][:3]
    write(f"looks/{outfit['slug']}/index.html", build_look(outfit, related))

  write(
    "about.html",
    build_static_page(
      slug="about.html",
      eyebrow="About",
      heading=SITE_NAME,
      title=f"About — {SITE_NAME}",
      description=(
        "Exquisite Silat puts together outfit collages — top, bottom, accessories and "
        "shoes — and links every piece so you can shop the whole look."
      ),
      paragraphs=[
        "Welcome to Exquisite Silat — outfit collages and shoppable looks. Each post shows "
        "a full combination (top, bottom, accessories, shoes), then links each piece so you "
        "can shop the look.",
        "Browse by style — casual, dressy or modest — or by season, and every collage breaks "
        "down into the individual pieces underneath it.",
        "Some links are Amazon affiliate links. As an Amazon Associate we earn from "
        "qualifying purchases, at no extra cost to you. Prices and availability change — "
        "always check the retailer page before buying.",
      ],
    ),
  )

  write("assets/js/outfits.js", build_outfits_js(outfits))
  write("sitemap.xml", build_sitemap(outfits, all_cats))
  write("robots.txt", build_robots())
  write("look.html", build_redirect("look"))
  write("hub.html", build_redirect("hub"))

  print(f"Built {len(written)} files")
  print(f"  {len(outfits)} looks · {len(all_cats)} categories")
  for rel in written[:4]:
    print(f"  {rel}")
  print(f"  … and {len(written) - 4} more")


if __name__ == "__main__":
  main()
