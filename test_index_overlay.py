import asyncio
import json
import urllib.request
import websockets

async def check_index_overlay_reviews():
    with urllib.request.urlopen('http://127.0.0.1:9222/json') as r:
        targets = json.loads(r.read().decode('utf-8'))
    tab = next(t for t in targets if '8080' in t.get('url', ''))

    async with websockets.connect(tab['webSocketDebuggerUrl'], max_size=50*1024*1024) as ws:
        msg_id = 16000
        async def send(m, p=None):
            nonlocal msg_id
            msg_id += 1
            await ws.send(json.dumps({'id': msg_id, 'method': m, 'params': p or {}}))
            while True:
                resp = json.loads(await ws.recv())
                if resp.get('id') == msg_id: return resp.get('result', {})

        print("Navigating to http://127.0.0.1:8080/index.html?token=shse2026 ...")
        await send('Page.navigate', {'url': 'http://127.0.0.1:8080/index.html?token=shse2026'})
        await asyncio.sleep(2.0)

        # Open admin portal overlay
        open_overlay_js = """(() => {
            if (window.openAdminPortal) {
                window.openAdminPortal();
                return { success: true };
            }
            return { error: 'openAdminPortal not found' };
        })()"""
        r = await send('Runtime.evaluate', {'expression': open_overlay_js, 'returnByValue': True})
        print("openAdminPortal:", r.get('result', {}).get('value'))
        await asyncio.sleep(1.0)

        # Check rows in #dashReviewsTbody
        check_overlay_rows = """(() => {
            const tbody = document.getElementById('dashReviewsTbody');
            const rows = tbody ? tbody.querySelectorAll('tr') : [];
            const stats = {
                total: document.getElementById('dashStatReviewsTotal')?.textContent,
                pending: document.getElementById('dashStatReviewsPending')?.textContent,
                approved: document.getElementById('dashStatReviewsApproved')?.textContent,
                rejected: document.getElementById('dashStatReviewsRejected')?.textContent,
            };
            const rowData = Array.from(rows).map(tr => {
                const tds = tr.querySelectorAll('td');
                if (tds.length < 6) return null;
                return {
                    customer: tds[1].innerText.trim(),
                    rating: tds[2].innerText.trim(),
                    status: tds[4].innerText.trim(),
                    buttons: tds[5].querySelectorAll('button').length
                };
            }).filter(Boolean);
            return {
                rowCount: rows.length,
                stats: stats,
                reviews: rowData
            };
        })()"""
        res = await send('Runtime.evaluate', {'expression': check_overlay_rows, 'returnByValue': True})
        data = res.get('result', {}).get('value', {})
        print("Overlay Portal Data:")
        print(json.dumps(data, indent=2))
        assert data['rowCount'] == 3, f"Expected 3 rows in overlay table, got {data['rowCount']}"
        print("  [PASS] Index.html integrated Admin Overlay reviews table renders perfectly with 3 rows!")

asyncio.run(check_index_overlay_reviews())
