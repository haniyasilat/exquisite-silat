"""Publish generated content to WordPress.com via REST API."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

from generate import generate_all
load_dotenv(ROOT / ".env")

WP_SITE = os.getenv("WP_SITE", "exquisitesilatdotblog.wordpress.com")
WP_USERNAME = os.getenv("WP_USERNAME", "")
WP_APP_PASSWORD = os.getenv("WP_APP_PASSWORD", "").replace(" ", "")

API_BASE = f"https://public-api.wordpress.com/rest/v1.1/sites/{WP_SITE}"


def check_credentials() -> None:
  if not WP_USERNAME or not WP_APP_PASSWORD:
    print(
      "\nMissing WordPress credentials.\n"
      "1. Copy .env.example to .env\n"
      "2. Create an Application Password at:\n"
      "   https://wordpress.com/me/security\n"
      "3. Fill in WP_USERNAME and WP_APP_PASSWORD\n"
    )
    sys.exit(1)


def wp_request(method: str, endpoint: str, **kwargs) -> dict:
  url = f"{API_BASE}{endpoint}"
  auth = (WP_USERNAME, WP_APP_PASSWORD)
  resp = requests.request(method, url, auth=auth, timeout=60, **kwargs)
  if not resp.ok:
    print(f"API error {resp.status_code}: {resp.text[:500]}")
    sys.exit(1)
  return resp.json()


def find_existing(slug: str, content_type: str = "post") -> dict | None:
  results = wp_request(
    "GET",
    f"/{content_type}s",
    params={"slug": slug, "number": 1, "status": "any"},
  )
  posts = results.get("posts", [])
  return posts[0] if posts else None


def publish_item(item: dict) -> None:
  content_type = "posts" if item["type"] == "post" else "pages"
  slug = item["slug"]
  existing = find_existing(slug, "post" if item["type"] == "post" else "page")

  payload = {
    "title": item["title"],
    "content": item["content"],
    "status": item.get("status", "draft"),
    "slug": slug,
  }

  if item["type"] == "post" and item.get("categories"):
    payload["categories"] = item["categories"]

  if existing:
    post_id = existing["ID"]
    wp_request("POST", f"/{content_type}/{post_id}", data=payload)
    print(f"  Updated {item['type']}: {item['title']} ({item.get('status', 'draft')})")
  else:
    wp_request("POST", f"/{content_type}/new", data=payload)
    print(f"  Created {item['type']}: {item['title']} ({item.get('status', 'draft')})")


def launch_check() -> None:
  """Warn if site still shows coming soon."""
  try:
    r = requests.get(f"https://{WP_SITE}", timeout=15)
    if "coming soon" in r.text.lower() or "bright idea" in r.text.lower():
      print(
        "\n⚠  Site may still be in 'Coming soon' mode.\n"
        "   Launch it: WordPress → Settings → General → disable Coming soon\n"
      )
  except requests.RequestException:
    pass


def main() -> None:
  check_credentials()
  launch_check()

  print("Generating content from links.json...")
  items = generate_all()
  print(f"Publishing {len(items)} items to {WP_SITE}...\n")

  for item in items:
    publish_item(item)

  print(f"\nDone. Visit https://{WP_SITE}")
  print("Next: add your Amazon affiliate links in links.json, then run again.")


if __name__ == "__main__":
  main()
