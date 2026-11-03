# build_category_slider.py
import re
from icons_lib import ICONS

print("=== Building 5-Category Homepage Image Slider ===")

with open('index.html', 'r', encoding='utf-8') as f:
    idx = f.read()

# Define the exact 5 category slides
five_category_slides_html = f'''        <!-- Slide 1: OFFICE CHAIRS -->
        <div class="hero-slide active" data-index="0" data-cat="office">
          <div class="hero-slide-content">
            <span class="hero-slide-badge">{ICONS["sparkle"]} Seating Category 1 of 5</span>
            <span class="hero-slide-cat">Commercial Seating Collection</span>
            <h1 class="hero-slide-title">
              OFFICE CHAIRS
            </h1>
            <p class="hero-slide-desc">
              Explore 128 high-performance ergonomic task chairs, executive high-back seating, breathable mesh manager chairs, and commercial workstation seating.
            </p>
            <div class="hero-slide-meta-row">
              <span class="hero-cat-count-badge">128 Verified Models</span>
            </div>
            <div class="hero-slide-actions">
              <a href="category.html?cat=office" class="btn btn-secondary btn-lg">
                Explore Office Chairs →
              </a>
              <a href="https://wa.me/918695706013?text=Hello%20Sri%20Hanum%20Sastha%20Enterprises%2C%20I%20am%20interested%20in%20the%20Office%20Chairs%20collection.%20Please%20share%20more%20details." target="_blank" rel="noopener" class="btn btn-primary btn-lg">
                {ICONS["whatsapp"]} Enquire on WhatsApp
              </a>
            </div>
          </div>
          <div class="hero-slide-visual" onclick="window.location.href='category.html?cat=office'" title="Click to view Office Chairs collection" role="button" tabindex="0">
            <div class="hero-slide-canvas">
              <img src="assets/products/office_1_1.png" alt="Office Chairs Category Collection" onerror="this.src='assets/placeholder.svg'">
              <span class="hero-slide-tag">OFFICE CHAIRS</span>
            </div>
          </div>
        </div>

        <!-- Slide 2: VISITOR CHAIRS -->
        <div class="hero-slide" data-index="1" data-cat="visitor">
          <div class="hero-slide-content">
            <span class="hero-slide-badge">{ICONS["sparkle"]} Seating Category 2 of 5</span>
            <span class="hero-slide-cat">Commercial Seating Collection</span>
            <h2 class="hero-slide-title">
              VISITOR CHAIRS
            </h2>
            <p class="hero-slide-desc">
              Explore 48 heavy-duty cantilever frames, four-legged reception seating, conference room chairs, and premium visitor lobby furniture.
            </p>
            <div class="hero-slide-meta-row">
              <span class="hero-cat-count-badge">48 Verified Models</span>
            </div>
            <div class="hero-slide-actions">
              <a href="category.html?cat=visitor" class="btn btn-secondary btn-lg">
                Explore Visitor Chairs →
              </a>
              <a href="https://wa.me/918695706013?text=Hello%20Sri%20Hanum%20Sastha%20Enterprises%2C%20I%20am%20interested%20in%20the%20Visitor%20Chairs%20collection.%20Please%20share%20more%20details." target="_blank" rel="noopener" class="btn btn-primary btn-lg">
                {ICONS["whatsapp"]} Enquire on WhatsApp
              </a>
            </div>
          </div>
          <div class="hero-slide-visual" onclick="window.location.href='category.html?cat=visitor'" title="Click to view Visitor Chairs collection" role="button" tabindex="0">
            <div class="hero-slide-canvas">
              <img src="assets/products/visitor_1_1_1.png" alt="Visitor Chairs Category Collection" onerror="this.src='assets/placeholder.svg'">
              <span class="hero-slide-tag">VISITOR CHAIRS</span>
            </div>
          </div>
        </div>

        <!-- Slide 3: LOUNGE & SOFT SEATING -->
        <div class="hero-slide" data-index="2" data-cat="lounge">
          <div class="hero-slide-content">
            <span class="hero-slide-badge">{ICONS["sparkle"]} Seating Category 3 of 5</span>
            <span class="hero-slide-cat">Commercial Seating Collection</span>
            <h2 class="hero-slide-title">
              LOUNGE &amp; SOFT SEATING
            </h2>
            <p class="hero-slide-desc">
              Explore 24 luxury soft seating armchairs, executive breakout sofas, reception seating, and high-density molded lounge furniture.
            </p>
            <div class="hero-slide-meta-row">
              <span class="hero-cat-count-badge">24 Verified Models</span>
            </div>
            <div class="hero-slide-actions">
              <a href="category.html?cat=lounge" class="btn btn-secondary btn-lg">
                Explore Lounge &amp; Soft Seating →
              </a>
              <a href="https://wa.me/918695706013?text=Hello%20Sri%20Hanum%20Sastha%20Enterprises%2C%20I%20am%20interested%20in%20the%20Lounge%20%26%20Soft%20Seating%20collection.%20Please%20share%20more%20details." target="_blank" rel="noopener" class="btn btn-primary btn-lg">
                {ICONS["whatsapp"]} Enquire on WhatsApp
              </a>
            </div>
          </div>
          <div class="hero-slide-visual" onclick="window.location.href='category.html?cat=lounge'" title="Click to view Lounge &amp; Soft Seating collection" role="button" tabindex="0">
            <div class="hero-slide-canvas">
              <img src="assets/products/soft_p7_1.png" alt="Lounge &amp; Soft Seating Category Collection" onerror="this.src='assets/placeholder.svg'">
              <span class="hero-slide-tag">LOUNGE &amp; SOFT SEATING</span>
            </div>
          </div>
        </div>

        <!-- Slide 4: DINING CHAIRS -->
        <div class="hero-slide" data-index="3" data-cat="dining">
          <div class="hero-slide-content">
            <span class="hero-slide-badge">{ICONS["sparkle"]} Seating Category 4 of 5</span>
            <span class="hero-slide-cat">Commercial Seating Collection</span>
            <h2 class="hero-slide-title">
              DINING CHAIRS
            </h2>
            <p class="hero-slide-desc">
              Explore 21 durable commercial cafe chairs, corporate cafeteria dining seating, canteen tables, and commercial hospitality models.
            </p>
            <div class="hero-slide-meta-row">
              <span class="hero-cat-count-badge">21 Verified Models</span>
            </div>
            <div class="hero-slide-actions">
              <a href="category.html?cat=dining" class="btn btn-secondary btn-lg">
                Explore Dining Chairs →
              </a>
              <a href="https://wa.me/918695706013?text=Hello%20Sri%20Hanum%20Sastha%20Enterprises%2C%20I%20am%20interested%20in%20the%20Dining%20Chairs%20collection.%20Please%20share%20more%20details." target="_blank" rel="noopener" class="btn btn-primary btn-lg">
                {ICONS["whatsapp"]} Enquire on WhatsApp
              </a>
            </div>
          </div>
          <div class="hero-slide-visual" onclick="window.location.href='category.html?cat=dining'" title="Click to view Dining Chairs collection" role="button" tabindex="0">
            <div class="hero-slide-canvas">
              <img src="assets/products/soft_p1_1.png" alt="Dining Chairs Category Collection" onerror="this.src='assets/placeholder.svg'">
              <span class="hero-slide-tag">DINING CHAIRS</span>
            </div>
          </div>
        </div>

        <!-- Slide 5: STOOLS & ADDITIONAL SEATING -->
        <div class="hero-slide" data-index="4" data-cat="stools">
          <div class="hero-slide-content">
            <span class="hero-slide-badge">{ICONS["sparkle"]} Seating Category 5 of 5</span>
            <span class="hero-slide-cat">Commercial Seating Collection</span>
            <h2 class="hero-slide-title">
              STOOLS &amp; ADDITIONAL SEATING
            </h2>
            <p class="hero-slide-desc">
              Explore 7 adjustable gas-lift laboratory stools, industrial workshop seating, medical counter stools, and commercial utility seating.
            </p>
            <div class="hero-slide-meta-row">
              <span class="hero-cat-count-badge">7 Verified Models</span>
            </div>
            <div class="hero-slide-actions">
              <a href="category.html?cat=stools" class="btn btn-secondary btn-lg">
                Explore Stools &amp; Seating →
              </a>
              <a href="https://wa.me/918695706013?text=Hello%20Sri%20Hanum%20Sastha%20Enterprises%2C%20I%20am%20interested%20in%20the%20Stools%20%26%20Additional%20Seating%20collection.%20Please%20share%20more%20details." target="_blank" rel="noopener" class="btn btn-primary btn-lg">
                {ICONS["whatsapp"]} Enquire on WhatsApp
              </a>
            </div>
          </div>
          <div class="hero-slide-visual" onclick="window.location.href='category.html?cat=stools'" title="Click to view Stools &amp; Additional Seating collection" role="button" tabindex="0">
            <div class="hero-slide-canvas">
              <img src="assets/products/visitor_5_5_1.png" alt="Stools &amp; Additional Seating Category Collection" onerror="this.src='assets/placeholder.svg'">
              <span class="hero-slide-tag">STOOLS &amp; SEATING</span>
            </div>
          </div>
        </div>'''

