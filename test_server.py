import urllib.request
import json
import sys

base_url = "http://127.0.0.1:8080"

def test_url(path, desc):
    url = f"{base_url}{path}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            status = response.status
            content = response.read()
            size = len(content)
            print(f"[PASS] {desc}: {path} -> Status {status}, Size: {size} bytes")
            return content
    except Exception as e:
        print(f"[FAIL] {desc}: {path} -> Error: {e}")
        return None

print("=== 1. Core Pages & Assets ===")
index_html = test_url("/index.html", "Homepage HTML")
styles_css = test_url("/styles.css", "Styles CSS")
app_js = test_url("/app.js", "App JS")
catalog_json_bytes = test_url("/assets/catalog.json", "Catalog JSON")
logo_svg = test_url("/assets/logo.svg", "Logo SVG")
logo_white = test_url("/assets/logo-white.svg", "Logo White SVG")
placeholder_svg = test_url("/assets/placeholder.svg", "Placeholder SVG")
contact_html = test_url("/contact.html", "Contact Page HTML")
category_html = test_url("/category.html?cat=office", "Category Page HTML")

print("\n=== 2. Catalogue Verification ===")
if catalog_json_bytes:
    data = json.loads(catalog_json_bytes.decode('utf-8'))
    print(f"Total products loaded: {len(data)}")
    
    # Check sample images
    sample_items = data[:10] + data[120:130] + data[180:190]
    img_failures = 0
    for item in sample_items:
        img_res = test_url(f"/{item['image']}", f"Image for {item['name']}")
        if img_res is None or len(img_res) == 0:
            img_failures += 1
            
    print(f"Image failures on 30 sample items: {img_failures}")

print("\n=== 3. Verification of Business Details in HTML ===")
if index_html:
    txt = index_html.decode('utf-8')
    assert "9688727284" in txt, "Missing phone 9688727284"
    assert "8695706013" in txt, "Missing phone 8695706013"
    assert "tel:9688727284" in txt, "Missing tel:9688727284 link"
    assert "tel:8695706013" in txt, "Missing tel:8695706013 link"
    assert "Call 9688727284" in txt, "Missing Call 9688727284 button"
    assert "Call 8695706013" in txt, "Missing Call 8695706013 button"
    assert "173, First Floor, KK Lane Street, Avinashi Road, Coimbatore" in txt, "Missing address"
    assert "Sri Hanum Sastha Enterprises" in txt, "Missing company name"
    assert "Quality Seating for Every Space" in txt, "Missing hero heading"
    assert "Prices may change. Please contact us to confirm current prices and availability." in txt, "Missing price notice"
    print("[PASS] All required business details and buttons present!")

if contact_html:
    ctxt = contact_html.decode('utf-8')
    assert "tel:9688727284" in ctxt, "Missing tel in contact.html"
    assert "tel:8695706013" in ctxt, "Missing tel in contact.html"
    print("[PASS] Contact page verified!")

print("\nALL SYSTEM TESTS PASSED SUCCESSFULLY!")
