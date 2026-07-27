"""Build a WordPress WXR import file from generated outfit content."""

from __future__ import annotations

import html
from datetime import datetime, timezone
from pathlib import Path

from generate import generate_all, slugify

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "content" / "generated" / "exquisite-silat-import.xml"


def cdata(s: str) -> str:
  return "<![CDATA[" + s.replace("]]>", "]]]]><![CDATA[>") + "]]>"


def main() -> None:
  items = generate_all()
  now = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")
  local = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  gmt = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
  cats = ["Casual", "Fancy", "Modest", "Spring", "Summer", "Autumn", "Winter"]

  parts: list[str] = []
  parts.append(
    f"""<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0"
  xmlns:excerpt="http://wordpress.org/export/1.2/excerpt/"
  xmlns:content="http://purl.org/rss/1.0/modules/content/"
  xmlns:wfw="http://wellformedweb.org/CommentAPI/"
  xmlns:dc="http://purl.org/dc/elements/1.1/"
  xmlns:wp="http://wordpress.org/export/1.2/">
<channel>
<title>Exquisite Silat</title>
<link>https://exquisitesilatdotblog.wordpress.com</link>
<description>Outfit collages &amp; shoppable looks</description>
<pubDate>{now}</pubDate>
<language>en-US</language>
<wp:wxr_version>1.2</wp:wxr_version>
<wp:base_site_url>https://exquisitesilatdotblog.wordpress.com</wp:base_site_url>
<wp:base_blog_url>https://exquisitesilatdotblog.wordpress.com</wp:base_blog_url>
"""
  )

  for i, name in enumerate(cats, start=2):
    parts.append(
      f"""
<wp:category>
  <wp:term_id>{i}</wp:term_id>
  <wp:category_nicename>{slugify(name)}</wp:category_nicename>
  <wp:category_parent></wp:category_parent>
  <wp:cat_name>{cdata(name)}</wp:cat_name>
</wp:category>
"""
    )

  post_id = 100
  for item in items:
    post_id += 1
    post_type = "page" if item["type"] == "page" else "post"
    cats_xml = ""
    for c in item.get("categories") or []:
      cats_xml += (
        f'<category domain="category" nicename="{slugify(c)}">'
        f"{cdata(c)}</category>\n"
      )
    parts.append(
      f"""
<item>
  <title>{html.escape(item["title"])}</title>
  <link>https://exquisitesilatdotblog.wordpress.com/{item["slug"]}/</link>
  <pubDate>{now}</pubDate>
  <dc:creator>{cdata("hnsilat")}</dc:creator>
  <guid isPermaLink="false">https://exquisitesilatdotblog.wordpress.com/?p={post_id}</guid>
  <description></description>
  <content:encoded>{cdata(item["content"])}</content:encoded>
  <excerpt:encoded><![CDATA[]]></excerpt:encoded>
  <wp:post_id>{post_id}</wp:post_id>
  <wp:post_date>{local}</wp:post_date>
  <wp:post_date_gmt>{gmt}</wp:post_date_gmt>
  <wp:post_name>{item["slug"]}</wp:post_name>
  <wp:status>publish</wp:status>
  <wp:post_type>{post_type}</wp:post_type>
  <wp:post_parent>0</wp:post_parent>
  <wp:menu_order>0</wp:menu_order>
  <wp:is_sticky>0</wp:is_sticky>
  {cats_xml}
</item>
"""
    )

  parts.append("</channel></rss>")
  OUT.write_text("".join(parts), encoding="utf-8")
  print(f"Wrote {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
  main()
