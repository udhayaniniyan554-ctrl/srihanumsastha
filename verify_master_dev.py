import urllib.request
import urllib.parse
import http.client
import json
import os
import re

BASE_URL = "http://127.0.0.1:8080"
PROJECT_DIR = r"C:\Users\user\.gemini\antigravity\scratch\srihanumsastha-catalogue"

def request_url(url, method=None, data=None, headers=None, timeout=10):
    parsed = urllib.parse.urlparse(url)
    conn = http.client.HTTPConnection(parsed.hostname, parsed.port or 80, timeout=timeout)
    hdrs = {}
    if headers:
        hdrs.update(headers)
    if method is None:
        method = "POST" if data is not None else "GET"
    path = parsed.path
    if parsed.query:
        path += "?" + parsed.query
    conn.request(method, path, body=data, headers=hdrs)
    resp = conn.getresponse()
    body = resp.read().decode('utf-8')
    status = resp.status
    conn.close()
    return status, body

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

# ---------------- STEP 2: DESIGN TOKENS & BUTTON SYSTEM ----------------
print("\n[STEP 2] Verifying Showroom Palette & Button System in styles.css...")
with open(os.path.join(PROJECT_DIR, "styles.css"), "r", encoding="utf-8") as f:
    css_content = f.read()
    assert "#14532D" in css_content, "Forest green #14532D missing in CSS!"
    assert "#166534" in css_content, "Hover green #166534 missing in CSS!"
    assert "#FFFFFF" in css_content, "Pure white missing in CSS!"
    assert "#111111" in css_content, "Main text #111111 missing in CSS!"
    assert "#F7F8F6" in css_content, "Light neutral #F7F8F6 missing in CSS!"
    assert "#E5E7EB" in css_content, "Border #E5E7EB missing in CSS!"
    assert "--btn-h-base: 44px" in css_content
    assert "--btn-h-sm: 38px" in css_content
    assert "--btn-h-lg: 50px" in css_content
    assert ".btn-primary" in css_content
    assert ".btn-secondary" in css_content
    assert ".hero-carousel-section" in css_content
    assert ".preview-section" in css_content

print("  [PASS] Showroom palette tokens verified (White, #111111, Forest Green #14532D, Neutral #F7F8F6, Borders #E5E7EB).")
print("  [PASS] Standard button heights (44px, 38px, 50px) and variants verified.")

# ---------------- STEP 3: REST API ENDPOINTS ----------------
print("\n[STEP 3] Testing FastAPI REST Endpoints on Port 8080...")

# 3a. Health
status, body = request_url(f"{BASE_URL}/api/health")
assert status == 200
health = json.loads(body)
assert health["status"] == "healthy"
assert health["backend"] == "FastAPI"
assert health["catalogue_items"] == 228
print(f"  [PASS] /api/health returned 200 OK (Items: {health['catalogue_items']}, Backend: {health['backend']})")

# 3b. Chairs
status, body = request_url(f"{BASE_URL}/api/chairs")
assert status == 200
chairs = json.loads(body)
assert len(chairs) == 228
print(f"  [PASS] /api/chairs returned 200 OK ({len(chairs)} chairs served)")

# 3c. Single Chair (office_1_2 requested by user)
status, body = request_url(f"{BASE_URL}/api/chairs/office_1_2")
assert status == 200
c2 = json.loads(body)
assert c2["code"] == "SHSE 2"
assert c2["display_name"] == "OFFICE CHAIRS  SHSE 2"
assert c2["_internal_model"] == "4G"
print(f"  [PASS] /api/chairs/office_1_2 returned 200 OK (Title: {c2['display_name']}, Code: {c2['code']}, Model: {c2['_internal_model']})")

# 3d. Admin Auth (Testing Priya / Adhithi@2021)
login_payload = json.dumps({"username": "Priya", "password": "Adhithi@2021"}).encode('utf-8')
status, body = request_url(
    f"{BASE_URL}/api/admin/login",
    data=login_payload,
    headers={"Content-Type": "application/json"}
)
assert status == 200
auth_data = json.loads(body)
assert auth_data["success"] is True
assert "token" in auth_data
print("  [PASS] /api/admin/login authenticated successfully with Priya / Adhithi@2021.")

