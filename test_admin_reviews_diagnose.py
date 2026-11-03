import asyncio
import json
import urllib.request
import websockets

async def diagnose_admin_reviews():
    with urllib.request.urlopen('http://127.0.0.1:9222/json') as r:
        targets = json.loads(r.read().decode('utf-8'))
    tab = next(t for t in targets if '8080' in t.get('url', ''))

    async with websockets.connect(tab['webSocketDebuggerUrl'], max_size=50*1024*1024) as ws:
        msg_id = 9600
        async def send(m, p=None):
            nonlocal msg_id
            msg_id += 1
            await ws.send(json.dumps({'id': msg_id, 'method': m, 'params': p or {}}))
            while True:
                resp = json.loads(await ws.recv())
                if resp.get('id') == msg_id: return resp.get('result', {})

        # Enable Log and Runtime to catch console errors
        await send('Log.enable')
        await send('Runtime.enable')

        # Navigate to admin.html with token
        print("Navigating to http://127.0.0.1:8080/admin.html?token=shse2026 ...")
        await send('Page.navigate', {'url': 'http://127.0.0.1:8080/admin.html?token=shse2026'})
        await asyncio.sleep(2.0)

        # Evaluate what's happening on admin.html
        eval_script = """(() => {
            const tbody = document.getElementById('reviewsTbody');
            const rows = tbody ? tbody.querySelectorAll('tr') : [];
            const stats = {
                total: document.getElementById('statReviewsTotal')?.textContent,
                pending: document.getElementById('statReviewsPending')?.textContent,
                approved: document.getElementById('statReviewsApproved')?.textContent,
                rejected: document.getElementById('statReviewsRejected')?.textContent,
            };
            return {
                reviewsDataLength: typeof reviewsData !== 'undefined' ? reviewsData.length : 'undefined',
                tbodyHtml: tbody ? tbody.innerHTML : null,
                rowCount: rows.length,
                stats: stats
            };
        })()"""
        res = await send('Runtime.evaluate', {'expression': eval_script, 'returnByValue': True})
        print("ADMIN.HTML RESULT:")
        print(json.dumps(res.get('result', {}).get('value', {}), indent=2))

asyncio.run(diagnose_admin_reviews())
