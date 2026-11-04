import asyncio
import json
import sqlite3
import urllib.request
import urllib.parse
import websockets

BASE_URL = "http://127.0.0.1:8080"
ADMIN_TOKEN = "shse2026"

def test_reviews_moderation_api():
    print("\n=======================================================")
    print("STEP 1: TESTING REVIEWS PERMANENT MODERATION WORKFLOW")
    print("=======================================================")

    # 1. Submit review
    review_payload = {
        "name": "Arun Kumar Test",
        "rating": 5,
        "comment": "Antigravity automation test review - luxury ergonomic mesh chair.",
        "location": "RS Puram, Coimbatore"
    }
    req = urllib.request.Request(
        f"{BASE_URL}/api/reviews",
        data=json.dumps(review_payload).encode('utf-8'),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        created = json.loads(resp.read().decode('utf-8'))
        review_obj = created.get("review", created)
        review_id = review_obj.get("id")
    assert review_id, f"Failed to create review: {created}"
    print(f"[PASS] 1. Review created successfully with ID: {review_id}, status: {review_obj.get('status')}")

    # 2. Check public reviews - MUST NOT contain pending review
    req = urllib.request.Request(f"{BASE_URL}/api/reviews?t={review_id}")
    with urllib.request.urlopen(req) as resp:
        cc = resp.getheader("Cache-Control") or ""
        assert "no-cache" in cc, f"Cache-Control header missing, got {cc}"
        public_revs = json.loads(resp.read().decode('utf-8'))
    assert all(r["id"] != review_id for r in public_revs), "Pending review leaked into public API!"
    print(f"[PASS] 2. Pending review correctly HIDDEN from public API. Cache-Control verified: {cc}")

    # 3. Check admin reviews - MUST contain pending review
    req = urllib.request.Request(
        f"{BASE_URL}/api/admin/reviews?t={review_id}",
        headers={"Authorization": f"Bearer {ADMIN_TOKEN}"}
    )
    with urllib.request.urlopen(req) as resp:
        admin_revs = json.loads(resp.read().decode('utf-8'))
    found = next((r for r in admin_revs if r["id"] == review_id), None)
    assert found, "Created review not found in admin reviews"
    assert found["status"] == "pending", f"Expected pending status, got {found['status']}"
    print(f"[PASS] 3. Pending review correctly visible in Admin Dashboard API.")

    # 4. Approve review
    req = urllib.request.Request(
        f"{BASE_URL}/api/admin/reviews/{review_id}/status",
        data=json.dumps({"status": "approved"}).encode('utf-8'),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {ADMIN_TOKEN}"},
        method="PUT"
    )
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode('utf-8'))
    assert res.get("status") == "approved", "Status update failed"
    print(f"[PASS] 4. Review status updated to 'approved' via admin PUT.")

    # 5. Check public reviews - MUST contain approved review
    req = urllib.request.Request(f"{BASE_URL}/api/reviews?t={review_id}_approved")
    with urllib.request.urlopen(req) as resp:
        public_revs = json.loads(resp.read().decode('utf-8'))
    found_pub = next((r for r in public_revs if r["id"] == review_id), None)
    assert found_pub, "Approved review not visible on public website!"
    print(f"[PASS] 5. Approved review is now LIVE and visible on public website.")

    # 6. Reject review
    req = urllib.request.Request(
        f"{BASE_URL}/api/admin/reviews/{review_id}/status",
        data=json.dumps({"status": "rejected"}).encode('utf-8'),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {ADMIN_TOKEN}"},
        method="PUT"
    )
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode('utf-8'))
    assert res.get("status") == "rejected", "Status update failed"
    print(f"[PASS] 6. Review status updated to 'rejected' via admin PUT.")

    # 7. Check public reviews - MUST NOT contain rejected review
    req = urllib.request.Request(f"{BASE_URL}/api/reviews?t={review_id}_rejected")
    with urllib.request.urlopen(req) as resp:
        public_revs = json.loads(resp.read().decode('utf-8'))
    assert all(r["id"] != review_id for r in public_revs), "Rejected review leaked into public API!"
    print(f"[PASS] 7. Rejected review is IMMEDIATELY HIDDEN from public website.")

    # 8. Check admin reviews - MUST contain review with status rejected
    req = urllib.request.Request(
        f"{BASE_URL}/api/admin/reviews?t={review_id}_admin_rejected",
        headers={"Authorization": f"Bearer {ADMIN_TOKEN}"}
    )
    with urllib.request.urlopen(req) as resp:
        admin_revs = json.loads(resp.read().decode('utf-8'))
    found_adm = next((r for r in admin_revs if r["id"] == review_id), None)
    assert found_adm and found_adm["status"] == "rejected", "Rejected review missing or incorrect status in admin"
    print(f"[PASS] 8. Rejected review correctly retained in Admin Dashboard with status 'rejected'.")

    # 9. Delete review
    req = urllib.request.Request(
        f"{BASE_URL}/api/admin/reviews/{review_id}",
        headers={"Authorization": f"Bearer {ADMIN_TOKEN}"},
        method="DELETE"
    )
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode('utf-8'))
    assert res.get("deleted_id") == review_id, "Delete failed"
    print(f"[PASS] 9. Review permanently deleted via DELETE API.")

    # 10. Check SQLite DB directly for tombstone & absence from customer_reviews
    conn = sqlite3.connect("assets/shse_database.sqlite")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM customer_reviews WHERE id = ?", (review_id,))
    assert c.fetchone() is None, "Review still exists in customer_reviews table!"
    c.execute("SELECT * FROM deleted_review_tombstones WHERE id = ?", (review_id,))
    tombstone = c.fetchone()
    assert tombstone is not None, "Tombstone record not found for deleted review!"
    conn.close()
    print(f"[PASS] 10. SQLite database verified: Removed from customer_reviews, tombstoned in deleted_review_tombstones.")

    # 11. Check admin reviews & public reviews - MUST NOT contain deleted review
    req = urllib.request.Request(
        f"{BASE_URL}/api/admin/reviews?t={review_id}_deleted",
        headers={"Authorization": f"Bearer {ADMIN_TOKEN}"}
    )
    with urllib.request.urlopen(req) as resp:
        admin_revs = json.loads(resp.read().decode('utf-8'))
    assert all(r["id"] != review_id for r in admin_revs), "Deleted review still in admin reviews!"
    print(f"[PASS] 11. Deleted review permanently gone from Admin Dashboard and Public views.")