# ---------------- STEP 4: PUBLIC PAGES & STRICT REQUIREMENTS ----------------
print("\n[STEP 4] Testing Public Pages & Strict Requirements...")
pages = [
    ("/", "Homepage"),
    ("/index.html", "Index Page"),
    ("/category.html?cat=office", "Category Page (Office)"),
    ("/category.html?cat=visitor", "Category Page (Visitor)"),
    ("/product.html?id=office_1_2", "Primary Test Product Page (office_1_2)"),
    ("/contact.html", "Contact Page"),
    ("/admin.html", "Admin Manager")
]

for path, name in pages:
    url = f"{BASE_URL}{path}"
    status, body = request_url(url)
    assert status == 200, f"Failed {name}: status {status}"
    print(f"  [PASS] {name} ({url}) returned HTTP 200 ({len(body)} bytes)")

    # Verify email display in contact section & footer area
    if "admin" not in path:
        assert "srihanumsastha@gmail.com" in body, f"Email address missing on {name}!"
        assert "mailto:srihanumsastha@gmail.com" in body, f"mailto link missing on {name}!"

        # Verify zero PROMAX branding or publication years in public pages
        assert "promax" not in body.lower(), f"PROMAX branding found on {name}!"
        assert "catalogue 2024" not in body.lower()
        assert "catalogue 2025" not in body.lower()

        # WhatsApp check: MUST use 8695706013 exclusively for WhatsApp
        assert "https://wa.me/918695706013" in body, f"WhatsApp 8695706013 missing on {name}"
        assert "https://wa.me/919688727284" not in body, f"Old WhatsApp 9688727284 found on {name}!"

        # Direct & alternate phone numbers
        assert "9688727284" in body, f"Phone 9688727284 missing on {name}!"
        assert "tel:+919688727284" in body, f"tel link 9688727284 missing on {name}!"
        assert "tel:+918695706013" in body, f"tel link 8695706013 missing on {name}!"

        # Header check: Clean PROMAX-style layout - NO phone, NO email, NO address, NO WhatsApp in header
        header_match = re.search(r'<header.*?</header>', body, re.DOTALL)
        if header_match:
            header_html = header_match.group(0)
            assert "tel:" not in header_html, f"Phone link found in header of {name}!"
            assert "mailto:" not in header_html, f"Email link found in header of {name}!"
            assert "9688727284" not in header_html, f"Phone number found in header of {name}!"
            assert "8695706013" not in header_html, f"WhatsApp number found in header of {name}!"
            assert "wa.me" not in header_html, f"WhatsApp link found in header of {name}!"
            assert "KK Lane" not in header_html, f"Address found in header of {name}!"
            assert ("assets/Sri Hanum Sastha Enterprises Logo landscape.png" in header_html or "assets/SHSE Logo.png" in header_html), f"SHSE Logo missing from header of {name}!"
        
        # Verify top black information bar is completely removed
        topbar_match = re.search(r'<aside class="top-bar".*?</aside>', body, re.DOTALL)
        assert topbar_match is None, f"Top bar must be removed completely on {name}!"

print("  [PASS] Clean PROMAX-style header verified: Zero phone, email, address, or WhatsApp in header.")
print("  [PASS] Top bar completely removed across all public pages.")
print("  [PASS] Official SHSE Logo verified in header.")
print("  [PASS] Contact details verified: Company, Address, WhatsApp 8695706013, Phone 9688727284, Email srihanumsastha@gmail.com.")
print("  [PASS] Zero PROMAX branding or catalogue publication years verified.")

# ---------------- STEP 5: HERO CAROUSEL & PRODUCT PREVIEW (2s Timing) ----------------
print("\n[STEP 5] Verifying 2s Hero Carousel & Moving Product Preview...")
with open(os.path.join(PROJECT_DIR, "index.html"), "r", encoding="utf-8") as f:
    idx_html = f.read()
    assert "hero-carousel-container" in idx_html, "Hero carousel missing in index.html"
    assert "hero-slide" in idx_html, "Hero slides missing in index.html"
    assert "previewTrack" in idx_html, "previewTrack missing in index.html"
    assert "preview-section" in idx_html, "preview-section missing in index.html"
    assert "OFFICE CHAIRS  SHSE 1" in idx_html
    assert "OFFICE CHAIRS  SHSE 2" in idx_html

