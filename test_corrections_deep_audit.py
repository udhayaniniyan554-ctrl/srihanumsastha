# test_corrections_deep_audit.py
import asyncio
import json
import time
import urllib.request
import websockets

async def run_audit():
    with urllib.request.urlopen('http://127.0.0.1:9222/json') as r:
        targets = json.loads(r.read().decode('utf-8'))
    tab = next(t for t in targets if '8080' in t.get('url', ''))

    async with websockets.connect(tab['webSocketDebuggerUrl'], max_size=50*1024*1024) as ws:
        msg_id = 8000
        async def send(m, p=None):
            nonlocal msg_id
            msg_id += 1
            await ws.send(json.dumps({'id': msg_id, 'method': m, 'params': p or {}}))
            while True:
                resp = json.loads(await ws.recv())
                if resp.get('id') == msg_id: return resp.get('result', {})

        print("==================================================================")
        print("     DEEP VERIFICATION AUDIT: CORRECTIONS FOR PROMPT 10           ")
        print("==================================================================")

        # ---------------- 1. HOMEPAGE CATEGORY SLIDER WITH LEFT & RIGHT ARROWS ----------------
        print("\n--- 1. Testing Homepage Category Slider & SVG Arrow Controls ---")
        await send('Emulation.setDeviceMetricsOverride', {'width': 1200, 'height': 850, 'deviceScaleFactor': 1, 'mobile': False})
        t_now = int(time.time() * 1000)
        await send('Page.navigate', {'url': f'http://127.0.0.1:8080/index.html?t={t_now}'})
        await asyncio.sleep(1.0)

        # Check arrow elements and SVG
        check_arrows_js = """(() => {
            const prev = document.querySelector('.hero-carousel-prev');
            const next = document.querySelector('.hero-carousel-next');
            const prevSvg = prev?.querySelector('svg');
            const nextSvg = next?.querySelector('svg');
            const prevStyle = prev ? window.getComputedStyle(prev) : null;
            const nextStyle = next ? window.getComputedStyle(next) : null;
            return {
                hasPrev: !!prev,
                hasNext: !!next,
                prevHtml: prev?.outerHTML,
                nextHtml: next?.outerHTML,
                hasPrevSvg: !!prevSvg,
                hasNextSvg: !!nextSvg,
                prevVisible: prevStyle?.display !== 'none',
                nextVisible: nextStyle?.display !== 'none',
                prevWidth: prevStyle?.width,
                prevHeight: prevStyle?.height
            };
        })()"""
        arrows_res = (await send('Runtime.evaluate', {'expression': check_arrows_js, 'returnByValue': True}))['result']['value']
        assert arrows_res['hasPrev'] and arrows_res['hasNext'], "Arrows missing!"
        assert arrows_res['hasPrevSvg'] and arrows_res['hasNextSvg'], f"SVG Chevrons missing! Found: {arrows_res}"
        assert arrows_res['prevVisible'] and arrows_res['nextVisible'], "Arrows not visible on desktop!"
        print(f"  [PASS] Slider Arrow controls: Prev={arrows_res['prevWidth']}x{arrows_res['prevHeight']}, SVG icons verified.")

        # Test Right Arrow click advances slide
        get_active_index_js = "document.querySelector('#heroCarousel .hero-slide.active')?.getAttribute('data-index')"
        init_idx = (await send('Runtime.evaluate', {'expression': get_active_index_js, 'returnByValue': True}))['result']['value']
        
        click_next_js = "document.querySelector('.hero-carousel-next').click()"
        await send('Runtime.evaluate', {'expression': click_next_js})
        await asyncio.sleep(0.3)
        idx_after_next = (await send('Runtime.evaluate', {'expression': get_active_index_js, 'returnByValue': True}))['result']['value']
        
        url_js = "window.location.href"
        curr_url = (await send('Runtime.evaluate', {'expression': url_js, 'returnByValue': True}))['result']['value']
        assert 'index.html' in curr_url, f"Clicking next arrow incorrectly navigated away: {curr_url}"
        assert int(idx_after_next) == (int(init_idx) + 1) % 5, f"Next arrow failed: from {init_idx} to {idx_after_next}"
        print(f"  [PASS] Right arrow clicked: Advanced slide from Index {init_idx} to Index {idx_after_next} without navigating away.")

        # Test Left Arrow click goes back
        click_prev_js = "document.querySelector('.hero-carousel-prev').click()"
        await send('Runtime.evaluate', {'expression': click_prev_js})
        await asyncio.sleep(0.3)
        idx_after_prev = (await send('Runtime.evaluate', {'expression': get_active_index_js, 'returnByValue': True}))['result']['value']
        assert int(idx_after_prev) == int(init_idx), f"Prev arrow failed: from {idx_after_next} to {idx_after_prev}"
        print(f"  [PASS] Left arrow clicked: Returned slide to Index {idx_after_prev} without navigating away.")

        # Test slide visual click opens category page
        click_slide_js = "document.querySelector('#heroCarousel .hero-slide.active .hero-slide-visual').click()"
        await send('Runtime.evaluate', {'expression': click_slide_js})
        await asyncio.sleep(1.0)
        nav_url = (await send('Runtime.evaluate', {'expression': url_js, 'returnByValue': True}))['result']['value']
        assert 'category.html?cat=' in nav_url, f"Clicking slide visual failed to open category page: {nav_url}"
        print(f"  [PASS] Slide visual clicked: Correctly navigated to {nav_url}")

        # ---------------- 2. MOBILE HEADER & ADMIN DASHBOARD VISIBILITY ----------------
        print("\n--- 2. Testing Mobile Header (360px Viewport) ---")
        await send('Emulation.setDeviceMetricsOverride', {'width': 360, 'height': 800, 'deviceScaleFactor': 2, 'mobile': True})
        t_now = int(time.time() * 1000)
        await send('Page.navigate', {'url': f'http://127.0.0.1:8080/index.html?t={t_now}'})
        await asyncio.sleep(1.0)

        check_mobile_header_js = """(() => {
            const adminBtn = document.getElementById('openAdminNavBtn');
            const savedBtn = document.querySelector('.btn-header-saved');
            const toggleBtn = document.getElementById('mobileToggle');
            const logo = document.querySelector('.brand-logo img');
            
            const adminRect = adminBtn?.getBoundingClientRect();
            const savedRect = savedBtn?.getBoundingClientRect();
            const toggleRect = toggleBtn?.getBoundingClientRect();
            const logoRect = logo?.getBoundingClientRect();
            
            const adminStyle = adminBtn ? window.getComputedStyle(adminBtn) : null;
            const savedStyle = savedBtn ? window.getComputedStyle(savedBtn) : null;
            const toggleStyle = toggleBtn ? window.getComputedStyle(toggleBtn) : null;
            const logoStyle = logo ? window.getComputedStyle(logo) : null;
            
            return {
                adminVisible: adminStyle?.display !== 'none' && adminRect?.width > 0,
                adminText: adminBtn?.innerText?.trim(),
                adminHeight: adminRect?.height,
                savedVisible: savedStyle?.display !== 'none' && savedRect?.width > 0,
                savedText: savedBtn?.innerText?.trim(),
                savedHeight: savedRect?.height,
                toggleVisible: toggleStyle?.display !== 'none' && toggleRect?.width > 0,
                logoVisible: logoStyle?.display !== 'none' && logoRect?.width > 0,
                logoWidth: logoRect?.width,
                logoHeight: logoRect?.height,
                scrollWidth: document.documentElement.scrollWidth,
                innerWidth: window.innerWidth,
                hasOverflow: document.documentElement.scrollWidth > window.innerWidth
            };
        })()"""
        m_res = (await send('Runtime.evaluate', {'expression': check_mobile_header_js, 'returnByValue': True}))['result']['value']
        assert m_res['adminVisible'], "Admin button NOT visible in mobile header!"
        assert m_res['savedVisible'], "Saved button NOT visible in mobile header!"
        assert m_res['toggleVisible'], "Mobile toggle button NOT visible in mobile header!"
        assert m_res['logoVisible'], "Brand logo NOT visible in mobile header!"
        assert not m_res['hasOverflow'], f"Horizontal overflow at 360px: scrollW={m_res['scrollWidth']}, innerW={m_res['innerWidth']}"
        print(f"  [PASS] Mobile Header at 360px:")
        print(f"         - Logo: {m_res['logoWidth']:.1f}x{m_res['logoHeight']:.1f}px (Visible: {m_res['logoVisible']})")
        print(f"         - Admin Button: '{m_res['adminText']}' ({m_res['adminHeight']}px height, Visible: {m_res['adminVisible']})")
        print(f"         - Saved Button: '{m_res['savedText']}' ({m_res['savedHeight']}px height, Visible: {m_res['savedVisible']})")
        print(f"         - Menu Toggle: Visible: {m_res['toggleVisible']}")
        print(f"         - Horizontal Overflow: {m_res['hasOverflow']} (scrollW={m_res['scrollWidth']} <= {m_res['innerWidth']})")

        # Check mobile arrows visibility
        check_mobile_arrows_js = """(() => {
            const prev = document.querySelector('.hero-carousel-prev');
            const next = document.querySelector('.hero-carousel-next');
            const prevStyle = prev ? window.getComputedStyle(prev) : null;
            const nextStyle = next ? window.getComputedStyle(next) : null;
            return {
                prevDisplay: prevStyle?.display,
                nextDisplay: nextStyle?.display,
                prevWidth: prevStyle?.width,
                prevHeight: prevStyle?.height
            };
        })()"""
        m_arrows = (await send('Runtime.evaluate', {'expression': check_mobile_arrows_js, 'returnByValue': True}))['result']['value']
        assert m_arrows['prevDisplay'] == 'flex' and m_arrows['nextDisplay'] == 'flex', f"Mobile arrows not displayed: {m_arrows}"
        print(f"  [PASS] Mobile Slider Arrows visible on 360px: {m_arrows['prevWidth']}x{m_arrows['prevHeight']}")

        # Test clicking Admin Button on Mobile opens Admin Portal
        print("\n--- 3. Testing Mobile Admin Button Click ---")
        click_admin_js = "document.getElementById('openAdminNavBtn').click()"
        await send('Runtime.evaluate', {'expression': click_admin_js})
        await asyncio.sleep(0.5)
        check_admin_modal_js = """(() => {
            const modal = document.getElementById('adminLoginModal');
            const overlay = document.getElementById('adminDashboardOverlay');
            const modalOpen = modal?.classList.contains('open') || window.getComputedStyle(modal || {}).display !== 'none';
            const overlayOpen = overlay?.classList.contains('open') || window.getComputedStyle(overlay || {}).display !== 'none';
            return { modalOpen, overlayOpen };
        })()"""
        modal_res = (await send('Runtime.evaluate', {'expression': check_admin_modal_js, 'returnByValue': True}))['result']['value']
        assert modal_res['modalOpen'] or modal_res['overlayOpen'], "Clicking mobile Admin button did not open Admin portal!"
        print(f"  [PASS] Admin Button click on mobile successfully opened Admin modal/portal (modal={modal_res['modalOpen']}, overlay={modal_res['overlayOpen']})")

        # ---------------- 4. FEATHERLITE-INSPIRED PRODUCT CARD STYLING ----------------
        print("\n--- 4. Testing Featherlite-Inspired Product Card Aesthetics ---")
        await send('Emulation.setDeviceMetricsOverride', {'width': 1200, 'height': 850, 'deviceScaleFactor': 1, 'mobile': False})
        t_now = int(time.time() * 1000)
        await send('Page.navigate', {'url': f'http://127.0.0.1:8080/category.html?cat=office&t={t_now}'})
        await asyncio.sleep(1.0)

        check_cards_js = """(() => {
            const card = document.querySelector('.product-card');
            const canvas = card?.querySelector('.product-image-canvas');
            const img = canvas?.querySelector('img');
            const name = card?.querySelector('.product-name');
            const waBtn = card?.querySelector('.btn-primary');
            const detailBtn = card?.querySelector('.btn-outline');
            
            const cardStyle = card ? window.getComputedStyle(card) : null;
            const canvasStyle = canvas ? window.getComputedStyle(canvas) : null;
            const imgStyle = img ? window.getComputedStyle(img) : null;
            const waStyle = waBtn ? window.getComputedStyle(waBtn) : null;
            const detailStyle = detailBtn ? window.getComputedStyle(detailBtn) : null;
            
            return {
                cardBorder: cardStyle?.borderColor,
                cardRadius: cardStyle?.borderRadius,
                cardBg: cardStyle?.backgroundColor,
                canvasBg: canvasStyle?.backgroundImage || canvasStyle?.backgroundColor,
                imgFit: imgStyle?.objectFit,
                waBg: waStyle?.backgroundColor,
                waColor: waStyle?.color,
                detailBorder: detailStyle?.borderColor,
                detailColor: detailStyle?.color,
                waHref: waBtn?.getAttribute('href'),
                detailHref: detailBtn?.getAttribute('href')
            };
        })()"""
        card_res = (await send('Runtime.evaluate', {'expression': check_cards_js, 'returnByValue': True}))['result']['value']
        assert '226, 232, 240' in card_res['cardBorder'] or 'e2e8f0' in card_res['cardBorder'].lower(), f"Card border mismatch: {card_res['cardBorder']}"
        assert '10px' in card_res['cardRadius'] or '8px' in card_res['cardRadius'], f"Card radius mismatch: {card_res['cardRadius']}"
        assert card_res['imgFit'] == 'contain', f"Image object-fit mismatch: {card_res['imgFit']}"
        assert '20, 83, 45' in card_res['waBg'] or '14532d' in card_res['waBg'].lower(), f"WhatsApp button bg mismatch: {card_res['waBg']}"
        assert 'wa.me/918695706013' in card_res['waHref'], f"WhatsApp URL mismatch: {card_res['waHref']}"
        assert 'product.html?id=' in card_res['detailHref'], f"Detail href mismatch: {card_res['detailHref']}"
        print(f"  [PASS] Featherlite Product Card verification:")
        print(f"         - Card Border: {card_res['cardBorder']} (crisp #E2E8F0)")
        print(f"         - Card Radius: {card_res['cardRadius']}")
        print(f"         - Image object-fit: {card_res['imgFit']}")
        print(f"         - WhatsApp Button BG: {card_res['waBg']} (Featherlite commercial green #14532D)")
        print(f"         - View Details Target: {card_res['detailHref']}")

        print("\n==================================================================")
        print("  ALL AUDIT MANDATES PASSED WITH 100% SUCCESS!                    ")
        print("==================================================================")

asyncio.run(run_audit())
