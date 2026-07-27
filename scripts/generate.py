"""Generate outfit collage posts and pages from links.json."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LINKS_FILE = ROOT / "links.json"
PAGES_DIR = ROOT / "content" / "pages"
GENERATED_DIR = ROOT / "content" / "generated"

BEIGE = "#F5F0E8"
CREAM = "#FAF7F2"
CHARCOAL = "#2A2422"
RUBY = "#7A1F2B"
MUTED = "#6B635C"


def slugify(text: str) -> str:
  text = text.lower().strip()
  text = re.sub(r"[^\w\s-]", "", text)
  return re.sub(r"[-\s]+", "-", text).strip("-")


def md_to_html(md: str) -> str:
  lines = md.strip().split("\n")
  html: list[str] = []
  in_list = False

  for line in lines:
    stripped = line.strip()
    if not stripped:
      if in_list:
        html.append("</ul>")
        in_list = False
      continue

    if stripped.startswith("## "):
      if in_list:
        html.append("</ul>")
        in_list = False
      html.append(f"<h2>{stripped[3:]}</h2>")
    elif stripped.startswith("# "):
      if in_list:
        html.append("</ul>")
        in_list = False
      html.append(f"<h1>{stripped[2:]}</h1>")
    elif stripped.startswith("- "):
      if not in_list:
        html.append("<ul>")
        in_list = True
      html.append(f"<li>{_inline(stripped[2:])}</li>")
    else:
      if in_list:
        html.append("</ul>")
        in_list = False
      html.append(f"<p>{_inline(stripped)}</p>")

  if in_list:
    html.append("</ul>")
  return "\n".join(html)


def _inline(text: str) -> str:
  text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
  text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
  text = re.sub(
    r"\[(.+?)\]\((.+?)\)",
    r'<a href="\2" target="_blank" rel="nofollow sponsored noopener">\1</a>',
    text,
  )
  return text


def collage_block(image_url: str) -> str:
  if image_url and image_url.startswith("http"):
    return (
      f'<figure style="margin:0 0 1.5rem;">'
      f'<img src="{image_url}" alt="Outfit collage" '
      f'style="width:100%;height:auto;display:block;" />'
      f"</figure>"
    )
  return f"""
<div style="margin:0 0 1.5rem;padding:3.5rem 1.5rem;text-align:center;
  background:{CREAM};border:1px dashed rgba(122,31,43,0.4);color:{MUTED};">
  <p style="margin:0 0 0.35rem;font-size:1.35rem;color:{RUBY};"><strong>Add your collage here</strong></p>
  <p style="margin:0;font-size:0.95rem;">Top · Bottom · Bags / belts / jewelry · Shoes</p>
</div>
"""


def shop_the_look(pieces: list[dict], site_name: str) -> str:
  rows: list[str] = []
  for piece in pieces:
    slot = piece.get("slot", "Item")
    label = piece.get("label") or "Add item name"
    url = (piece.get("amazon_url") or "").strip()
    if url.startswith("http"):
      link = (
        f'<a href="{url}" target="_blank" rel="nofollow sponsored noopener" '
        f'style="display:inline-block;padding:0.55rem 0.9rem;background:{RUBY};'
        f'color:#fff8f6;text-decoration:none;font-size:0.8rem;font-weight:600;">'
        f"View on Amazon →</a>"
      )
    else:
      link = (
        f'<span style="display:inline-block;padding:0.55rem 0.9rem;'
        f'border:1px dashed rgba(122,31,43,0.4);color:{MUTED};font-size:0.8rem;">'
        f"Add your Amazon link here</span>"
      )
    rows.append(
      f"""
<div style="display:flex;align-items:center;justify-content:space-between;gap:1rem;
  padding:0.95rem 0;border-top:1px solid rgba(42,36,34,0.12);">
  <div>
    <div style="font-size:0.72rem;font-weight:600;letter-spacing:0.12em;
      text-transform:uppercase;color:{RUBY};">{slot}</div>
    <div style="margin-top:0.2rem;color:{CHARCOAL};font-weight:500;">{label}</div>
  </div>
  <div>{link}</div>
</div>
"""
    )

  body = "\n".join(rows)
  return f"""
<div style="margin:1.75rem 0;padding:1.5rem 1.35rem;background:{CREAM};
  border:1px solid rgba(42,36,34,0.12);">
  <h2 style="margin:0 0 0.35rem;color:{CHARCOAL};">Shop the look</h2>
  <p style="margin:0 0 1rem;color:{MUTED};font-size:0.95rem;">
    Links for each piece shown in the collage.
  </p>
  {body}
  <p style="margin:1.25rem 0 0;font-size:0.82rem;color:{MUTED};">
    <em>Disclosure: As an Amazon Associate, {site_name} earns from qualifying purchases.</em>
  </p>