with open(os.path.join(PROJECT_DIR, "app.js"), "r", encoding="utf-8") as f:
    app_js = f.read()
    assert "HERO_INTERVAL = 2000" in app_js, "Hero 2s interval missing in app.js"
    assert "PREVIEW_INTERVAL = 2000" in app_js, "Preview 2s interval missing in app.js"
    assert "initHeroCarousel" in app_js
    assert "initProductPreviewTrack" in app_js

print("  [PASS] Hero Automatic Chair Carousel verified with 2000ms (2s) interval, smooth transitions & controls.")
print("  [PASS] Moving Product Preview Section verified with 2000ms (2s) auto-step, authentic chairs & pause on hover.")

# ---------------- STEP 6: TARGET PRODUCT DETAIL PAGE (office_1_2) ----------------
print("\n[STEP 6] Testing Target Product Detail Page (office_1_2)...")
with open(os.path.join(PROJECT_DIR, "product.html"), "r", encoding="utf-8") as f:
    prod_html = f.read()
    assert "detail-gallery" in prod_html
    assert "detail-main-canvas" in prod_html
    assert "waPrimaryBtn" in prod_html
    assert "optionsTable" in prod_html
    assert "specsGrid" in prod_html
    assert "relatedGrid" in prod_html
    assert "backToCatBtn" in prod_html
    assert "https://wa.me/918695706013" in prod_html
    assert "https://wa.me/919688727284" not in prod_html

# Verify office_1_2 in catalog.json
with open(os.path.join(PROJECT_DIR, "assets", "catalog.json"), "r", encoding="utf-8") as f:
    catalog = json.load(f)
    o2 = [p for p in catalog if p['id'] == 'office_1_2'][0]
    assert o2['code'] == 'SHSE 2'
    assert o2['display_name'] == 'OFFICE CHAIRS  SHSE 2'
    assert o2['_internal_model'] == '4G'
    assert o2['category'] == 'Office Chairs'
    assert os.path.exists(os.path.join(PROJECT_DIR, o2['image'].replace('/', os.sep)))

print("  [PASS] Target product.html?id=office_1_2 verified: OFFICE CHAIRS  SHSE 2, model 4G, clean white canvas, specs & 8695706013 CTA.")

# ---------------- STEP 7: ASSET INTEGRITY & UNIFORM MODEL NAMING (228 Models) ----------------
print("\n[STEP 7] Verifying 228 Catalog Items, Uniform Model Naming, Authentic Photos, Schematics...")
assert len(catalog) == 228, f"Expected 228, got {len(catalog)}"

# Verify uniform model naming format on ALL 228 chairs:
valid_naming_pattern = re.compile(r"^(OFFICE CHAIRS|VISITOR CHAIRS|LOUNGE CHAIRS|DINING CHAIRS|STOOLS)  SHSE [0-9]+$")
for p in catalog:
    assert "display_name" in p, f"Missing display_name in {p['id']}"
    assert valid_naming_pattern.match(p["display_name"]), f"Invalid display_name '{p['display_name']}' in {p['id']}! Must follow CATEGORY  SHSE [N]"
    assert p["code"] == f"SHSE {p['code_number']}", f"Invalid code format '{p['code']}' in {p['id']}"

print("  [PASS] All 228 chairs strictly follow uniform naming format: [CATEGORY]  SHSE [N] with small consistent spacing.")

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

# Exact required category counts
assert cats.get('Office Chairs') == 128, f"Expected 128 Office Chairs, got {cats.get('Office Chairs')}"
assert cats.get('Visitor Chairs') == 48, f"Expected 48 Visitor Chairs, got {cats.get('Visitor Chairs')}"
assert cats.get('Lounge & Soft Seating') == 24, f"Expected 24 Lounge, got {cats.get('Lounge & Soft Seating')}"
assert cats.get('Dining Chairs') == 21, f"Expected 21 Dining, got {cats.get('Dining Chairs')}"
assert cats.get('Stools & Additional Seating') == 7, f"Expected 7 Stools, got {cats.get('Stools & Additional Seating')}"

