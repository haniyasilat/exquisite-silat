# Exquisite Silat Outfit Blog — Implementation Plan

> **For agentic workers:** Execute inline in this session. Steps use checkbox syntax.

**Goal:** Ship a light beige + dark-ruby outfit collage blog on WordPress.com (`exquisitesilatdotblog`) with style/season hubs and placeholder shop-the-look posts, plus a matching local preview and outfit-first publish pipeline.

**Architecture:** Local HTML preview for instant viewing; `links.json` becomes outfit-first; `generate.py` builds collage + shop-slot HTML; WordPress.com gets theme/colors/categories/sample content via browser (API password empty on Free — browser + optional later API).

**Tech Stack:** WordPress.com Free, static HTML/CSS preview, Python generate/publish scripts, WordPress REST when credentials exist.

## Global Constraints

- Brand: Exquisite Silat
- Site: exquisitesilatdotblog.wordpress.com
- Colors: beige `#F5F0E8`, cream `#FAF7F2`, charcoal `#2A2422`, ruby `#7A1F2B`, muted `#6B635C`
- Hubs: Casual, Fancy, Modest, Spring, Summer, Autumn, Winter
- Empty Amazon URLs → “Add your Amazon link here”; empty collage → “Add your collage here”
- Do not commit unless user asks

---

### Task 1: Local outfit-blog preview (instant view)

**Files:**
- Modify: `index.html`, `assets/css/styles.css`, `assets/js/main.js`
- Create: hub pages under `preview/hubs/*.html` OR single-page hubs via hash/sections in `index.html` + `outfit.html` template

- [ ] Replace martial-arts landing with beige/ruby outfit home (brand, hub squares)
- [ ] Add sample outfit detail page with collage placeholder + shop slots
- [ ] Serve on localhost:8080 and verify visually

### Task 2: Outfit-first data + generator

**Files:**
- Modify: `links.json`, `scripts/generate.py`, `scripts/publish.py`, `.env.example`
- Modify: `content/pages/about.md`, `content/pages/disclosure.md`

- [ ] Rewrite `links.json` with sample placeholder outfits across hubs
- [ ] Rewrite generator for outfit posts + About/Disclosure; drop rosemary/product format
- [ ] Point publish default site to `exquisitesilatdotblog.wordpress.com`
- [ ] Run `python scripts/generate.py` and verify `content/generated/`

### Task 3: WordPress.com live setup (browser)

- [ ] Launch site (disable Coming Soon)
- [ ] Set title/tagline; apply clean theme + beige/ruby colors
- [ ] Create categories (hubs) and menu
- [ ] Create About + Disclosure pages
- [ ] Create sample outfit posts (publish) with generated HTML
- [ ] Homepage: hub navigation + latest outfits
- [ ] Open public URL for user to view

### Task 4: Wire credentials note

- [ ] Update README for outfit workflow and correct site hostname
- [ ] If app password available, try API publish; else document browser path
