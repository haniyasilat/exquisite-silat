# Exquisite Silat — Outfit Collage Blog Design

**Date:** 2026-07-22  
**Site:** https://exquisitesilatdotblog.wordpress.com  
**Status:** Approved for implementation (pending user review of this spec)

## Goal

Build **Exquisite Silat** as a clean, light fashion blog where each post is one **outfit collage** (top, bottom, accessories, shoes) with **Amazon affiliate links** for every piece shown. Readers browse by **style hubs** and **season hubs**. First ship uses placeholders so content can be filled later.

## Audience & content

- Mix of looks: casual, fancy/dresses, modest, plus seasonal outfits.
- Brand name stays **Exquisite Silat**.
- Tone: simple, visual, Pinterest-friendly — short copy, big collage, clear shop links.

## Visual direction

| Token | Value | Use |
|-------|--------|-----|
| Background | Light beige (`#F5F0E8`) | Page / section backgrounds |
| Surface | Soft cream (`#FAF7F2`) | Cards, shop boxes |
| Text | Charcoal (`#2A2422`) | Body and headings |
| Accent | Dark ruby red (`#7A1F2B`) | Buttons, hub labels, link accents, thin rules |
| Muted text | Warm gray (`#6B635C`) | Descriptions, captions |

Layout rules:
- Clean light fashion layout: lots of beige/whitespace, minimal chrome.
- No dark martial-arts look from the local Silat preview.
- No card-heavy dashboard feel on the homepage — one clear composition: brand + hub grid.
- Outfit grid on hub pages: simple rows/columns of collage + title; detail on the post.

## Information architecture

### Homepage
- Site title: **Exquisite Silat**
- Short tagline (placeholder OK), e.g. *Outfit collages & shoppable looks*
- Hub squares/cards linking to category archives:
  - **Style:** Casual · Fancy · Modest  
  - **Season:** Spring · Summer · Autumn · Winter  

### Hub pages (WordPress categories)
Clicking a hub shows a long grid/list of outfits in that category.  
An outfit may belong to **multiple** hubs (e.g. Modest + Summer).

### Outfit post (single)
1. **Collage image** — one image combining top, bottom, accessories (bags, belts, jewelry), and shoes.  
   Placeholder until filled: “Add your collage here”.
2. **Short description** — 1–2 sentences. Placeholder copy allowed.
3. **Shop the look** — labeled slots for each piece with Amazon links:
   - Top  
   - Bottom  
   - Dress (optional; used when the look is a dress instead of top+bottom)  
   - Shoes  
   - Bag  
   - Jewelry  
   - Belt  
   - Other (optional)

   Empty slots use: **Add your Amazon link here** (non-clickable or `#` until a real URL is set).

### Static pages
- **About** — short brand intro for Exquisite Silat as an outfit inspiration blog.
- **Affiliate Disclosure** — Amazon Associates disclosure.

### Out of scope (for later)
- Real filter “tabs” UI on a single page (hubs via categories for now).
- Custom domain / paid WordPress plan features.
- Auto-generating collages from product images.

## Data model (`links.json` → outfit-first)

Replace product-centric entries with **outfit** entries:

```json
{
  "site_name": "Exquisite Silat",
  "outfits": [
    {
      "id": "sample-summer-casual-01",
      "title": "Sample Summer Casual Look",
      "slug": "sample-summer-casual-01",
      "description": "Add a short outfit description here.",
      "collage_image": "",
      "categories": ["Casual", "Summer"],
      "pieces": [
        { "slot": "Top", "label": "Add item name", "amazon_url": "" },
        { "slot": "Bottom", "label": "Add item name", "amazon_url": "" },
        { "slot": "Shoes", "label": "Add item name", "amazon_url": "" },
        { "slot": "Bag", "label": "Add item name", "amazon_url": "" },
        { "slot": "Jewelry", "label": "Add item name", "amazon_url": "" },
        { "slot": "Belt", "label": "Add item name", "amazon_url": "" }
      ],
      "publish": true,
      "status": "draft"
    }
  ]
}
```

Rules:
- Empty `collage_image` → publish with a clear image placeholder in HTML.
- Empty `amazon_url` → show “Add your Amazon link here” for that slot (do not invent URLs).
- `categories` map to WordPress category names listed above.
- Ship **several sample placeholder outfits** across different hubs so the layout is visible.

## Generator & publisher

Adapt existing scripts:

| Piece | Change |
|-------|--------|
| `scripts/generate.py` | Build outfit post HTML (collage + description + shop-the-look). Update site name to Exquisite Silat. Generate About + Disclosure. Emit beige/ruby-friendly inline styles suitable for WordPress.com. |
| `scripts/publish.py` | Point default `WP_SITE` to `exquisitesilatdotblog.wordpress.com`. Create/assign categories. Publish posts/pages via REST API (draft by default). |
| `links.json` | Outfit-first schema as above. |
| `.env` / `.env.example` | Update site hostname; keep app password flow. |

Affiliate link markup: `rel="nofollow sponsored noopener"`, `target="_blank"`.

## WordPress.com theme setup

Apply on the live site (browser or Appearance settings):

1. Launch site (turn off Coming Soon).
2. Theme: clean blog theme available on Free plan (prefer a minimal/block theme such as **Twenty Twenty-Four** or **Retrospect** if available) customized to beige + ruby.
3. **Settings → General:** title Exquisite Silat; tagline as above.
4. **Settings → Reading:** latest posts (or a static home that embeds the hub grid if using the site editor).
5. Create categories for all hubs.
6. Menu: Home, style hubs, season hubs, About, Disclosure.
7. Colors / buttons / links set to the palette above as far as the free theme allows; post HTML carries shop-block styling so outfit posts stay on-brand even if theme options are limited.

## Success criteria

- Homepage shows beige/ruby brand and clickable hub squares.
- Each hub lists outfits (including placeholders).
- Each outfit post shows collage placeholder, short description, and shop slots with “Add your Amazon link here” where empty.
- `python scripts/publish.py` can push sample outfits + About + Disclosure to `exquisitesilatdotblog.wordpress.com`.
- User can later fill collage URLs and Amazon links in `links.json` and republish.

## Non-goals

- Matching the dark gold local Silat martial-arts landing page.
- Wellness/rosemary-oil product post format from the previous Remodot Vision content.
- Paid theme marketplace purchases unless free options fail.
