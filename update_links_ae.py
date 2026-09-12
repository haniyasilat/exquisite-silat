import json, pathlib, sys

# Paths
PROJECT_ROOT = pathlib.Path(r"C:/Users/cassi/Projects/exquisiteSilat")
LINKS_PATH = PROJECT_ROOT / "links.json"
AE_LINKS_PATH = pathlib.Path(r"C:/Users/cassi/.gemini/antigravity/brain/2d423166-4cf2-4f07-a0f2-e698539add69/scratch/ae_links.json")

# Load data
with open(LINKS_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

with open(AE_LINKS_PATH, "r", encoding="utf-8") as f:
    ae_links = json.load(f)

# Mapping of outfit id to piece keys in ae_links
outfit_piece_map = {
    "cozy-autumn-coffee-look-01": [
        "sweater", "trousers", "suede_bag", "clogs", "vintage_watch", "gold_hoops", "sunglasses"
    ],
    "quiet-luxury-summer-look-01": [
        "vest", "satin_skirt", "kitten_heels", "woven_clutch", "drop_earrings", "gold_cuff", "snake_necklace"
    ],
    "modest-pastel-spring-look-01": [
        "bow_blouse", "pleated_skirt", "slingback_heels", "trapeze_bag", "pearl_earrings", "gold_bangles", "hijab_scarf"
    ]
}

# Update URLs for the three new outfits
for outfit in data.get("outfits", []):
    oid = outfit.get("id")
    if oid in outfit_piece_map:
        pieces = outfit.get("pieces", [])
        keys = outfit_piece_map[oid]
        for piece, key in zip(pieces, keys):
            if key in ae_links:
                piece["amazon_url"] = ae_links[key]
            else:
                print(f"Warning: missing ae link for {key}", file=sys.stderr)

# Write back the updated links.json
with open(LINKS_PATH, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
print("links.json updated with Amazon.ae URLs for the new outfits.")