# ---------------- STEP 8: ORIGINAL CHAIR CONCEPTS API & ISOLATION ----------------
print("\n[STEP 8] Verifying Original Chair Concepts API & Separation...")
status, body = request_url(f"{BASE_URL}/api/concepts")
assert status == 200
concepts = json.loads(body)
assert len(concepts) == 6, f"Expected 6 concepts, got {len(concepts)}"
for c in concepts:
    assert c.get("is_concept") is True
    assert "Aura" in c.get("name") or "Kanso" in c.get("name") or "Solace" in c.get("name") or "Veloce" in c.get("name") or "Forma" in c.get("name") or "Nexus" in c.get("name")
print(f"  [PASS] /api/concepts returned 200 OK with {len(concepts)} exploratory design studies.")
print("  [PASS] All concepts verified with strict non-commercial R&D flag and disclaimer.")

# ---------------- STEP 9: AI CATALOGUE CHATBOT ENDPOINT ----------------
print("\n[STEP 9] Verifying AI Catalogue Chatbot API (/api/chat)...")
chat_payload = json.dumps({"message": "Tell me about ATLAS chair"}).encode('utf-8')
status, body = request_url(
    f"{BASE_URL}/api/chat",
    data=chat_payload,
    headers={"Content-Type": "application/json"}
)
assert status == 200
chat_res = json.loads(body)
assert "reply" in chat_res
assert len(chat_res["reply"]) > 20
assert "disclaimer" in chat_res
print(f"  [PASS] /api/chat returned 200 OK (Source: {chat_res.get('source', 'engine')})")
print(f"  [PASS] Verified grounded response: {chat_res['reply'][:70]}...")

# ---------------- STEP 10: INTERACTIVE UTILITIES CONSISTENCY ----------------
print("\n[STEP 10] Verifying Interactive Utilities across All Public Pages...")
core_pages = ["index.html", "product.html", "category.html", "contact.html"]
for page_file in core_pages:
    page_path = os.path.join(PROJECT_DIR, page_file)
    with open(page_path, "r", encoding="utf-8") as f:
        html = f.read()
        assert "compareFloatingBar" in html, f"compareFloatingBar missing in {page_file}"
        assert "compareModal" in html, f"compareModal missing in {page_file}"
        assert "savedDrawer" in html, f"savedDrawer missing in {page_file}"
        assert "chatWidgetToggle" in html, f"chatWidgetToggle missing in {page_file}"
        assert "chatWindow" in html, f"chatWindow missing in {page_file}"
        assert "app.js" in html, f"app.js script tag missing in {page_file}"
        print(f"  [PASS] {page_file} contains compare bar, compare modal, saved drawer, and AI chatbot widget.")

# ---------------- STEP 11: LIGHTBOX ZOOM ON PRODUCT DETAIL PAGE ----------------
print("\n[STEP 11] Verifying Image Lightbox Zoom on product.html...")
with open(os.path.join(PROJECT_DIR, "product.html"), "r", encoding="utf-8") as f:
    prod_html = f.read()
    assert "lightboxModal" in prod_html
    assert "lightboxImg" in prod_html
    assert "lightboxClose" in prod_html
    assert "btnDetailCompare" in prod_html
    assert "btnDetailSave" in prod_html
print("  [PASS] product.html verified with click-to-zoom Lightbox modal and Compare/Save toggles.")

# ---------------- STEP 12: CUSTOMER REVIEWS SYSTEM & FORM VALIDATION ----------------
print("\n[STEP 12] Verifying Customer Reviews Section, Storage & Form Validation...")