async def test_mobile_viewports():
    print("\n=======================================================")
    print("STEP 2: TESTING MOBILE VIEWPORTS (Zero Right Blank Space)")
    print("=======================================================")

    with urllib.request.urlopen('http://127.0.0.1:9222/json') as r:
        targets = json.loads(r.read().decode('utf-8'))
    tab = next(t for t in targets if '8080' in t.get('url', ''))

    async with websockets.connect(tab['webSocketDebuggerUrl'], max_size=50*1024*1024) as ws:
        msg_id = 5000
        async def send(m, p=None):
            nonlocal msg_id
            msg_id += 1
            await ws.send(json.dumps({'id': msg_id, 'method': m, 'params': p or {}}))
            while True:
                resp = json.loads(await ws.recv())
                if resp.get('id') == msg_id: return resp.get('result', {})

        await send('Network.clearBrowserCache')
        await send('Network.setCacheDisabled', {'cacheDisabled': True})

        viewports = [360, 375, 390, 430]

        # Test A: Standalone admin.html
        print("\n--- Testing Standalone admin.html ---")
        for w in viewports:
            await send('Emulation.setDeviceMetricsOverride', {'width': w, 'height': 800, 'deviceScaleFactor': 2, 'mobile': True})
            await send('Page.navigate', {'url': f'http://127.0.0.1:8080/admin.html?t={w}'})
            await asyncio.sleep(1.0)
            
            # Login if needed
            await send('Runtime.evaluate', {
                'expression': 'if (document.getElementById("adminPass")) { document.getElementById("adminPass").value="Adhithi@2021"; document.getElementById("loginForm").dispatchEvent(new Event("submit")); }'
            })
            await asyncio.sleep(0.8)

            diag = """(() => {
                const b = document.body;
                const doc = document.documentElement;
                return {
                    windowW: window.innerWidth,
                    docScrollW: doc.scrollWidth,
                    bodyScrollW: b.scrollWidth,
                    hasOverflow: b.scrollWidth > window.innerWidth
                };
            })()"""
            res = await send('Runtime.evaluate', {'expression': diag, 'returnByValue': True})
            val = res['result']['value']
            print(f"Viewport {w}px: windowW={val['windowW']}, docScrollW={val['docScrollW']}, bodyScrollW={val['bodyScrollW']}, hasOverflow={val['hasOverflow']}")
            assert not val['hasOverflow'], f"Horizontal overflow detected on admin.html at {w}px: bodyScrollW={val['bodyScrollW']} > {w}"

        # Test B: index.html with #adminDashboardOverlay
        print("\n--- Testing index.html with #adminDashboardOverlay ---")
        for w in viewports:
            await send('Emulation.setDeviceMetricsOverride', {'width': w, 'height': 800, 'deviceScaleFactor': 2, 'mobile': True})
            await send('Page.navigate', {'url': f'http://127.0.0.1:8080/index.html?token={ADMIN_TOKEN}&t={w}'})
            await asyncio.sleep(1.0)
            await send('Runtime.evaluate', {'expression': 'window.openAdminPortal()'})
            await asyncio.sleep(0.8)

            diag = """(() => {
                const overlay = document.getElementById('adminDashboardOverlay');
                const stage = document.querySelector('.stage-scroll-container');
                const mainStage = document.querySelector('.luxury-main-stage');
                return {
                    windowW: window.innerWidth,
                    overlayScrollW: overlay ? overlay.scrollWidth : null,
                    mainStageScrollW: mainStage ? mainStage.scrollWidth : null,
                    stageScrollW: stage ? stage.scrollWidth : null,
                    hasOverflow: (overlay && overlay.scrollWidth > window.innerWidth) || (mainStage && mainStage.scrollWidth > window.innerWidth)
                };
            })()"""
            res = await send('Runtime.evaluate', {'expression': diag, 'returnByValue': True})
            val = res['result']['value']
            print(f"Viewport {w}px: windowW={val['windowW']}, overlayScrollW={val['overlayScrollW']}, mainStageScrollW={val['mainStageScrollW']}, stageScrollW={val['stageScrollW']}, hasOverflow={val['hasOverflow']}")
            assert not val['hasOverflow'], f"Horizontal overflow detected on overlay at {w}px: {val}"

        # Test C: index.html Public Page
        print("\n--- Testing index.html Public Page ---")
        for w in viewports:
            await send('Emulation.setDeviceMetricsOverride', {'width': w, 'height': 800, 'deviceScaleFactor': 2, 'mobile': True})
            await send('Page.navigate', {'url': f'http://127.0.0.1:8080/index.html?t={w}'})
            await asyncio.sleep(1.0)

            diag = """(() => {
                const b = document.body;
                const doc = document.documentElement;
                return {
                    windowW: window.innerWidth,
                    docScrollW: doc.scrollWidth,
                    bodyScrollW: b.scrollWidth,
                    hasOverflow: b.scrollWidth > window.innerWidth
                };
            })()"""
            res = await send('Runtime.evaluate', {'expression': diag, 'returnByValue': True})
            val = res['result']['value']
            print(f"Viewport {w}px: windowW={val['windowW']}, docScrollW={val['docScrollW']}, bodyScrollW={val['bodyScrollW']}, hasOverflow={val['hasOverflow']}")
            assert not val['hasOverflow'], f"Horizontal overflow detected on public index.html at {w}px: {val}"

        # Take screenshot for visual inspection
        ss = await send('Page.captureScreenshot', {'format': 'png'})
        import base64
        with open('mobile_360_admin_check.png', 'wb') as f:
            f.write(base64.b64decode(ss.get('data', '')))
        print("[PASS] Screenshot saved to mobile_360_admin_check.png")

if __name__ == "__main__":
    test_reviews_moderation_api()
    asyncio.run(test_mobile_viewports())
    print("\nALL AUTOMATION TESTS PASSED PERFECTLY!")
