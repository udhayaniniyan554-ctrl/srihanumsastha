import urllib.request
import urllib.parse
import json
import os
import re

BASE_URL = "http://127.0.0.1:8080"
PROJECT_DIR = r"C:\Users\user\.gemini\antigravity\scratch\srihanumsastha-catalogue"

print("==================================================================")
print("  COMPREHENSIVE VERIFICATION SUITE - SRI HANUM SASTHA ENTERPRISES  ")
print("==================================================================")

# ---------------- STEP 1: ARCHITECTURE & DEPLOYMENT CONFIG ----------------
print("\n[STEP 1] Verifying Render Web Service & Supabase Architecture...")
assert os.path.exists(os.path.join(PROJECT_DIR, "render.yaml")), "render.yaml missing"
assert os.path.exists(os.path.join(PROJECT_DIR, "requirements.txt")), "requirements.txt missing"
assert os.path.exists(os.path.join(PROJECT_DIR, "app_server.py")), "app_server.py missing"
assert os.path.exists(os.path.join(PROJECT_DIR, "supabase_schema.sql")), "supabase_schema.sql missing"
assert os.path.exists(os.path.join(PROJECT_DIR, "seed_supabase.py")), "seed_supabase.py missing"

with open(os.path.join(PROJECT_DIR, "render.yaml"), "r", encoding="utf-8") as f:
    render_content = f.read()
    assert "type: web" in render_content
    assert "env: python" in render_content
    assert "uvicorn app_server:app" in render_content
    assert "SUPABASE_URL" in render_content

print("  [PASS] render.yaml configured with Python FastAPI web service and Supabase env vars.")
print("  [PASS] requirements.txt, supabase_schema.sql, and seed_supabase.py verified.")

# ---------------- STEP 2: REST API ENDPOINTS ----------------
print("\n[STEP 2] Testing FastAPI REST Endpoints on Port 8080...")

# 2a. Health
req = urllib.request.Request(f"{BASE_URL}/api/health")
with urllib.request.urlopen(req, timeout=15) as resp:
    assert resp.status == 200
    health = json.loads(resp.read().decode('utf-8'))
    assert health["status"] == "healthy"
    assert health["backend"] == "FastAPI"
    assert health["catalogue_items"] == 228
    print(f"  [PASS] /api/health returned 200 OK (Items: {health['catalogue_items']}, Backend: {health['backend']})")

# 2b. Chairs
req = urllib.request.Request(f"{BASE_URL}/api/chairs")
with urllib.request.urlopen(req, timeout=15) as resp:
    assert resp.status == 200
    chairs = json.loads(resp.read().decode('utf-8'))
    assert len(chairs) == 228
    print(f"  [PASS] /api/chairs returned 200 OK ({len(chairs)} chairs served)")

# 2c. Single Chair
req = urllib.request.Request(f"{BASE_URL}/api/chairs/office_1_1")
with urllib.request.urlopen(req, timeout=15) as resp:
    assert resp.status == 200
    c1 = json.loads(resp.read().decode('utf-8'))
    assert c1["code"] == "SHSE(1)"
    assert c1["_internal_model"] == "ATLAS/3G"
    print(f"  [PASS] /api/chairs/office_1_1 returned 200 OK (Code: {c1['code']}, Model: {c1['_internal_model']})")

# 2d. Admin Auth
login_payload = json.dumps({"username": "admin", "password": "shse2026"}).encode('utf-8')
req = urllib.request.Request(
    f"{BASE_URL}/api/admin/login",
    data=login_payload,
    headers={"Content-Type": "application/json"}
)
with urllib.request.urlopen(req, timeout=15) as resp:
    assert resp.status == 200
    auth_data = json.loads(resp.read().decode('utf-8'))
    assert auth_data["success"] is True
    assert "token" in auth_data
    print("  [PASS] /api/admin/login authenticated successfully and returned session token.")

# ---------------- STEP 3: HTML PAGES & STRICT REQUIREMENTS ----------------
print("\n[STEP 3] Testing Public Pages & Strict Requirements...")
pages = [
    ("/", "Homepage"),
    ("/index.html", "Index Page"),
    ("/category.html?cat=office", "Category Page (Office)"),
    ("/category.html?cat=visitor", "Category Page (Visitor)"),
    ("/product.html?id=office_1_1", "Dedicated Product Details Page"),
    ("/contact.html", "Contact Page"),
    ("/admin.html", "Admin Manager")
]

