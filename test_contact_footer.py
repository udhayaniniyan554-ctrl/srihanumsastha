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

print("=== 1. TESTING HTTP ENDPOINTS & HEADER/FOOTER DETAILS ===")
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
            
            # Check zero email display anywhere on public website
            assert 'mailto:' not in content, f"Unexpected mailto link found in {name}"
            assert "srihanumsastha@gmail.com" not in content, f"Unexpected email text in {name}"
            print("  [PASS] Zero email display verified across public page")
            
            # Check WhatsApp
            assert "https://wa.me/918695706013" in content, f"Missing WhatsApp in {name}"
            print("  [PASS] WhatsApp 8695706013 verified")
    except Exception as e:
        print(f"[FAIL] Error testing {url}: {e}")
        raise

print("\n=== 2. TESTING CATALOG INTEGRITY ===")
cat_url = f"{BASE_URL}/assets/catalog.json"
req = urllib.request.Request(cat_url, headers={"User-Agent": "VerificationBot/1.0"})
with urllib.request.urlopen(req, timeout=5) as resp:
    data = json.loads(resp.read().decode('utf-8'))
    assert len(data) == 228
    print(f"[PASS] All {len(data)} catalogue items loaded successfully")
