import asyncio
import json
import urllib.request
import websockets
import base64

async def capture_screenshots():
    with urllib.request.urlopen('http://127.0.0.1:9222/json') as r:
        targets = json.loads(r.read().decode('utf-8'))
    tab = next(t for t in targets if '8080' in t.get('url', ''))

    async with websockets.connect(tab['webSocketDebuggerUrl'], max_size=50*1024*1024) as ws:
        msg_id = 17000
        async def send(m, p=None):
            nonlocal msg_id
            msg_id += 1
            await ws.send(json.dumps({'id': msg_id, 'method': m, 'params': p or {}}))
            while True:
                resp = json.loads(await ws.recv())
                if resp.get('id') == msg_id: return resp.get('result', {})

        # 1. Desktop screenshot of admin.html customer reviews
        await send('Emulation.setDeviceMetricsOverride', {'width': 1280, 'height': 850, 'deviceScaleFactor': 1, 'mobile': False})
        await send('Page.navigate', {'url': 'http://127.0.0.1:8080/admin.html?token=shse2026'})
        await asyncio.sleep(2.0)
        shot1 = await send('Page.captureScreenshot', {'format': 'png'})
        with open('admin_reviews_desktop_fixed.png', 'wb') as f:
            f.write(base64.b64decode(shot1['data']))
        print("Captured: admin_reviews_desktop_fixed.png")

        # 2. Mobile screenshot of admin.html customer reviews (375px)
        await send('Emulation.setDeviceMetricsOverride', {'width': 375, 'height': 750, 'deviceScaleFactor': 2, 'mobile': True})
        await send('Page.navigate', {'url': 'http://127.0.0.1:8080/admin.html?token=shse2026'})
        await asyncio.sleep(2.0)
        shot2 = await send('Page.captureScreenshot', {'format': 'png'})
        with open('admin_reviews_mobile_fixed.png', 'wb') as f:
            f.write(base64.b64decode(shot2['data']))
        print("Captured: admin_reviews_mobile_fixed.png")

        # 3. Desktop screenshot of index.html overlay customer reviews
        await send('Emulation.setDeviceMetricsOverride', {'width': 1280, 'height': 850, 'deviceScaleFactor': 1, 'mobile': False})
        await send('Page.navigate', {'url': 'http://127.0.0.1:8080/index.html?token=shse2026'})
        await asyncio.sleep(1.5)
        await send('Runtime.evaluate', {'expression': 'window.openAdminPortal && window.openAdminPortal()'})
        await asyncio.sleep(1.5)
        shot3 = await send('Page.captureScreenshot', {'format': 'png'})
        with open('admin_overlay_reviews_fixed.png', 'wb') as f:
            f.write(base64.b64decode(shot3['data']))
        print("Captured: admin_overlay_reviews_fixed.png")

        # Reset emulation
        await send('Emulation.clearDeviceMetricsOverride')

asyncio.run(capture_screenshots())