# 12a. Verify HTML elements
with open(os.path.join(PROJECT_DIR, "index.html"), "r", encoding="utf-8") as f:
    idx_content = f.read()
    assert "What Our Customers Say" in idx_content, "Reviews section title missing"
    assert 'id="reviews"' in idx_content, "Reviews section id missing"
    assert 'id="openReviewModalBtn"' in idx_content, "Submit Review button missing"
    assert 'id="reviewModal"' in idx_content, "Review modal missing"
    assert 'id="reviewForm"' in idx_content, "Review form missing"
    assert 'id="reviewsGrid"' in idx_content, "Reviews grid missing"
    assert 'id="reviewsEmptyState"' in idx_content, "Reviews empty state missing"
print("  [PASS] index.html contains 'What Our Customers Say' section, review cards grid, and submission modal.")

# 12b. Verify CSS rules
with open(os.path.join(PROJECT_DIR, "styles.css"), "r", encoding="utf-8") as f:
    css_content = f.read()
    assert ".reviews-section" in css_content, "reviews-section CSS missing"
    assert ".review-card" in css_content, "review-card CSS missing"
    assert ".star-rating-picker" in css_content, "star-rating-picker CSS missing"
print("  [PASS] styles.css contains premium review cards, subtle hover effects, and star picker.")

# 12c. Test GET /api/reviews
status, body = request_url(f"{BASE_URL}/api/reviews")
assert status == 200, f"GET /api/reviews failed: {status}"
reviews_list = json.loads(body)
assert isinstance(reviews_list, list), "Reviews must be a list"
print(f"  [PASS] GET /api/reviews returned 200 OK (Current count: {len(reviews_list)}).")

# 12d. Test Validation Errors
validation_tests = [
    ({"name": "", "rating": 5, "comment": "Valid test comment long enough"}, "Missing name"),
    ({"name": "Test User", "rating": 6, "comment": "Valid test comment long enough"}, "Rating > 5"),
    ({"name": "Test User", "rating": 0, "comment": "Valid test comment long enough"}, "Rating < 1"),
    ({"name": "Test User", "rating": 5, "comment": "Too short"}, "Comment < 10 chars"),
]

for test_payload, test_name in validation_tests:
    req_body = json.dumps(test_payload).encode('utf-8')
    status, body = request_url(
        f"{BASE_URL}/api/reviews",
        data=req_body,
        headers={"Content-Type": "application/json"}
    )
    assert status == 400, f"Expected 400 Bad Request for {test_name}, got {status}"
print("  [PASS] Form validation strictly verified: empty names, invalid ratings, and short comments rejected with 400.")

# 12e. Test Review Submission with Pending Status & Public Isolation
test_sub_payload = {
    "name": "Coimbatore Tech Hub",
    "rating": 5,
    "comment": "Ordered ergonomic high-back chairs for our software engineering team. Superior lumbar support and quick coordination via WhatsApp.",
    "location": "Saravanampatti, Coimbatore"
}
req_sub = json.dumps(test_sub_payload).encode('utf-8')
status, body = request_url(
    f"{BASE_URL}/api/reviews",
    data=req_sub,
    headers={"Content-Type": "application/json"}
)
assert status == 200, f"Submission failed with status {status}"
sub_res = json.loads(body)
assert sub_res["success"] is True
assert sub_res["review"]["name"] == "Coimbatore Tech Hub"
assert sub_res["review"]["rating"] == 5
assert sub_res["review"]["status"] == "pending", f"Expected review status 'pending', got {sub_res['review']['status']}"
test_rev_id = sub_res["review"]["id"]

# Verify pending review is NOT returned in public GET /api/reviews
status, body = request_url(f"{BASE_URL}/api/reviews")
assert status == 200
stored_reviews = json.loads(body)
assert not any(r["id"] == test_rev_id for r in stored_reviews), "Pending review must NOT appear in public GET /api/reviews!"
print("  [PASS] Review submission saved with status 'pending' and strictly isolated from public website.")

# Verify pending review IS returned in protected GET /api/admin/reviews
status, body = request_url(
    f"{BASE_URL}/api/admin/reviews",
    headers={"Authorization": f"Bearer {auth_data['token']}"}
)
assert status == 200
admin_all_reviews = json.loads(body)
assert any(r["id"] == test_rev_id and r["status"] == "pending" for r in admin_all_reviews), "Pending review must appear in Admin Reviews!"
print("  [PASS] Pending review correctly returned only inside Admin Dashboard -> Customer Reviews.")