</div>
"""


def generate_outfit_post(outfit: dict, site_name: str) -> dict:
  title = outfit["title"]
  slug = outfit.get("slug") or outfit.get("id") or slugify(title)
  description = outfit.get("description") or "Add a short outfit description here."
  pieces = outfit.get("pieces") or []
  categories = outfit.get("categories") or []

  content = (
    collage_block(outfit.get("collage_image") or "")
    + f'<p style="color:{MUTED};">{description}</p>\n'
    + shop_the_look(pieces, site_name)
  )

  return {
    "type": "post",
    "title": title,
    "slug": slug,
    "content": content,
    "status": outfit.get("status", "draft"),
    "categories": categories,
  }


def generate_home_page(outfits: list[dict], site_name: str) -> dict:
  hubs = [
    ("Casual", "Everyday mixes"),
    ("Fancy", "Dresses & dressier"),
    ("Modest", "Covered & elegant"),
    ("Spring", "Light layers"),
    ("Summer", "Warm-weather looks"),
    ("Autumn", "Cozy transitions"),
    ("Winter", "Layered warmth"),
  ]
  cards = []
  for name, meta in hubs:
    cards.append(
      f"""
<a href="/category/{slugify(name)}/" style="display:block;padding:1.15rem 1.2rem;
  min-height:6.5rem;background:{CREAM};border:1px solid rgba(42,36,34,0.12);
  text-decoration:none;color:{CHARCOAL};">
  <div style="font-size:1.45rem;font-weight:600;">{name}</div>
  <div style="margin-top:0.35rem;font-size:0.85rem;color:{MUTED};">{meta}</div>
</a>
"""
    )

  samples = []
  for o in outfits[:3]:
    slug = o.get("slug") or o.get("id")
    samples.append(
      f'<li><a href="/{slug}/">{o["title"]}</a> '
      f'<span style="color:{MUTED};">— {", ".join(o.get("categories", []))}</span></li>'
    )

  content = f"""
<div style="background:{BEIGE};padding:0.5rem 0 2rem;">
  <p style="margin:0 0 0.5rem;font-size:0.75rem;font-weight:600;letter-spacing:0.16em;
    text-transform:uppercase;color:{RUBY};">Outfit collages · shoppable looks</p>
  <h1 style="margin:0;color:{CHARCOAL};">One look. Every piece linked.</h1>
  <p style="max-width:36rem;color:{MUTED};">
    Browse outfit collages by style or season — then shop each piece below the image.
  </p>
  <h2 style="margin:2rem 0 0.75rem;color:{CHARCOAL};">Browse hubs</h2>
  <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:0.75rem;">
    {"".join(cards)}
  </div>
  <h2 style="margin:2.5rem 0 0.75rem;color:{CHARCOAL};">Sample looks</h2>
  <ul>
    {"".join(samples) if samples else "<li>Looks coming soon.</li>"}
  </ul>
  <p style="font-size:0.85rem;color:{MUTED};">
    As an Amazon Associate, {site_name} earns from qualifying purchases.
  </p>
</div>
"""
  return {
    "type": "page",
    "title": "Home",
    "slug": "home",
    "content": content.strip(),
    "status": "publish",
  }


def load_links() -> dict:
  with open(LINKS_FILE, encoding="utf-8") as f:
    return json.load(f)


def generate_all() -> list[dict]:
  data = load_links()
  site_name = data.get("site_name") or "Exquisite Silat"
  outfits = data.get("outfits") or data.get("products") or []
  items: list[dict] = []

  for md_file in sorted(PAGES_DIR.glob("*.md")):
    slug = md_file.stem
    title = slug.replace("-", " ").title()
    if slug == "disclosure":
      title = "Affiliate Disclosure"
    raw = md_file.read_text(encoding="utf-8")
    items.append(
      {
        "type": "page",
        "title": title,
        "slug": slug,
        "content": md_to_html(raw),
        "status": "publish",
      }
    )

  items.append(generate_home_page(outfits, site_name))

  for outfit in outfits:
    # Support legacy product shape briefly
    if "amazon_affiliate_url" in outfit and "pieces" not in outfit:
      continue
    if outfit.get("publish", True):
      items.append(generate_outfit_post(outfit, site_name))

  GENERATED_DIR.mkdir(parents=True, exist_ok=True)
  out = GENERATED_DIR / "manifest.json"
  with open(out, "w", encoding="utf-8") as f:
    json.dump(items, f, indent=2)

  for item in items:
    (GENERATED_DIR / f"{item['slug']}.html").write_text(item["content"], encoding="utf-8")

  return items


if __name__ == "__main__":
  generated = generate_all()
  print(f"Generated {len(generated)} items in {GENERATED_DIR}")
