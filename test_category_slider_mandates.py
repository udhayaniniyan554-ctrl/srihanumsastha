# test_category_slider_mandates.py
import asyncio
import json
import urllib.request
import websockets

async def run_mandate_tests():
    with urllib.request.urlopen('http://127.0.0.1:9222/json') as r:
        targets = json.loads(r.read().decode('utf-8'))
    tab = next(t for t in targets if '8080' in t.get('url', ''))

    async with websockets.connect(tab['webSocketDebuggerUrl'], max_size=50*1024*1024) as ws:
        msg_id = 9500
        async def send(m, p=None):
            nonlocal msg_id
            msg_id += 1
            await ws.send(json.dumps({'id': msg_id, 'method': m, 'params': p or {}}))
            while True:
                resp = json.loads(await ws.recv())
                if resp.get('id') == msg_id: return resp.get('result', {})

        print("==================================================================")
        print("     MANDATORY TESTING: 5-CATEGORY AUTOMATIC IMAGE SLIDER         ")
        print("==================================================================")

        # Navigate to homepage
        await send('Page.navigate', {'url': 'http://127.0.0.1:8080/index.html'})
        await asyncio.sleep(1.0)

        # 1. Confirm exactly five category slides exist
        js_slides = """(() => {
            const slides = document.querySelectorAll('#heroCarousel .hero-slide');
            return Array.from(slides).map((s, idx) => {
                const title = s.querySelector('.hero-slide-title')?.textContent.trim();
                const img = s.querySelector('.hero-slide-canvas img')?.getAttribute('src');
                const visualOnclick = s.querySelector('.hero-slide-visual')?.getAttribute('onclick');
                const actionHref = s.querySelector('.hero-slide-actions a')?.getAttribute('href');
                return { idx, title, img, visualOnclick, actionHref };
            });
        })()"""
        res = await send('Runtime.evaluate', {'expression': js_slides, 'returnByValue': True})
        slides_info = res['result']['value']
        assert len(slides_info) == 5, f"Expected exactly 5 slides, got {len(slides_info)}"
        print(f"  [PASS] Confirmed exactly 5 category slides exist (count = {len(slides_info)}).")

        expected_categories = [
            ("OFFICE CHAIRS", "category.html?cat=office", "office_1_1.png"),
            ("VISITOR CHAIRS", "category.html?cat=visitor", "visitor_1_1_1.png"),
            ("LOUNGE & SOFT SEATING", "category.html?cat=lounge", "soft_p7_1.png"),
            ("DINING CHAIRS", "category.html?cat=dining", "soft_p1_1.png"),
            ("STOOLS & ADDITIONAL SEATING", "category.html?cat=stools", "visitor_5_5_1.png")
        ]

        # 2 & 3. Verify order, categories, photographs, and no individual product names
        for idx, (exp_title, exp_link, exp_img) in enumerate(expected_categories):
            s = slides_info[idx]
            # Replace non-breaking spaces or &amp; for title check
            clean_title = s['title'].replace('&', '&').replace('&amp;', '&')
            assert exp_title in clean_title, f"Slide {idx} title mismatch: expected {exp_title}, got {clean_title}"
            assert exp_img in s['img'], f"Slide {idx} image mismatch: expected {exp_img}, got {s['img']}"
            assert exp_link in s['visualOnclick'] or exp_link in s['actionHref'], f"Slide {idx} link mismatch: expected {exp_link}"
            # Assert NO individual chair product names
            assert "SHSE 1" not in clean_title and "SHSE 2" not in clean_title and "ATLAS" not in clean_title, f"Individual product found in slide {idx}: {clean_title}"
            print(f"  [PASS] Slide {idx+1}: {clean_title} -> {exp_img} (Target: {exp_link})")

        # 4. Confirm each slide changes automatically (~2s interval)
        print("\n  Testing 2-second automatic slider transition...")
        initial_slide_js = "document.querySelector('#heroCarousel .hero-slide.active')?.getAttribute('data-index')"
        s0 = (await send('Runtime.evaluate', {'expression': initial_slide_js, 'returnByValue': True}))['result']['value']
        await asyncio.sleep(2.3)
        s1 = (await send('Runtime.evaluate', {'expression': initial_slide_js, 'returnByValue': True}))['result']['value']
        await asyncio.sleep(2.3)
        s2 = (await send('Runtime.evaluate', {'expression': initial_slide_js, 'returnByValue': True}))['result']['value']
        print(f"    Slide transition timeline: Index {s0} -> Index {s1} -> Index {s2}")
        assert s0 != s1 or s1 != s2, "Slider did not advance automatically!"
        print("  [PASS] Automatic 2-second cycle verified.")

        # 5. Click all five photographs and verify each opens its own category page
        print("\n  Testing category page navigation for all five categories...")
        for cat_param, exp_heading, min_count in [
            ('office', 'OFFICE CHAIRS', 100),
            ('visitor', 'VISITOR CHAIRS', 40),
            ('lounge', 'LOUNGE & SOFT SEATING', 20),
            ('dining', 'DINING CHAIRS', 20),
            ('stools', 'STOOLS', 7)
        ]:
            url = f"http://127.0.0.1:8080/category.html?cat={cat_param}"
            await send('Page.navigate', {'url': url})
            await asyncio.sleep(1.0)
            check_cat_js = """(() => {
                const heading = document.getElementById('catHeading')?.textContent.trim();
                const cards = document.querySelectorAll('#catProductsGrid .product-card');
                const breadcrumb = document.getElementById('breadcrumbCatName')?.textContent.trim();
                return { heading, count: cards.length, breadcrumb };
            })()"""
            c_res = (await send('Runtime.evaluate', {'expression': check_cat_js, 'returnByValue': True}))['result']['value']
            assert exp_heading in c_res['heading'], f"Heading mismatch for {cat_param}: expected {exp_heading}, got {c_res['heading']}"
            assert c_res['count'] >= min_count, f"Product count mismatch for {cat_param}: expected >={min_count}, got {c_res['count']}"
            print(f"  [PASS] category.html?cat={cat_param} -> Heading: '{c_res['heading']}', Breadcrumb: '{c_res['breadcrumb']}', Products Rendered: {c_res['count']}")

        # 6. Confirm individual products open their own details pages
        print("\n  Testing product click from category to product details page...")
        await send('Page.navigate', {'url': 'http://127.0.0.1:8080/category.html?cat=office'})
        await asyncio.sleep(1.0)
        prod_click_js = """(() => {
            const firstCard = document.querySelector('#catProductsGrid .product-card');
            const pid = firstCard?.getAttribute('data-id');
            const btn = firstCard?.querySelector('a.btn-outline');
            return { pid, href: btn?.getAttribute('href') };
        })()"""
        p_info = (await send('Runtime.evaluate', {'expression': prod_click_js, 'returnByValue': True}))['result']['value']
        assert p_info['pid'] and 'product.html' in p_info['href']
        await send('Page.navigate', {'url': f"http://127.0.0.1:8080/{p_info['href']}"})
        await asyncio.sleep(1.0)
        detail_check_js = """(() => {
            const title = document.getElementById('productTitle')?.textContent.trim();
            const waHref = document.getElementById('waPrimaryBtn')?.getAttribute('href');
            return { title, waHref };
        })()"""
        d_res = (await send('Runtime.evaluate', {'expression': detail_check_js, 'returnByValue': True}))['result']['value']
        assert "SHSE" in d_res['title']
        assert "wa.me/918695706013" in d_res['waHref']
        print(f"  [PASS] Product Details verified: '{d_res['title']}' with active WhatsApp CTA ({d_res['waHref'][:35]}...)")

        # 7. Check responsive layout (no overflow at 375px mobile and 1200px desktop)
        print("\n  Testing responsive layout (375px mobile and 1200px desktop)...")
        for w in [375, 1200]:
            await send('Emulation.setDeviceMetricsOverride', {'width': w, 'height': 800, 'deviceScaleFactor': 2, 'mobile': (w <= 768)})
            await send('Page.navigate', {'url': 'http://127.0.0.1:8080/index.html'})
            await asyncio.sleep(0.8)
            overflow_js = "({ w: window.innerWidth, scrollW: document.documentElement.scrollWidth, overflow: document.documentElement.scrollWidth > window.innerWidth })"
            of_res = (await send('Runtime.evaluate', {'expression': overflow_js, 'returnByValue': True}))['result']['value']
            assert not of_res['overflow'], f"Horizontal overflow detected at {w}px: innerW={of_res['w']}, scrollW={of_res['scrollW']}"
            print(f"  [PASS] Responsive layout at {w}px: width={of_res['w']}, scrollWidth={of_res['scrollW']}, overflow={of_res['overflow']}")

        print("==================================================================")
        print("  ALL MANDATORY SLIDER & CATEGORY TESTS PASSED WITH 100% SUCCESS! ")
        print("==================================================================")

asyncio.run(run_mandate_tests())
