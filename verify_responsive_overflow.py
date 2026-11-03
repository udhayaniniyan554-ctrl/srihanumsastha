# verify_responsive_overflow.py
import asyncio
import json
import urllib.request
import websockets

async def test_all_responsive():
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

        widths = [360, 375, 390, 430, 768, 1200]
        pages = [
            'index.html',
            'category.html?cat=office',
            'category.html?cat=visitor',
            'product.html?id=office_1_2',
            'contact.html',
            'admin.html'
        ]

        print("==================================================================")
        print("     RESPONSIVE OVERFLOW AUDIT ACROSS ALL VIEWPORT SIZES          ")
        print("==================================================================")

        all_passed = True
        for w in widths:
            is_mobile = w <= 768
            await send('Emulation.setDeviceMetricsOverride', {'width': w, 'height': 850, 'deviceScaleFactor': 2, 'mobile': is_mobile})
            for p in pages:
                await send('Page.navigate', {'url': f'http://127.0.0.1:8080/{p}'})
                await asyncio.sleep(0.8)
                js = """(() => {
                    const docWidth = window.innerWidth;
                    const docScrollW = document.documentElement.scrollWidth;
                    const bodyScrollW = document.body.scrollWidth;
                    return {
                        innerWidth: docWidth,
                        docScrollW: docScrollW,
                        bodyScrollW: bodyScrollW,
                        hasOverflow: docScrollW > docWidth
                    };
                })()"""
                res = await send('Runtime.evaluate', {'expression': js, 'returnByValue': True})
                val = res['result']['value']
                has_of = val['hasOverflow']
                status = "[PASS]" if not has_of else "[FAIL]"
                if has_of: all_passed = False
                print(f"  {status} {p:<30} at {w}px: innerW={val['innerWidth']}, scrollW={val['docScrollW']}, overflow={val['hasOverflow']}")

        print("==================================================================")
        if all_passed:
            print("  ALL PAGES PASSED RESPONSIVE AUDIT WITH ZERO OVERFLOW!")
        else:
            print("  FAILURES DETECTED!")
        print("==================================================================")

asyncio.run(test_all_responsive())