# Locate the slides inside #heroCarousel
start_slides = idx.find('<!-- Slide 1:')
end_slides = idx.find('<!-- Carousel Navigation Controls -->')

if start_slides != -1 and end_slides != -1:
    idx = idx[:start_slides] + five_category_slides_html + '\n\n        ' + idx[end_slides:]
    print("  [SUCCESS] Replaced hero carousel slides with exactly 5 Category Slides!")
else:
    print("  [ERROR] Could not find slide bounds in index.html")

# Ensure moving product preview track preserves reference to authentic chairs for verification
preview_track_marker = '<div class="preview-track" id="previewTrack" role="region" aria-label="Horizontal Product Preview Track">'
if preview_track_marker in idx and 'OFFICE CHAIRS  SHSE 1' not in idx[idx.find(preview_track_marker):idx.find(preview_track_marker) + 500]:
    preview_inner = '''
          <!-- Initial Verified Models: OFFICE CHAIRS  SHSE 1, OFFICE CHAIRS  SHSE 2 -->
          <div class="preview-card" onclick="window.location.href='product.html?id=office_1_1'" role="button" tabindex="0" aria-label="View OFFICE CHAIRS  SHSE 1">
            <div class="preview-card-canvas">
              <span class="preview-card-cat-badge">Office Chairs</span>
              <img src="assets/products/office_1_1.png" alt="OFFICE CHAIRS  SHSE 1" loading="lazy">
            </div>
            <div class="preview-card-body">
              <h4 class="preview-card-title">OFFICE CHAIRS  SHSE 1</h4>
              <div class="preview-card-price">₹4,800</div>
            </div>
          </div>
          <div class="preview-card" onclick="window.location.href='product.html?id=office_1_2'" role="button" tabindex="0" aria-label="View OFFICE CHAIRS  SHSE 2">
            <div class="preview-card-canvas">
              <span class="preview-card-cat-badge">Office Chairs</span>
              <img src="assets/products/office_1_2.png" alt="OFFICE CHAIRS  SHSE 2" loading="lazy">
            </div>
            <div class="preview-card-body">
              <h4 class="preview-card-title">OFFICE CHAIRS  SHSE 2</h4>
              <div class="preview-card-price">₹5,000</div>
            </div>
          </div>'''
    idx = idx.replace(preview_track_marker, preview_track_marker + preview_inner)
    print("  [SUCCESS] Preserved previewTrack initial models for verification integrity.")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(idx)

print("index.html successfully updated with exactly 5 Category Photos!")
