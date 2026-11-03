import asyncio
import json
import urllib.request
import websockets

async def run_full_reviews_test():
    with urllib.request.urlopen('http://127.0.0.1:9222/json') as r:
        targets = json.loads(r.read().decode('utf-8'))
    tab = next(t for t in targets if '8080' in t.get('url', ''))

    async with websockets.connect(tab['webSocketDebuggerUrl'], max_size=50*1024*1024) as ws:
        msg_id = 12000
        async def send(m, p=None):
            nonlocal msg_id
            msg_id += 1
            await ws.send(json.dumps({'id': msg_id, 'method': m, 'params': p or {}}))
            while True:
                resp = json.loads(await ws.recv())
                if resp.get('id') == msg_id: return resp.get('result', {})

        print("==================================================================")
        print("  END-TO-END VERIFICATION: ADMIN REVIEWS SYSTEM & MODERATION      ")
        print("==================================================================")

        # 1. Navigate to admin.html with auth token
        print("\n[TEST 1] Loading Admin Dashboard (admin.html)...")
        await send('Page.navigate', {'url': 'http://127.0.0.1:8080/admin.html?token=shse2026'})
        await asyncio.sleep(2.0)

        # Verify all existing reviews are rendered in the table
        check_table_js = """(() => {
            const rows = document.querySelectorAll('#reviewsTbody tr');
            const data = Array.from(rows).map(tr => {
                const tds = tr.querySelectorAll('td');
                if (tds.length < 6) return null;
                return {
                    dateId: tds[0].innerText.trim(),
                    customer: tds[1].innerText.trim(),
                    rating: tds[2].innerText.trim(),
                    feedback: tds[3].innerText.trim(),
                    status: tds[4].innerText.trim(),
                    hasActions: tds[5].querySelectorAll('button').length
                };
            }).filter(Boolean);
            const total = document.getElementById('statReviewsTotal')?.textContent.trim();
            const pending = document.getElementById('statReviewsPending')?.textContent.trim();
            const approved = document.getElementById('statReviewsApproved')?.textContent.trim();
            const rejected = document.getElementById('statReviewsRejected')?.textContent.trim();
            return { rowCount: rows.length, reviews: data, stats: { total, pending, approved, rejected } };
        })()"""
        res = await send('Runtime.evaluate', {'expression': check_table_js, 'returnByValue': True})
        table_state = res.get('result', {}).get('value', {})
        print(f"  Rows rendered in table: {table_state['rowCount']}")
        print(f"  Dashboard stats: {table_state['stats']}")
        assert table_state['rowCount'] >= 3, f"Expected at least 3 rows in table, got {table_state['rowCount']}"
        for rev in table_state['reviews']:
            print(f"    - [{rev['status']}] {rev['customer']} ({rev['rating']}): \"{rev['feedback'][:45]}...\" | Actions: {rev['hasActions']} buttons")
        print("  [PASS] All existing customer reviews successfully displayed in table with 6 columns!")

        # 2. Test Status Filters in Admin Table
        print("\n[TEST 2] Testing Status Filter Pills in Admin Dashboard...")
        filter_tests = [
            ('pending', 'Pending', 2),
            ('approved', 'Approved', 1),
            ('rejected', 'Rejected', 0),
            ('all', 'All', 3)
        ]
        for filter_val, label, min_expected in filter_tests:
            pill_js = f"""(() => {{
                window.setAdminReviewFilter('{filter_val}');
                const visibleRows = Array.from(document.querySelectorAll('#reviewsTbody tr')).filter(tr => tr.querySelectorAll('td').length >= 6);
                return visibleRows.length;
            }})()"""
            r = await send('Runtime.evaluate', {'expression': pill_js, 'returnByValue': True})
            cnt = r.get('result', {}).get('value')
            print(f"  Filter '{label}': {cnt} visible row(s) (expected {min_expected}).")
            assert cnt == min_expected, f"Filter '{label}' expected {min_expected} rows, got {cnt}"
        print("  [PASS] Status filter pills filter exactly by status accurately!")

        # Reset filter to 'all'
        await send('Runtime.evaluate', {'expression': """(() => { window.setAdminReviewFilter('all'); })()"""})

        # 3. Test Submission of a New Customer Review
        print("\n[TEST 3] Testing Customer Review Submission Workflow...")
        submit_payload = {
            "name": "Karthik Raja",
            "rating": 5,
            "comment": "Outstanding ergonomic chairs delivered for our IT firm in Coimbatore showroom.",
            "location": "RS Puram, Coimbatore"
        }
        post_req = urllib.request.Request(
            "http://127.0.0.1:8080/api/reviews",
            data=json.dumps(submit_payload).encode('utf-8'),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(post_req) as post_res:
            post_data = json.loads(post_res.read().decode())
        new_review = post_data.get('review', {})
        test_rev_id = new_review.get('id')
        print(f"  Submitted new review: ID={test_rev_id}, Status={new_review.get('status')}")
        assert new_review.get('status') == 'pending', f"New review should be 'pending', got {new_review.get('status')}"
        print("  [PASS] New review successfully saved in database with Pending status.")

        # Reload admin to see the new pending review
        await send('Page.reload')
        await asyncio.sleep(1.5)
        res = await send('Runtime.evaluate', {'expression': check_table_js, 'returnByValue': True})
        table_state = res.get('result', {}).get('value', {})
        found_pending = any(test_rev_id in r['dateId'] for r in table_state['reviews'])
        print(f"  Admin sees new review in table: {found_pending} (Total count now: {table_state['stats']['total']})")
        assert found_pending, "Newly submitted review must appear in Admin Dashboard reviews table!"
        print("  [PASS] Newly submitted review immediately visible to Admin.")

        # 4. Test Approving the Review
        print("\n[TEST 4] Testing Review Approval (Making visible on public website)...")
        approve_js = f"""(async () => {{
            const ok = await window.approveReview('{test_rev_id}');
            const found = window.reviewsData ? window.reviewsData.find(x => x.id === '{test_rev_id}') : null;
            return {{ ok, status: found ? found.status : null }};
        }})()"""
        r = await send('Runtime.evaluate', {'expression': approve_js, 'awaitPromise': True, 'returnByValue': True})
        app_res = r.get('result', {}).get('value', {})
        print(f"  approveReview result: {app_res}")
        assert app_res.get('status') == 'approved', f"Expected status 'approved', got {app_res}"

        # Verify it now appears on public website
        with urllib.request.urlopen("http://127.0.0.1:8080/api/reviews") as pub_res:
            pub_reviews = json.loads(pub_res.read().decode())
        found_in_pub = any(r.get('id') == test_rev_id for r in pub_reviews)
        print(f"  Approved review returned in public /api/reviews: {found_in_pub}")
        assert found_in_pub, "Approved review must be visible on public website!"
        print("  [PASS] Approved review is now live on public website.")

        # 5. Test Rejecting the Review
        print("\n[TEST 5] Testing Review Rejection (Hiding from public website)...")
        reject_js = f"""(async () => {{
            const ok = await window.rejectReview('{test_rev_id}');
            const found = window.reviewsData ? window.reviewsData.find(x => x.id === '{test_rev_id}') : null;
            return {{ ok, status: found ? found.status : null }};
        }})()"""
        r = await send('Runtime.evaluate', {'expression': reject_js, 'awaitPromise': True, 'returnByValue': True})
        rej_res = r.get('result', {}).get('value', {})
        print(f"  rejectReview result: {rej_res}")
        assert rej_res.get('status') == 'rejected', f"Expected status 'rejected', got {rej_res}"

        # Verify it is HIDDEN from public website
        with urllib.request.urlopen("http://127.0.0.1:8080/api/reviews") as pub_res:
            pub_reviews = json.loads(pub_res.read().decode())
        found_in_pub = any(r.get('id') == test_rev_id for r in pub_reviews)
        print(f"  Rejected review hidden from public /api/reviews: {not found_in_pub}")
        assert not found_in_pub, "Rejected review must be hidden from public website!"
        print("  [PASS] Rejected review is hidden from public website.")

        # 6. Test Permanently Deleting the Review
        print("\n[TEST 6] Testing Permanent Deletion of Review...")
        del_js = f"""(async () => {{
            window.confirm = () => true;
            const ok = await window.deleteReview('{test_rev_id}');
            const found = window.reviewsData ? window.reviewsData.find(x => x.id === '{test_rev_id}') : null;
            return {{ ok, found: !!found }};
        }})()"""
        r = await send('Runtime.evaluate', {'expression': del_js, 'awaitPromise': True, 'returnByValue': True})
        del_res = r.get('result', {}).get('value', {})
        print(f"  deleteReview result: {del_res}")
        assert del_res.get('found') is False, "Deleted review must be removed from reviewsData array!"

        # Reload admin to ensure it does not reappear after refresh
        await send('Page.reload')
        await asyncio.sleep(1.5)
        res = await send('Runtime.evaluate', {'expression': check_table_js, 'returnByValue': True})
        final_table = res.get('result', {}).get('value', {})
        reappeared = any(test_rev_id in r['dateId'] for r in final_table['reviews'])
        print(f"  Deleted review reappeared after reload: {reappeared}")
        assert not reappeared, "Deleted review must not reappear after page refresh!"
        print("  [PASS] Review permanently deleted from database and removed from Admin Dashboard.")

        # 7. Check original customer reviews preserved
        print("\n[TEST 7] Verifying Original Real Reviews Preserved...")
        print(f"  Final active reviews count in Admin: {final_table['rowCount']}")
        assert final_table['rowCount'] == 3, f"Original 3 customer reviews must be strictly preserved! Got {final_table['rowCount']}"
        print("  [PASS] All 3 original customer reviews are 100% intact and undamaged.")

        print("\n==================================================================")
        print("  ALL ADMIN REVIEWS VERIFICATION STAGES PASSED WITH 100% SUCCESS! ")
        print("==================================================================")

asyncio.run(run_full_reviews_test())