for path, name in pages:
    url = f"{BASE_URL}{path}"
    with urllib.request.urlopen(url, timeout=15) as resp:
        assert resp.status == 200, f"Failed {name}: status {resp.status}"
        body = resp.read().decode('utf-8')
        print(f"  [PASS] {name} ({url}) returned HTTP 200 ({len(body)} bytes)")

        # Verify official business email is visibly present and clickable on all public pages
        if "admin" not in path:
            assert "srihanumsastha@gmail.com" in body, f"Official email missing on {name}!"
            assert "mailto:srihanumsastha@gmail.com" in body, f"mailto link missing on {name}!"

            # Verify zero PROMAX branding or publication years in public pages
            assert "promax" not in body.lower(), f"PROMAX branding found on {name}!"
            assert "catalogue 2024" not in body.lower()
            assert "catalogue 2025" not in body.lower()

            # Phone numbers check: both must be present
            assert "9688727284" in body, f"Phone 9688727284 missing on {name}"
            assert "8695706013" in body, f"Phone 8695706013 missing on {name}"

            # WhatsApp check: MUST use 8695706013 exclusively for WhatsApp
            assert "https://wa.me/918695706013" in body, f"WhatsApp 8695706013 missing on {name}"
            assert "https://wa.me/919688727284" not in body, f"Old WhatsApp 9688727284 found on {name}!"

print("  [PASS] Verified official email srihanumsastha@gmail.com with mailto: links across all public pages.")
print("  [PASS] Zero PROMAX branding or catalogue publication years verified.")
print("  [PASS] Exclusive WhatsApp routing to 8695706013 verified across all pages.")
print("  [PASS] Both business phone lines (9688727284 & 8695706013) verified across all pages.")

# ---------------- STEP 4: PRODUCT DETAIL PAGE SPECIFICS ----------------
print("\n[STEP 4] Testing Product Detail Experience...")
with open(os.path.join(PROJECT_DIR, "product.html"), "r", encoding="utf-8") as f:
    prod_html = f.read()
    assert "detail-gallery" in prod_html
    assert "waPrimaryBtn" in prod_html
    assert "optionsTable" in prod_html
    assert "specsGrid" in prod_html
    assert "relatedGrid" in prod_html
    assert "backToCatBtn" in prod_html
    assert "https://wa.me/918695706013" in prod_html
    assert "https://wa.me/919688727284" not in prod_html
    print("  [PASS] product.html verified with Featherlite gallery, specs grid, options table, and 8695706013 CTA.")

# ---------------- STEP 5: ASSET INTEGRITY ----------------
print("\n[STEP 5] Verifying 228 Catalog Items, Images, Diagrams...")
with open(os.path.join(PROJECT_DIR, "assets", "catalog.json"), "r", encoding="utf-8") as f:
    catalog = json.load(f)
    assert len(catalog) == 228, f"Expected 228, got {len(catalog)}"

missing_images = []
missing_diagrams = []
cats = {}

for p in catalog:
    c = p.get('category')
    cats[c] = cats.get(c, 0) + 1
    
    img_path = os.path.join(PROJECT_DIR, p.get('image', '').replace('/', os.sep))
    if not os.path.exists(img_path):
        missing_images.append((p.get('id'), p.get('image')))
        
    diag = p.get('diagram')
    if diag:
        diag_path = os.path.join(PROJECT_DIR, diag.replace('/', os.sep))
        if not os.path.exists(diag_path):
            missing_diagrams.append((p.get('id'), diag))

assert len(missing_images) == 0, f"Missing {len(missing_images)} product images!"
assert len(missing_diagrams) == 0, f"Missing {len(missing_diagrams)} diagrams!"

print(f"  [PASS] All 228 product images verified on disk (0 missing).")
print(f"  [PASS] All dimensional schematics verified on disk (0 missing).")
for cat, cnt in sorted(cats.items()):
    print(f"    - {cat}: {cnt} models")

print("\n==================================================================")
print("  ALL 5 VERIFICATION STAGES PASSED WITH ZERO ERRORS!             ")
print("==================================================================")