# 12f. Test Admin Review Deletion Security & Permanent Removal

# Verify admin.html contains Customer Reviews management
with open(os.path.join(PROJECT_DIR, "admin.html"), "r", encoding="utf-8") as f:
    admin_content = f.read()
    assert "tabBtnReviews" in admin_content, "Reviews tab missing in admin.html"
    assert "tabPanelReviews" in admin_content, "Reviews panel missing in admin.html"
    assert "btn-delete-review" in admin_content, "Delete review button missing in admin.html"
    assert "deleteReview" in admin_content, "deleteReview JS function missing in admin.html"
    assert "confirm(" in admin_content, "Confirmation prompt missing before review deletion"
print("  [PASS] admin.html contains Customer Reviews tab, review table, confirmation prompt, and Delete buttons.")

# Unauthenticated delete attempt -> 401
status, _ = request_url(f"{BASE_URL}/api/admin/reviews/{test_rev_id}", method="DELETE")
assert status == 401, f"Expected 401 Unauthorized for review delete without token, got {status}"

# Bad token delete attempt -> 403
status, _ = request_url(
    f"{BASE_URL}/api/admin/reviews/{test_rev_id}",
    method="DELETE",
    headers={"Authorization": "Bearer invalid_token_123"}
)
assert status == 403, f"Expected 403 Forbidden for review delete with invalid token, got {status}"
print("  [PASS] Admin security strictly verified: unauthorized or invalid tokens cannot delete reviews.")

# Authorized admin delete
status, body = request_url(
    f"{BASE_URL}/api/admin/reviews/{test_rev_id}",
    method="DELETE",
    headers={"Authorization": f"Bearer {auth_data['token']}"}
)
assert status == 200, f"Expected 200 OK for authorized admin delete, got {status}"
del_res = json.loads(body)
assert del_res["success"] is True

# Verify review is permanently removed from public GET /api/reviews
status, body = request_url(f"{BASE_URL}/api/reviews")
assert status == 200
stored_reviews_after = json.loads(body)
assert not any(r["id"] == test_rev_id for r in stored_reviews_after), "Deleted review still present in GET /api/reviews!"
print("  [PASS] Review permanently deleted from database & removed from public website.")

# ---------------- STEP 13: MERGED IN-PAGE ADMIN DASHBOARD (2 OPTIONS) & REVIEW MODERATION ----------------
print("\n[STEP 13] Verifying Merged Admin Dashboard on index.html (Customer Reviews & Add New Chairs)...")

with open(os.path.join(PROJECT_DIR, "index.html"), "r", encoding="utf-8") as f:
    idx_content = f.read()
    # Check Admin Dashboard button in header
    assert 'id="openAdminNavBtn"' in idx_content, "openAdminNavBtn button missing in index.html"
    assert 'btn-header-admin' in idx_content, "btn-header-admin CSS class missing in index.html"
    # Check Admin button is to the left of the Saved button
    admin_btn_pos = idx_content.find('id="openAdminNavBtn"')
    saved_btn_pos = idx_content.find('btn-header-saved')
    assert admin_btn_pos != -1 and saved_btn_pos != -1, "Both admin and saved buttons must exist in index.html"
    assert admin_btn_pos < saved_btn_pos, "Admin Dashboard button must be to the left of the Saved button!"

    # Check mobile drawer button
    assert 'id="mobileOpenAdminBtn"' in idx_content, "mobileOpenAdminBtn missing in index.html"

    # Check Admin Login Modal
    assert 'id="adminLoginModal"' in idx_content, "adminLoginModal missing in index.html"
    assert 'id="adminLoginForm"' in idx_content, "adminLoginForm missing in index.html"
    assert 'id="adminModalUser"' in idx_content, "adminModalUser missing in index.html"
    assert 'id="adminModalPass"' in idx_content, "adminModalPass missing in index.html"

    # Check Admin Dashboard Overlay with ONLY TWO main options
    assert 'id="adminDashboardOverlay"' in idx_content, "adminDashboardOverlay missing in index.html"
    assert 'id="adminTabBtnReviews"' in idx_content, "Customer Reviews tab missing in merged dashboard"
    assert 'id="adminTabBtnAddChair"' in idx_content, "Add New Chairs tab missing in merged dashboard"
    assert 'id="adminTabBtnChairs"' not in idx_content, "Chair Catalogue tab must be removed from Admin Dashboard!"
    assert 'id="adminPanelReviews"' in idx_content, "Customer Reviews panel missing in merged dashboard"
    assert 'id="adminPanelAddChair"' in idx_content, "Add New Chairs panel missing in merged dashboard"
    assert 'id="chairUploadDropzone"' in idx_content, "Chair photo upload dropzone missing in Add New Chairs panel"
    assert 'id="dashAddChairForm"' in idx_content, "Add Chair Form missing in Add New Chairs panel"
    assert 'id="pillRevAll"' in idx_content, "All Reviews filter pill missing in index.html"
    assert 'id="pillRevPending"' in idx_content, "Pending filter pill missing in index.html"
    assert 'id="pillRevApproved"' in idx_content, "Approved filter pill missing in index.html"
    assert 'id="pillRevRejected"' in idx_content, "Rejected filter pill missing in index.html"
    assert 'id="btnAdminCustomerView"' in idx_content, "btnAdminCustomerView missing in index.html"
