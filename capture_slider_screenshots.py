import asyncio, json, urllib.request, websockets, base64, os

ARTIFACT_DIR = r"C:\Users\user\.gemini\antigravity\brain\fc8bd55f-e93a-4611-bc32-454569cca86d"

async def capture():
    with urllib.request.urlopen("http://127.0.0.1:9222/json") as r:
        targets = json.loads(r.read().decode("utf-8"))
    tab = next(t for t in targets if "8080" in t.get("url", ""))

    async with websockets.connect(tab["webSocketDebuggerUrl"], max_size=50*1024*1024) as ws:
        msg_id = 9700
        async def send(m, p=None):
            nonlocal msg_id
            msg_id += 1
            await ws.send(json.dumps({"id": msg_id, "method": m, "params": p or {}}))
            while True:
                resp = json.loads(await ws.recv())
                if resp.get("id") == msg_id: return resp.get("result", {})

        # Desktop Office Chairs Slide
        await send("Emulation.setDeviceMetricsOverride", {"width": 1200, "height": 800, "deviceScaleFactor": 2, "mobile": False})
        await send("Page.navigate", {"url": "http://127.0.0.1:8080/index.html"})
        await asyncio.sleep(0.5)
        res = await send("Page.captureScreenshot", {"format": "png"})
        with open(os.path.join(ARTIFACT_DIR, "slider_desktop_office.png"), "wb") as f:
            f.write(base64.b64decode(res["data"]))
        print("Captured: slider_desktop_office.png")

        # Wait 2.2 seconds for automatic transition to Slide 2 (Visitor Chairs)
        await asyncio.sleep(2.2)
        res = await send("Page.captureScreenshot", {"format": "png"})
        with open(os.path.join(ARTIFACT_DIR, "slider_desktop_visitor.png"), "wb") as f:
            f.write(base64.b64decode(res["data"]))
        print("Captured: slider_desktop_visitor.png")

        # Mobile View at 375px
        await send("Emulation.setDeviceMetricsOverride", {"width": 375, "height": 812, "deviceScaleFactor": 2, "mobile": True})
        await send("Page.navigate", {"url": "http://127.0.0.1:8080/index.html"})
        await asyncio.sleep(0.5)
        res = await send("Page.captureScreenshot", {"format": "png"})
        with open(os.path.join(ARTIFACT_DIR, "slider_mobile_office.png"), "wb") as f:
            f.write(base64.b64decode(res["data"]))
        print("Captured: slider_mobile_office.png")

asyncio.run(capture())
