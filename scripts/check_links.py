"""Check every product link on the site still leads to a buyable Amazon product.

    python scripts/check_links.py                  # all published looks
    python scripts/check_links.py <outfit-id> ...  # just those looks

For each piece it follows the link (including amazon short links) and reads the product
page: title, availability, Add to Cart, affiliate tag. Statuses:

    OK     buyable (or an add-to-cart link, which works but whose stock can't be read)
    LOW    buyable, but "only N left"
    OOS    no Add to Cart / currently unavailable  -> replace the product
    DEAD   page gone or not a product page          -> replace the product
    CHECK  Amazon served a robot check or the fetch failed; re-run later

Writes content/generated/link-report.md and exits 1 if anything is OOS or DEAD, so the
weekly task knows to act. Amazon.ae answers reliably from a UAE connection; run it locally.
"""

import html
import json
import pathlib
import re
import sys
import time
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
LINKS_JSON = ROOT / "links.json"
REPORT = ROOT / "content" / "generated" / "link-report.md"
TAG = "tag=exquisitesila-21"

UA = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/128.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}


def fetch(url: str):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.geturl(), r.read().decode("utf-8", "replace")


def text(fragment: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", fragment))).strip()


def check(url: str) -> dict:
    res = {"url": url}
    for attempt in range(3):
        try:
            final, page = fetch(url)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return {**res, "status": "DEAD", "note": "HTTP 404"}
            res.update(status="CHECK", note=f"HTTP {e.code}")
            time.sleep(4 * (attempt + 1))
            continue
        except Exception as e:  # network hiccup
            res.update(status="CHECK", note=str(e)[:80])
            time.sleep(4 * (attempt + 1))
            continue

        if "/cart/" in final or "/gp/aws/cart/" in final:
            # an add-to-cart link: it drops the item straight into the cart, which is a
            # working purchase path, but the product page (and stock) can't be read here
            return {**res, "status": "OK", "note": "add-to-cart link (stock not checked)", "final": final}

        title = re.search(r'id="productTitle"[^>]*>\s*(.*?)\s*</span>', page, re.S)
        if not title:
            if "captcha" in page.lower() or "robot" in page.lower()[:20000]:
                res.update(status="CHECK", note="robot check")
                time.sleep(6 * (attempt + 1))
                continue
            return {**res, "status": "DEAD", "note": "not a product page", "final": final}

        av = re.search(r'<div id="availability".*?</div>', page, re.S)
        availability = text(av.group(0))[:80] if av else ""
        availability = availability.split("{")[0].strip()
        cart = 'id="add-to-cart-button"' in page or 'name="submit.add-to-cart"' in page
        asin = re.search(r"/dp/([A-Z0-9]{10})", final) or re.search(r'name="ASIN" value="([A-Z0-9]{10})"', page)
        res.update(
            title=text(title.group(1))[:90],
            availability=availability,
            asin=asin.group(1) if asin else "",
            final=final,
        )
        if not cart or "unavailable" in availability.lower():
            res.update(status="OOS", note=availability or "no Add to Cart")
        elif re.search(r"only \d+ left", availability, re.I):
            res.update(status="LOW", note=availability)
        else:
            res.update(status="OK", note=availability)
        if "amazon.ae/dp/" in url and TAG not in url:
            res["note"] = (res["note"] + " | missing affiliate tag").strip(" |")
        return res
    return res


def main() -> int:
    only = set(sys.argv[1:])
    data = json.loads(LINKS_JSON.read_text(encoding="utf-8"))
    rows = []
    for outfit in data["outfits"]:
        if not outfit.get("publish", True) or (only and outfit["id"] not in only):
            continue
        for piece in outfit["pieces"]:
            url = (piece.get("amazon_url") or "").strip()
            if not url.startswith("http"):
                continue
            r = check(url)
            r.update(look=outfit["title"], look_id=outfit["id"], slot=piece["slot"], label=piece.get("label", ""))
            rows.append(r)
            print(f"{r['status']:5} {outfit['id'][:30]:30} {piece['slot']:10} {r.get('note', '')[:60]}")
            sys.stdout.flush()
            time.sleep(1.2)

    bad = [r for r in rows if r["status"] in ("OOS", "DEAD")]
    low = [r for r in rows if r["status"] == "LOW"]
    unsure = [r for r in rows if r["status"] == "CHECK"]
    lines = [
        "# Product link report",
        "",
        f"{len(rows)} links checked: {len(rows) - len(bad) - len(low) - len(unsure)} OK, "
        f"{len(low)} low stock, {len(bad)} need replacing, {len(unsure)} inconclusive.",
        "",
        "| Status | Look | Slot | Product | Note |",
        "|---|---|---|---|---|",
    ]
    order = {"DEAD": 0, "OOS": 1, "CHECK": 2, "LOW": 3, "OK": 4}
    for r in sorted(rows, key=lambda r: order[r["status"]]):
        lines.append(f"| {r['status']} | {r['look']} | {r['slot']} | {r.get('title') or r['url']} | {r.get('note', '')} |")
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\n{lines[2]}\nReport: {REPORT.relative_to(ROOT)}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
