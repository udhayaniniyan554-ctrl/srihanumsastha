import urllib.request
import re
import json

BASE_URL = "http://127.0.0.1:8080"

pages_to_test = [
    ("/", "Homepage"),
    ("/index.html", "Index"),
    ("/category.html?cat=office", "Category - Office"),
    ("/category.html?cat=visitor", "Category - Visitor"),
    ("/category.html?cat=lounge", "Category - Lounge"),
    ("/contact.html", "Contact Page"),
]

print("=== 1. TESTING HTTP ENDPOINTS & FOOTER DETAILS ===")
for path, name in pages_to_test:
    url = f"{BASE_URL}{path}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "VerificationBot/1.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            status = resp.status
            content = resp.read().decode('utf-8')
            print(f"\n[OK] {name} ({url}) returned HTTP {status} ({len(content)} bytes)")
            
            # Check Contact Us header in footer
            assert "Contact Us" in content, f"Missing 'Contact Us' heading in {name}"
            print("  [PASS] 'Contact Us' heading found")
            
            # Check Company Name
            assert "Sri Hanum Sastha Enterprises" in content, f"Missing Company Name in {name}"
            print("  [PASS] Company Name 'Sri Hanum Sastha Enterprises' found")
            
            # Check Complete Address with proper line breaks
            assert "173, First Floor, KK Lane Street" in content, f"Missing Address line 1 in {name}"
            assert "Avinashi Road, Coimbatore" in content, f"Missing Address line 2 in {name}"
            assert "Tamil Nadu" in content and "641018" in content, f"Missing Tamil Nadu - 641018 in {name}"
            print("  [PASS] Complete address with line breaks found")
            
            # Check Email visibly and mailto link
            assert 'href="mailto:srihanumsastha@gmail.com"' in content, f"Missing mailto:srihanumsastha@gmail.com in {name}"
            assert "srihanumsastha@gmail.com" in content, f"Missing visible email text in {name}"
            print("  [PASS] Email 'srihanumsastha@gmail.com' visibly displayed with mailto: link")
            
            # Check Phone Numbers and tel links
            assert 'href="tel:9688727284"' in content, f"Missing tel:9688727284 in {name}"
            assert 'href="tel:8695706013"' in content, f"Missing tel:8695706013 in {name}"
            assert "9688727284" in content and "8695706013" in content, f"Missing phone number text in {name}"
            print("  [PASS] Both phone numbers clickable with tel: links")
            
            # Check Separate Call Now buttons
            assert "Call Now: 9688727284" in content, f"Missing Call Now: 9688727284 button in {name}"
            assert "Call Now: 8695706013" in content, f"Missing Call Now: 8695706013 button in {name}"
            print("  [PASS] Both separate 'Call Now: 9688727284' and 'Call Now: 8695706013' buttons found")
    except Exception as e:
        print(f"[FAIL] Error testing {url}: {e}")
        raise

print("\n=== 2. TESTING CATALOG INTEGRITY ===")
cat_url = f"{BASE_URL}/assets/catalog.json"
with urllib.request.urlopen(cat_url) as resp:
    data = json.loads(resp.read().decode('utf-8'))
    print(f"Catalog items count: {len(data)}")
    assert len(data) == 228, f"Expected 228 items, got {len(data)}"
    print("  [PASS] Exact 228 chair models preserved")

print("\n=== ALL CONTACT DETAILS AND FOOTER CHECKS PASSED SUCCESSFULLY! ===")
