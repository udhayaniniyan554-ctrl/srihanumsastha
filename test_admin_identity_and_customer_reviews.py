import asyncio
import json
import sqlite3
import urllib.request
import websockets

BASE_URL = "http://127.0.0.1:8080"
ADMIN_TOKEN = "shse2026"

def test_backend_and_database():
    print("\n=======================================================")
    print("PHASE 1: VERIFYING SEPARATION OF ADMIN & CUSTOMER DATA")
    print("=======================================================")

    # 1. Check SQLite customer_reviews table
    conn = sqlite3.connect("assets/shse_database.sqlite")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT id, name, status, rating, comment, location FROM customer_reviews ORDER BY created_at DESC")
    db_reviews = [dict(r) for r in c.fetchall()]
    conn.close()

    print(f"Found {len(db_reviews)} customer reviews in SQLite:")
    for r in db_reviews:
        print(f"  - [{r['status']}] Customer: '{r['name']}', Location: '{r['location']}'")
        # Ensure no customer review is named Priya Sathiyaraj
        assert r['name'] != "Priya Sathiyaraj", "Customer review mistakenly named Priya Sathiyaraj!"

    # Verify genuine customer names exist
    names = [r['name'] for r in db_reviews]
    assert "Priya Shankar" in names, "Genuine customer review 'Priya Shankar' missing from database!"
    assert "Udhayan" in names, "Genuine customer review 'Udhayan' missing from database!"
    print("[PASS] 1. SQLite database contains genuine customer records with their own distinct names.")

    # 2. Check public reviews API endpoint
    req = urllib.request.Request(f"{BASE_URL}/api/reviews?t=verify_sep")
    with urllib.request.urlopen(req) as resp:
        pub_revs = json.loads(resp.read().decode('utf-8'))
    print(f"Public API returned {len(pub_revs)} approved review(s):")
    for r in pub_revs:
        print(f"  - Customer: '{r['name']}', Rating: {r['rating']} Stars, Comment: '{r['comment'][:40]}...'")
        assert r['status'] == "approved", "Unapproved review returned publicly!"
        assert r['name'] != "Priya Sathiyaraj", "Public review mistakenly named administrator name!"
    print("[PASS] 2. Public reviews API endpoint returns only approved reviews with genuine customer names.")

    # 3. Check admin reviews API endpoint
    req = urllib.request.Request(
        f"{BASE_URL}/api/admin/reviews?t=verify_admin",
        headers={"Authorization": f"Bearer {ADMIN_TOKEN}"}
    )
    with urllib.request.urlopen(req) as resp:
        admin_revs = json.loads(resp.read().decode('utf-8'))
    print(f"Admin API returned {len(admin_revs)} review(s):")
    admin_names = [r['name'] for r in admin_revs]
    assert "Priya Shankar" in admin_names, "Customer 'Priya Shankar' missing in admin API!"
    assert "Udhayan" in admin_names, "Customer 'Udhayan' missing in admin API!"
    print("[PASS] 3. Admin reviews API returns all reviews with original customer names.")

    # 4. Verify login credentials remain unchanged
    login_payload = json.dumps({"username": "Priya", "password": "Adhithi@2021"}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/api/admin/login", data=login_payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as resp:
        login_res = json.loads(resp.read().decode('utf-8'))
    assert login_res.get("success"), "Login failed with Priya / Adhithi@2021"
    print("[PASS] 4. Existing login credentials (Priya / Adhithi@2021) authenticated successfully.")

async def test_frontend_dom_elements():
    print("\n=======================================================")
    print("PHASE 2: VERIFYING FRONTEND ADMIN DISPLAY & CUSTOMER NAMES")
    print("=======================================================")

    with urllib.request.urlopen('http://127.0.0.1:9222/json') as r:
        targets = json.loads(r.read().decode('utf-8'))
    tab = next(t for t in targets if '8080' in t.get('url', ''))

    async with websockets.connect(tab['webSocketDebuggerUrl'], max_size=50*1024*1024) as ws:
        msg_id = 7000
        async def send(m, p=None):
            nonlocal msg_id
            msg_id += 1
            await ws.send(json.dumps({'id': msg_id, 'method': m, 'params': p or {}}))
            while True:
                resp = json.loads(await ws.recv())
                if resp.get('id') == msg_id: return resp.get('result', {})

        await send('Network.clearBrowserCache')
        await send('Network.setCacheDisabled', {'cacheDisabled': True})

        # Test A: Standalone admin.html
        print("\n--- Inspecting Standalone admin.html ---")
        await send('Emulation.setDeviceMetricsOverride', {'width': 1200, 'height': 800, 'deviceScaleFactor': 1, 'mobile': False})
        await send('Page.navigate', {'url': 'http://127.0.0.1:8080/admin.html?t=test_standalone'})
        await asyncio.sleep(1.0)
        # Login
        await send('Runtime.evaluate', {
            'expression': 'if (document.getElementById("adminPass")) { document.getElementById("adminPass").value="Adhithi@2021"; document.getElementById("loginForm").dispatchEvent(new Event("submit")); }'
        })
        await asyncio.sleep(1.0)

        diag_admin_html = """(() => {
            const profileHeader = document.querySelector('.admin-profile-header-card');
            const navBadge = document.querySelector('.admin-exec-badge');
            const reviewsRows = Array.from(document.querySelectorAll('#reviewsTbody tr')).map(tr => {
                const customerEl = tr.querySelector('td:nth-child(2) strong');
                return customerEl ? customerEl.textContent.trim() : null;
            }).filter(Boolean);

            return {
                profileHeaderHtml: profileHeader ? profileHeader.innerText : null,
                navBadgeText: navBadge ? navBadge.innerText : null,
                customerNamesInTable: reviewsRows
            };
        })()"""
        res = await send('Runtime.evaluate', {'expression': diag_admin_html, 'returnByValue': True})
        val = res['result']['value']
        print(f"admin.html Nav Badge: {val['navBadgeText']}")
        print(f"admin.html Profile Header Card snippet: {val['profileHeaderHtml'][:120] if val['profileHeaderHtml'] else 'NONE'}")
        print(f"admin.html Customer Names in Review Table: {val['customerNamesInTable']}")

        assert val['profileHeaderHtml'] and "Priya Sathiyaraj" in val['profileHeaderHtml'], "Priya Sathiyaraj missing in admin.html profile card"
        assert val['profileHeaderHtml'] and "Executive Administrator" in val['profileHeaderHtml'], "Executive Administrator missing in admin.html profile card"
        assert val['navBadgeText'] and "Priya Sathiyaraj" in val['navBadgeText'], "Priya Sathiyaraj missing in admin.html navbar badge"
        assert val['navBadgeText'] and "Executive Administrator" in val['navBadgeText'], "Executive Administrator missing in admin.html navbar badge"

        # Verify customer review table shows genuine customer names (not Priya Sathiyaraj!)
        assert "Priya Shankar" in val['customerNamesInTable'], "Customer 'Priya Shankar' missing from review table in admin.html"
        assert "Udhayan" in val['customerNamesInTable'], "Customer 'Udhayan' missing from review table in admin.html"
        assert "Priya Sathiyaraj" not in val['customerNamesInTable'], "Administrator Priya Sathiyaraj mistakenly placed in review records!"
        print("[PASS] Standalone admin.html correctly displays Priya Sathiyaraj as Executive Administrator and genuine customer names in review table.")

        # Test B: Executive Overlay in index.html
        print("\n--- Inspecting index.html Luxury Admin Overlay ---")
        await send('Page.navigate', {'url': f'http://127.0.0.1:8080/index.html?token={ADMIN_TOKEN}&t=test_overlay'})
        await asyncio.sleep(1.0)
        await send('Runtime.evaluate', {'expression': 'window.openAdminPortal()'})
        await asyncio.sleep(1.0)

        diag_overlay = """(() => {
            const sidebarName = document.querySelector('.admin-profile-name')?.textContent.trim();
            const sidebarRole = document.querySelector('.admin-profile-role')?.textContent.trim();
            const topNavBadge = document.querySelector('.admin-exec-badge')?.innerText;
            const heroWelcome = document.querySelector('.hero-welcome-badge')?.innerText;
            const dashRows = Array.from(document.querySelectorAll('#dashReviewsTbody tr')).map(tr => {
                const nameEl = tr.querySelector('td:nth-child(2) strong');
                return nameEl ? nameEl.textContent.trim() : null;
            }).filter(Boolean);

            return {
                sidebarName,
                sidebarRole,
                topNavBadge,
                heroWelcome,
                customerNamesInDashTable: dashRows
            };
        })()"""
        res = await send('Runtime.evaluate', {'expression': diag_overlay, 'returnByValue': True})
        val = res['result']['value']
        print(f"Overlay Sidebar Profile Name: '{val['sidebarName']}'")
        print(f"Overlay Sidebar Role: '{val['sidebarRole']}'")
        print(f"Overlay Top Nav Badge: '{val['topNavBadge']}'")
        print(f"Overlay Welcome Greeting: '{val['heroWelcome']}'")
        print(f"Overlay Customer Names in Review Table: {val['customerNamesInDashTable']}")

        assert val['sidebarName'] == "Priya Sathiyaraj", f"Expected 'Priya Sathiyaraj', got '{val['sidebarName']}'"
        assert val['sidebarRole'] == "Executive Administrator", f"Expected 'Executive Administrator', got '{val['sidebarRole']}'"
        assert val['topNavBadge'] and "Priya Sathiyaraj" in val['topNavBadge'], "Priya Sathiyaraj missing in top nav badge"
        assert val['heroWelcome'] and "priya sathiyaraj" in val['heroWelcome'].lower(), "Priya Sathiyaraj missing in hero welcome greeting"
        assert val['heroWelcome'] and "executive administrator" in val['heroWelcome'].lower(), "Executive Administrator missing in hero welcome"

        # Verify customer review table shows genuine customer names (not Priya Sathiyaraj!)
        assert "Priya Shankar" in val['customerNamesInDashTable'], "Customer 'Priya Shankar' missing from review table in overlay"
        assert "Udhayan" in val['customerNamesInDashTable'], "Customer 'Udhayan' missing from review table in overlay"
        assert "Priya Sathiyaraj" not in val['customerNamesInDashTable'], "Administrator Priya Sathiyaraj mistakenly placed in review records!"
        print("[PASS] Luxury Admin Overlay correctly displays Priya Sathiyaraj as Executive Administrator and genuine customer names in review table.")

        # Test C: Public Customer Reviews on index.html
        print("\n--- Inspecting Public Customer Reviews on index.html ---")
        await send('Page.navigate', {'url': 'http://127.0.0.1:8080/index.html#reviews'})
        await asyncio.sleep(1.0)

        diag_public = """(() => {
            const cards = Array.from(document.querySelectorAll('.review-card')).map(card => {
                const name = card.querySelector('.review-author-name')?.textContent.trim();
                const loc = card.querySelector('.review-user-sub')?.textContent.trim();
                return { name, loc };
            });
            return cards;
        })()"""
        res = await send('Runtime.evaluate', {'expression': diag_public, 'returnByValue': True})
        cards = res['result']['value']
        print(f"Public Review Cards Rendered ({len(cards)}): {cards}")
        for c in cards:
            assert c['name'] != "Priya Sathiyaraj", "Administrator name mistakenly rendered in public customer review!"
        assert any(c['name'] == "Priya Shankar" for c in cards), "Customer 'Priya Shankar' approved review missing from public website!"
        print("[PASS] Public Customer Reviews correctly display actual customer names ('Priya Shankar', etc.) and NEVER administrator Priya Sathiyaraj.")

        # Test D: Mobile 360px Viewport Audit
        print("\n--- Mobile 360px Viewport Audit Post-Changes ---")
        await send('Emulation.setDeviceMetricsOverride', {'width': 360, 'height': 800, 'deviceScaleFactor': 2, 'mobile': True})
        
        # Standalone admin.html
        await send('Page.navigate', {'url': 'http://127.0.0.1:8080/admin.html?t=mob_check'})
        await asyncio.sleep(1.0)
        res = await send('Runtime.evaluate', {'expression': 'document.body.scrollWidth', 'returnByValue': True})
        sw = res['result']['value']
        print(f"Mobile 360px Standalone admin.html bodyScrollWidth: {sw} (Must be <= 360)")
        assert sw <= 360, f"admin.html overflowed on 360px: {sw}"

        # Overlay
        await send('Page.navigate', {'url': f'http://127.0.0.1:8080/index.html?token={ADMIN_TOKEN}&t=mob_overlay'})
        await asyncio.sleep(1.0)
        await send('Runtime.evaluate', {'expression': 'window.openAdminPortal()'})
        await asyncio.sleep(1.0)
        res = await send('Runtime.evaluate', {'expression': 'document.getElementById("adminDashboardOverlay").scrollWidth', 'returnByValue': True})
        osw = res['result']['value']
        print(f"Mobile 360px Overlay scrollWidth: {osw} (Must be <= 360)")
        assert osw <= 360, f"Overlay overflowed on 360px: {osw}"
        print("[PASS] Both Admin Dashboards maintain ZERO horizontal overflow at 360px mobile width.")

if __name__ == "__main__":
    test_backend_and_database()
    asyncio.run(test_frontend_dom_elements())
    print("\n=======================================================")
    print("ALL TESTS PASSED: ADMIN AND CUSTOMER SEPARATION VERIFIED!")
    print("=======================================================")
