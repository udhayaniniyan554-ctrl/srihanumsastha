import httpx
import json
import re
import sys

base_url = "http://127.0.0.1:8080"
client = httpx.Client(base_url=base_url, timeout=5.0)

print("=== 1. Testing Core Pages ===")
for path in ["/index.html", "/category.html?cat=office", "/contact.html", "/styles.css", "/app.js", "/assets/logo.svg"]:
    r = client.get(path)
    assert r.status_code == 200, f"Failed to fetch {path}: {r.status_code}"
    print(f"[PASS] {path} -> 200 OK ({len(r.content)} bytes)")

print("\n=== 2. Testing Catalogue Dataset ===")
r = client.get("/assets/catalog.json")
assert r.status_code == 200
items = r.json()
print(f"Total products in catalog: {len(items)} (Expected: 228)")
assert len(items) == 228, f"Expected 228 items, got {len(items)}"

expected_counts = {
    "Office Chairs": 128,
    "Visitor Chairs": 48,
    "Lounge & Soft Seating": 24,
    "Dining Chairs": 21,
    "Stools & Additional Seating": 7
}

for cat, exp_count in expected_counts.items():
    cat_items = [i for i in items if i["category"] == cat]
    assert len(cat_items) == exp_count, f"{cat}: Expected {exp_count}, got {len(cat_items)}"
    assert cat_items[0]["code"] == "SHSE(1)", f"{cat}: First code is {cat_items[0]['code']}"
    assert cat_items[-1]["code"] == f"SHSE({exp_count})", f"{cat}: Last code is {cat_items[-1]['code']}"
    assert cat_items[0]["display_name"] == f"{cat} — SHSE(1)"
    assert cat_items[-1]["display_name"] == f"{cat} — SHSE({exp_count})"
    print(f"[PASS] {cat}: Exactly {len(cat_items)} items, numbered SHSE(1) to SHSE({exp_count})")

print("\n=== 3. Verification of Zero Model Name Leaks ===")
forbidden_words = [
    "ATLAS", "CASANOVA", "VIRGO", "LIBRA", "SCORPIO", "TAURUS", "BUTTERFLY", "JAZZ", "MATRIX",
    "VIBE", "MARVEL", "BREEZE", "ORION", "MYSTIC", "POSH", "BONAI", "METERRODE", "FLAIR",
    "OPTIMA", "CONTACT", "EROS", "HELIOS", "FLIP", "ADONIS", "FIDO", "ELANZO", "FILO",
    "LUCANO", "CAMRY", "IRIS", "WAVE", "DIPLOMET", "YLN", "GAMING CHAIR", "BUCKET CHAIR",
    "202", "SWING", "A815", "VOGUE", "ONYX", "AMAZE", "ZMA717", "FLOWER NETTED", "ISO NETTED",
    "NUNO", "CLAC", "GERMAN FLOWER", "COMFORT", "PARADISE", "R2BS14", "R2B", "RC55", "RC37", "RC36",
    "PEACOCK", "ALEX", "BOSTON", "ZARA", "SWAN", "KIWI", "STAR", "HEXA", "KNOLL", "BONNY", "KING",
    "ZETA", "AMAYRA", "LUV", "DAYTON", "TOLEDO", "WALTER", "SIAM", "STEFANO", "GEMINI", "SUNFLOWER",
    "LOUNGE DC", "LUXE", "PROMAX"
]

leak_count = 0
for it in items:
    public_str = f"{it['display_name']} {it['code']} {it['price_display']} {' '.join(o['variant'] for o in it.get('options', []))} {' '.join(it.get('features', []))}"
    for w in forbidden_words:
        if re.search(r'\b' + re.escape(w) + r'\b', public_str, re.IGNORECASE):
            print(f"[FAIL] Leak found in {it['display_name']}: {w}")
            leak_count += 1

assert leak_count == 0, f"Found {leak_count} leaks"
print("[PASS] Zero manufacturer or model name leaks across all 228 items!")

print("\n=== 4. Image Availability Test ===")
broken_images = 0
for it in items:
    img_r = client.get("/" + it["image"])
    if img_r.status_code != 200 or len(img_r.content) < 500:
        broken_images += 1
assert broken_images == 0, f"Found {broken_images} broken images"
print(f"[PASS] All {len(items)} images are accessible over HTTP!")

print("\n=== 5. Business Details in HTML ===")
index_html = client.get("/index.html").text
assert "Quality Seating for Every Space" in index_html
assert "Office Chairs — SHSE(1)" in index_html
assert "tel:9688727284" in index_html
assert "tel:8695706013" in index_html
assert "Call 9688727284" in index_html
assert "Call 8695706013" in index_html
assert "173, First Floor, KK Lane Street, Avinashi Road, Coimbatore" in index_html
assert "Prices may change. Please contact us to confirm current prices and availability." in index_html
print("[PASS] All business information, telephone numbers, and call buttons verified!")

print("\n🎉 ALL TESTS PASSED SUCCESSFULLY! THE WEBSITE IS 100% READY!")
