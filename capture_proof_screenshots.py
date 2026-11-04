import asyncio
import base64
import json
import os
import urllib.request
import websockets

ARTIFACT_DIR = r"C:\Users\user\.gemini\antigravity\brain\fc8bd55f-e93a-4611-bc32-454569cca86d"

async def capture_screenshots():
    with urllib.request.urlopen('http://127.0.0.1:9222/json') as r:
        targets = json.loads(r.read().decode('utf-8'))
    tab = next(t for t in targets if '8080' in t.get('url', ''))

    async with websockets.connect(tab['webSocketDebuggerUrl'], max_size=50*1024*1024) as ws:
        msg_id = 15000
        async def send(m, p=None):
            nonlocal msg_id
            msg_id += 1
            await ws.send(json.dumps({'id': msg_id, 'method': m, 'params': p or {}}))
            while True:
                resp = json.loads(await ws.recv())
                if resp.get('id') == msg_id: return resp.get('result', {})

        # 1. Desktop Slider & Header (1200px)
        await send('Emulation.setDeviceMetricsOverride', {'width': 1280, 'height': 820, 'deviceScaleFactor': 1, 'mobile': False})
        await send('Page.navigate', {'url': 'http://127.0.0.1:8080/index.html?t=desktop_shot'})
        await asyncio.sleep(1.2)
        shot1 = await send('Page.captureScreenshot', {'format': 'png'})
        path1 = os.path.join(ARTIFACT_DIR, 'desktop_category_slider_arrows.png')
        with open(path1, 'wb') as f:
            f.write(base64.b64decode(shot1['data']))
        print(f"Captured: {path1}")

        # 2. Mobile Header at 360px (Admin & Saved Items visible)
        await send('Emulation.setDeviceMetricsOverride', {'width': 360, 'height': 780, 'deviceScaleFactor': 2, 'mobile': True})
        await send('Page.navigate', {'url': 'http://127.0.0.1:8080/index.html?t=mobile_shot'})
        await asyncio.sleep(1.2)
        shot2 = await send('Page.captureScreenshot', {'format': 'png'})
        path2 = os.path.join(ARTIFACT_DIR, 'mobile_header_admin_visible_360px.png')
        with open(path2, 'wb') as f:
            f.write(base64.b64decode(shot2['data']))
        print(f"Captured: {path2}")

        # 3. Featherlite Product Cards (Desktop 1280px)
        await send('Emulation.setDeviceMetricsOverride', {'width': 1280, 'height': 900, 'deviceScaleFactor': 1, 'mobile': False})
        await send('Page.navigate', {'url': 'http://127.0.0.1:8080/category.html?cat=office&t=featherlite_shot'})
        await asyncio.sleep(1.2)
        shot3 = await send('Page.captureScreenshot', {'format': 'png'})
        path3 = os.path.join(ARTIFACT_DIR, 'featherlite_product_cards.png')
        with open(path3, 'wb') as f:
            f.write(base64.b64decode(shot3['data']))
        print(f"Captured: {path3}")

asyncio.run(capture_screenshots())
