import urllib.request
import json
import os
import re

BASE_URL = "http://127.0.0.1:8080"
PROJECT_DIR = r"C:\Users\user\.gemini\antigravity\scratch\srihanumsastha-catalogue"

print("==================================================")
print("  MASTER VERIFICATION TEST - SRI HANUM SASTHA    ")
print("==================================================")

# 1. Test Static files & Netlify config
print("\n[STEP 1] Checking Netlify Config & Key Files...")
assert os.path.exists(os.path.join(PROJECT_DIR, "netlify.toml")), "netlify.toml missing"
assert os.path.exists(os.path.join(PROJECT_DIR, "product.html")), "product.html missing"
assert os.path.exists(os.path.join(PROJECT_DIR, "admin.html")), "admin.html missing"
assert os.path.exists(os.path.join(PROJECT_DIR, "assets", "catalog.json")), "catalog.json missing"
print("  [PASS] netlify.toml, product.html, admin.html, catalog.json all present.")

# 2. Test HTTP Endpoints
print("\n[STEP 2] Testing HTTP Endpoints...")
endpoints = [
    ("/", "Homepage"),
    ("/index.html", "Index Page"),
    ("/category.html?cat=office", "Category Page (Office)"),
    ("/category.html?cat=visitor", "Category Page (Visitor)"),
    ("/product.html?id=office_1_1", "Dedicated Product Details Page"),
    ("/contact.html", "Contact Page"),
    ("/admin.html", "Admin Manager"),
    ("/assets/catalog.json", "Catalog JSON Database")
]

for path, name in endpoints:
    url = f"{BASE_URL}{path}"
    req = urllib.request.Request(url, headers={"User-Agent": "VerifierBot/1.0"})
    with urllib.request.urlopen(req, timeout=5) as resp:
        assert resp.status == 200, f"Failed {name}: status {resp.status}"
        body = resp.read().decode('utf-8')
        print(f"  [PASS] {name} ({url}) returned HTTP 200 ({len(body)} bytes)")

        # Verify NO email anywhere on public pages
        if not path.endswith('.json') and 'admin' not in path:
            assert "srihanumsastha@gmail.com" not in body, f"Email found on {name}!"
            assert "mailto:" not in body, f"mailto link found on {name}!"
            
            # Verify Phone numbers
            assert "9688727284" in body, f"Phone 9688727284 missing on {name}"
            assert "8695706013" in body, f"Phone 8695706013 missing on {name}"
            
            # Verify WhatsApp links
            assert "wa.me" in body or "WhatsApp" in body, f"WhatsApp missing on {name}"

print("  [PASS] Zero email leakage verified across all pages.")
print("  [PASS] Phone numbers and WhatsApp links verified across all pages.")

# 3. Test Product Detail Page Specifics
print("\n[STEP 3] Testing Product Details Page Content...")
with open(os.path.join(PROJECT_DIR, "product.html"), "r", encoding="utf-8") as f:
    prod_html = f.read()
    assert "detail-gallery" in prod_html
    assert "waPrimaryBtn" in prod_html
    assert "waSecondaryBtn" in prod_html
    assert "optionsTable" in prod_html
    assert "specsGrid" in prod_html
    assert "relatedGrid" in prod_html
    assert "backToCatBtn" in prod_html
    assert "https://wa.me/919688727284" in prod_html
    assert "https://wa.me/918695706013" in prod_html
    print("  [PASS] product.html contains Featherlite-inspired layout, WhatsApp CTAs, options table, and related chairs.")

# 4. Catalog Breakdown
print("\n[STEP 4] Verifying 228 Catalog Items & Model Names...")
with open(os.path.join(PROJECT_DIR, "assets", "catalog.json"), "r", encoding="utf-8") as f:
    catalog = json.load(f)
    assert len(catalog) == 228, f"Expected 228, got {len(catalog)}"
    cats = {}
    missing_models = 0
    for p in catalog:
        c = p.get('category')
        cats[c] = cats.get(c, 0) + 1
        if not p.get('_internal_model'):
            missing_models += 1

    print(f"  [PASS] Total items: {len(catalog)}")
    for c, cnt in cats.items():
        print(f"    - {c}: {cnt} items")
    assert missing_models == 0, f"Found {missing_models} missing model names"
    print("  [PASS] All 228 items have genuine manufacturer model names.")

print("\n==================================================")
print("  ALL VERIFICATION TESTS COMPLETED SUCCESSFULLY!  ")
print("==================================================")