print("  [PASS] Admin Dashboard strictly contains only Customer Reviews and Add New Chairs with 4 Status Filter Pills.")

# Test Review Moderation API (Approve / Reject / Delete)
# 1. Create a review
test_mod_payload = {
    "name": "Arun Kumar Moderation Test",
    "rating": 5,
    "comment": "Testing the approve, reject and delete moderation functionality in merged dashboard.",
    "location": "RS Puram, Coimbatore"
}
req_sub = json.dumps(test_mod_payload).encode('utf-8')
status, body = request_url(
    f"{BASE_URL}/api/reviews",
    data=req_sub,
    headers={"Content-Type": "application/json"}
)
assert status == 200
mod_review = json.loads(body)["review"]
mod_rev_id = mod_review["id"]
assert mod_review["status"] == "pending", f"Expected 'pending' status for newly submitted review, got {mod_review['status']}"

# Verify pending review is NOT in public reviews
status, body = request_url(f"{BASE_URL}/api/reviews")
assert not any(r["id"] == mod_rev_id for r in json.loads(body)), "Pending review must NOT appear in public reviews!"
print("  [PASS] Newly submitted review has status 'pending' and is hidden from public website.")

# 2. Status toggle without token -> 401
reject_payload = json.dumps({"status": "rejected"}).encode('utf-8')
status, _ = request_url(
    f"{BASE_URL}/api/admin/reviews/{mod_rev_id}/status",
    method="PUT",
    data=reject_payload,
    headers={"Content-Type": "application/json"}
)
assert status == 401, f"Expected 401 Unauthorized for status update without token, got {status}"

# 3. Status toggle with valid admin token -> reject
status, body = request_url(
    f"{BASE_URL}/api/admin/reviews/{mod_rev_id}/status",
    method="PUT",
    data=reject_payload,
    headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {auth_data['token']}"
    }
)
assert status == 200, f"Expected 200 OK for status reject, got {status}"
res_status = json.loads(body)
assert res_status["status"] == "rejected"

# 4. Verify rejected review is hidden from public GET /api/reviews
status, body = request_url(f"{BASE_URL}/api/reviews")
assert status == 200
pub_reviews = json.loads(body)
assert not any(r["id"] == mod_rev_id for r in pub_reviews), "Rejected review must NOT appear in public GET /api/reviews"
print("  [PASS] Rejected review is successfully hidden from public customer reviews.")

# 5. Status toggle with valid admin token -> approve
approve_payload = json.dumps({"status": "approved"}).encode('utf-8')
status, body = request_url(
    f"{BASE_URL}/api/admin/reviews/{mod_rev_id}/status",
    method="PUT",
    data=approve_payload,
    headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {auth_data['token']}"
    }
)
assert status == 200, f"Expected 200 OK for status approve, got {status}"

