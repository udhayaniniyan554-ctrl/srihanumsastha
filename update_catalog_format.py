import json
import os
import re

PROJECT_DIR = r"C:\Users\user\.gemini\antigravity\scratch\srihanumsastha-catalogue"
CATALOG_PATH = os.path.join(PROJECT_DIR, "assets", "catalog.json")

CAT_PREFIX = {
    "Office Chairs": "OFFICE CHAIRS",
    "Visitor Chairs": "VISITOR CHAIRS",
    "Lounge & Soft Seating": "LOUNGE CHAIRS",
    "Dining Chairs": "DINING CHAIRS",
    "Stools & Additional Seating": "STOOLS"
}

def update_catalog():
    with open(CATALOG_PATH, "r", encoding="utf-8") as f:
        catalog = json.load(f)

    print(f"Loaded {len(catalog)} items from {CATALOG_PATH}")

    updated_count = 0
    for p in catalog:
        cat = p.get("category", "")
        prefix = CAT_PREFIX.get(cat, cat.upper())
        code_num = p.get("code_number", 1)

        # Standardized code: e.g. "SHSE 1", "SHSE 2"
        new_code = f"SHSE {code_num}"
        # Required format: category name first, 2 consistent spaces, genuine model code
        new_display_name = f"{prefix}  {new_code}"

        p["code"] = new_code
        p["display_name"] = new_display_name
        p["name"] = new_display_name

        # Ensure search_keywords includes all relevant search tokens
        internal_model = p.get("_internal_model", "")
        p["search_keywords"] = f"{new_display_name} {new_code} SHSE({code_num}) SHSE{code_num} {internal_model} {cat}".strip()

        updated_count += 1

    with open(CATALOG_PATH, "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)

    print(f"Successfully updated {updated_count} items in {CATALOG_PATH}")

    # Print representative samples
    for cat, prefix in CAT_PREFIX.items():
        sample = next(p for p in catalog if p["category"] == cat)
        print(f"  [{cat}] -> code='{sample['code']}', display_name='{sample['display_name']}'")

if __name__ == "__main__":
    update_catalog()