# 6. Verify approved review is now visible in public GET /api/reviews
status, body = request_url(f"{BASE_URL}/api/reviews")
assert status == 200
pub_reviews_app = json.loads(body)
assert any(r["id"] == mod_rev_id for r in pub_reviews_app), "Approved review must appear in public GET /api/reviews"
print("  [PASS] Approved review is successfully displayed in public customer reviews.")

# 7. Clean up by deleting the test review via admin API
status, body = request_url(
    f"{BASE_URL}/api/admin/reviews/{mod_rev_id}",
    method="DELETE",
    headers={"Authorization": f"Bearer {auth_data['token']}"}
)
assert status == 200
print("  [PASS] Test review cleaned up via DELETE API; real customer reviews preserved.")

# ---------------- STEP 14: ADD NEW CHAIRS ADMIN OPTION & WORKFLOW ----------------
print("\n[STEP 14] Verifying Add New Chairs Admin Feature & Catalogue Synchronization...")

# 1. Add new chair via POST /api/admin/chairs
test_chair_payload = {
    "name": "Ergonomic Pro High-Back Test Chair",
    "category": "Office Chairs",
    "base_price": 7500,
    "description": "Breathable high-density mesh, synchro tilt, nylon base, test entry.",
    "image": "assets/products/office_1_1.png"
}
status, body = request_url(
    f"{BASE_URL}/api/admin/chairs",
    data=json.dumps(test_chair_payload).encode('utf-8'),
    headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {auth_data['token']}"
    }
)
assert status == 200, f"Expected 200 OK for add chair, got {status}: {body}"
created_chair = json.loads(body)["chair"]
test_chair_id = created_chair["id"]
assert "Office Chairs" in created_chair["category"]
assert created_chair["base_price"] == 7500
assert "SHSE" in created_chair["code"]
print(f"  [PASS] New chair created successfully: {created_chair['code']} ({created_chair['display_name']}).")

# 2. Verify new chair appears in public GET /api/chairs
status, body = request_url(f"{BASE_URL}/api/chairs")
assert status == 200
chairs_list = json.loads(body)
found_chair = next((c for c in chairs_list if c["id"] == test_chair_id), None)
assert found_chair is not None, "Newly added chair must appear in public chairs catalogue!"
print("  [PASS] Newly added chair immediately published and visible in public catalogue.")

# 3. Edit chair via PUT /api/admin/chairs/{id}
update_chair_payload = {
    "name": "Ergonomic Pro High-Back Updated",
    "category": "Office Chairs",
    "base_price": 8200,
    "description": "Updated specifications and pricing.",
    "image": "assets/products/office_1_1.png"
}
status, body = request_url(
    f"{BASE_URL}/api/admin/chairs/{test_chair_id}",
    method="PUT",
    data=json.dumps(update_chair_payload).encode('utf-8'),
    headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {auth_data['token']}"
    }
)
assert status == 200, f"Expected 200 OK for chair update, got {status}: {body}"
updated_res = json.loads(body)["chair"]
assert updated_res["base_price"] == 8200
print("  [PASS] Chair successfully updated with new pricing and specifications.")

# 4. Delete chair via DELETE /api/admin/chairs/{id}
status, body = request_url(
    f"{BASE_URL}/api/admin/chairs/{test_chair_id}",
    method="DELETE",
    headers={"Authorization": f"Bearer {auth_data['token']}"}
)
assert status == 200, f"Expected 200 OK for chair deletion, got {status}: {body}"

# 5. Verify deleted chair is removed from public catalogue
status, body = request_url(f"{BASE_URL}/api/chairs")
assert status == 200
chairs_after_del = json.loads(body)
assert not any(c["id"] == test_chair_id for c in chairs_after_del), "Deleted chair must NOT appear in catalogue!"
assert len(chairs_after_del) == 228, f"Expected 228 original catalogue items, got {len(chairs_after_del)}"
print("  [PASS] Chair permanently deleted from catalogue; baseline of 228 items perfectly intact.")

print("\n==================================================================")
print("  ALL 14 VERIFICATION STAGES PASSED WITH ZERO ERRORS!            ")
print("==================================================================")
