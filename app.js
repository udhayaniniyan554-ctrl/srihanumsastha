/**
 * Sri Hanum Sastha Enterprises — Commercial Seating Showroom
 * Ultra-Premium Vanilla JavaScript Engine
 * Automatic 2s Carousels, Comparison, Saved Chairs, Recent Views, Lightbox & AI Chatbot
 */

(function () {
  'use strict';

  // Global State
  const state = {
    allProducts: [],
    filteredProducts: [],
    selectedCategory: 'all',
    searchQuery: '',
    sortBy: 'default',
    currentPage: 1,
    pageSize: 24,
    comparedIds: JSON.parse(sessionStorage.getItem('shse_compare_ids') || '[]'),
    savedIds: JSON.parse(localStorage.getItem('shse_saved_chairs') || '[]'),
    recentlyViewedIds: JSON.parse(localStorage.getItem('shse_recently_viewed') || '[]'),
    concepts: [],
    categories: [
      { id: 'all', name: 'All Chairs' },
      { id: 'Office Chairs', name: 'Office Chairs', hash: 'office-chairs' },
      { id: 'Visitor Chairs', name: 'Visitor Chairs', hash: 'visitor-chairs' },
      { id: 'Lounge & Soft Seating', name: 'Lounge & Soft Seating', hash: 'lounge-seating' },
      { id: 'Dining Chairs', name: 'Dining Chairs', hash: 'dining-chairs' },
      { id: 'Stools & Additional Seating', name: 'Stools & Additional Seating', hash: 'stools-seating' }
    ]
  };

  // DOM Elements
  const el = {
    productsGrid: document.getElementById('productsGrid'),
    searchBar: document.getElementById('searchBar'),
    sortSelect: document.getElementById('sortSelect'),
    filterPillsContainer: document.getElementById('filterPillsContainer'),
    categoryCardsContainer: document.getElementById('categoryCardsContainer'),
    filterCount: document.getElementById('filterCount'),
    activeFilterName: document.getElementById('activeFilterName'),
    btnResetFilter: document.getElementById('btnResetFilter'),
    loadMoreContainer: document.getElementById('loadMoreContainer'),
    btnLoadMore: document.getElementById('btnLoadMore'),
    paginationInfo: document.getElementById('paginationInfo'),
    emptyState: document.getElementById('emptyState'),
    mobileToggle: document.getElementById('mobileToggle'),
    mobileDrawer: document.getElementById('mobileDrawer'),
    drawerBackdrop: document.getElementById('drawerBackdrop'),
    drawerCloseBtn: document.getElementById('drawerCloseBtn'),
    heroCarousel: document.getElementById('heroCarousel'),
    previewTrack: document.getElementById('previewTrack'),
    previewBtnPrev: document.getElementById('previewBtnPrev'),
    previewBtnNext: document.getElementById('previewBtnNext'),
    savedCountBadge: document.getElementById('savedCountBadge'),
    savedDrawer: document.getElementById('savedDrawer'),
    savedDrawerClose: document.getElementById('savedDrawerClose'),
    savedListContainer: document.getElementById('savedListContainer'),
    compareBar: document.getElementById('compareFloatingBar'),
    compareCountText: document.getElementById('compareCountText'),
    compareBarThumbs: document.getElementById('compareBarThumbs'),
    btnOpenCompareModal: document.getElementById('btnOpenCompareModal'),
    btnClearCompare: document.getElementById('btnClearCompare'),
    compareModal: document.getElementById('compareModal'),
    compareModalClose: document.getElementById('compareModalClose'),
    compareTableContent: document.getElementById('compareTableContent'),
    chatWidgetToggle: document.getElementById('chatWidgetToggle'),
    chatWindow: document.getElementById('chatWindow'),
    chatCloseBtn: document.getElementById('chatCloseBtn'),
    chatMessages: document.getElementById('chatMessages'),
    chatInput: document.getElementById('chatInput'),
    chatSendBtn: document.getElementById('chatSendBtn'),
    conceptsGrid: document.getElementById('conceptsGrid'),
    recentViewsSection: document.getElementById('recentViewsSection'),
    recentViewsTrack: document.getElementById('recentViewsTrack')
  };

  // Timers
  let heroTimer = null;
  let previewTimer = null;

  // ---------------- 1. INITIALIZE APPLICATION ----------------
  async function init() {
    try {
      let response = await fetch('assets/catalog.json');
      if (!response.ok) {
        response = await fetch('/api/chairs');
      }
      if (!response.ok) throw new Error('Failed to load catalogue dataset');
      state.allProducts = await response.json();

      initHeroCarousel();
      initProductPreviewTrack();
      renderCategoryCards();
      renderFilterPills();
      setupEventListeners();
      setupMobileDrawer();
      initCompareSystem();
      initSavedChairsSystem();
      initRecentlyViewedSystem();
      initAIChatbot();
      initConceptsSection();
      handleInitialHash();
      applyFiltersAndSort();
    } catch (err) {
      console.error('Initialization error:', err);
      if (el.productsGrid) {
        el.productsGrid.innerHTML = `
          <div class="empty-state">
            <div class="empty-state-icon">⚠️</div>
            <h3>Unable to load catalogue</h3>
            <p>Please check your local assets folder or refresh the page.</p>
            <button class="btn btn-primary" onclick="location.reload()">Retry Loading</button>
          </div>
        `;
      }
    }
  }

  // ---------------- 2. HERO AUTOMATIC CHAIR CAROUSEL (2s) ----------------
  function initHeroCarousel() {
    const container = el.heroCarousel;
    if (!container) return;

    const slides = container.querySelectorAll('.hero-slide');
    const dotsContainer = container.querySelector('.hero-carousel-indicators');
    const btnPrev = container.querySelector('.hero-carousel-prev');
    const btnNext = container.querySelector('.hero-carousel-next');

    if (!slides.length) return;

    let currentIndex = 0;
    const totalSlides = slides.length;
    const HERO_INTERVAL = 2000; // Exact 2-second automatic advance

    // Build indicator dots
    if (dotsContainer) {
      dotsContainer.innerHTML = '';
      for (let i = 0; i < totalSlides; i++) {
        const dot = document.createElement('button');
        dot.className = `hero-dot ${i === 0 ? 'active' : ''}`;
        dot.setAttribute('aria-label', `Go to slide ${i + 1}`);
        dot.addEventListener('click', () => {
          stopHeroTimer();
          goToSlide(i);
          startHeroTimer();
        });
        dotsContainer.appendChild(dot);
      }
    }

    // Preload slide images
    slides.forEach(slide => {
      const img = slide.querySelector('img');
      if (img && img.src) {
        const pre = new Image();
        pre.src = img.src;
      }
    });

    function goToSlide(index) {
      slides[currentIndex].classList.remove('active');
      const dots = dotsContainer ? dotsContainer.querySelectorAll('.hero-dot') : [];
      if (dots[currentIndex]) dots[currentIndex].classList.remove('active');

      currentIndex = (index + totalSlides) % totalSlides;

      slides[currentIndex].classList.add('active');
      if (dots[currentIndex]) dots[currentIndex].classList.add('active');
    }

    function nextSlide() {
      goToSlide(currentIndex + 1);
    }

    function prevSlide() {
      goToSlide(currentIndex - 1);
    }

    function startHeroTimer() {
      if (heroTimer) clearInterval(heroTimer);
      if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
      heroTimer = setInterval(nextSlide, HERO_INTERVAL);
    }

    function stopHeroTimer() {
      if (heroTimer) {
        clearInterval(heroTimer);
        heroTimer = null;
      }
    }

    if (btnNext) {
      btnNext.addEventListener('click', () => {
        stopHeroTimer();
        nextSlide();
        startHeroTimer();
      });
    }

    if (btnPrev) {
      btnPrev.addEventListener('click', () => {
        stopHeroTimer();
        prevSlide();
        startHeroTimer();
      });
    }

    // Pause on hover & focus
    container.addEventListener('mouseenter', stopHeroTimer);
    container.addEventListener('mouseleave', startHeroTimer);
    container.addEventListener('focusin', stopHeroTimer);
    container.addEventListener('focusout', startHeroTimer);

    // Touch swipe
    let touchStartX = 0;
    container.addEventListener('touchstart', (e) => {
      touchStartX = e.changedTouches[0].screenX;
    }, { passive: true });

    container.addEventListener('touchend', (e) => {
      const diff = e.changedTouches[0].screenX - touchStartX;
      if (diff < -40) {
        stopHeroTimer();
        nextSlide();
        startHeroTimer();
      } else if (diff > 40) {
        stopHeroTimer();
        prevSlide();
        startHeroTimer();
      }
    }, { passive: true });

    startHeroTimer();
  }

  // ---------------- 3. MOVING PRODUCT PREVIEW TRACK (2s) ----------------
  function initProductPreviewTrack() {
    const track = el.previewTrack;
    if (!track) return;

    const previewIds = [
      'office_1_1', 'office_1_2', 'visitor_1_1_1', 'soft_p7_1',
      'soft_p1_1', 'office_6_2', 'office_2_1', 'visitor_1_1_2',
      'visitor_6_1_1', 'soft_p3_1'
    ];

    const previewItems = previewIds
      .map(id => state.allProducts.find(p => p.id === id))
      .filter(Boolean);

    if (previewItems.length === 0 && state.allProducts.length > 0) {
      previewItems.push(...state.allProducts.slice(0, 10));
    }

    track.innerHTML = previewItems.map(p => {
      const model = p._internal_model || '';
      const code = p.code || `SHSE(${p.code_number || 1})`;
      const price = p.price_display || `₹${(p.base_price || 0).toLocaleString('en-IN')}`;

      return `
        <div class="preview-card" onclick="window.location.href='product.html?id=${p.id}'" role="button" tabindex="0" aria-label="View ${code} ${model}">
          <div class="preview-card-canvas">
            <span class="preview-card-cat-badge">${p.category}</span>
            <img src="${p.image}" alt="${code} - ${model}" loading="lazy" onerror="this.src='assets/placeholder.svg'">
          </div>
          <div class="preview-card-body">
            <span class="preview-card-code">${code}</span>
            <h4 class="preview-card-name">${model ? model : code}</h4>
            <div class="preview-card-price-row">
              <span class="preview-card-price">${price}</span>
              <span class="preview-card-action">View Details →</span>
            </div>
          </div>
        </div>
      `;
    }).join('');

    const PREVIEW_INTERVAL = 2000;

    function advanceTrack() {
      if (!track) return;
      const firstCard = track.querySelector('.preview-card');
      if (!firstCard) return;
      const step = firstCard.offsetWidth + 20;
      const maxScroll = track.scrollWidth - track.clientWidth;

      if (track.scrollLeft >= maxScroll - 15) {
        track.scrollTo({ left: 0, behavior: 'smooth' });
      } else {
        track.scrollBy({ left: step, behavior: 'smooth' });
      }
    }

    function startPreviewTimer() {
      if (previewTimer) clearInterval(previewTimer);
      if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
      previewTimer = setInterval(advanceTrack, PREVIEW_INTERVAL);
    }

    function stopPreviewTimer() {
      if (previewTimer) {
        clearInterval(previewTimer);
        previewTimer = null;
      }
    }

    if (el.previewBtnNext) {
      el.previewBtnNext.addEventListener('click', () => {
        stopPreviewTimer();
        advanceTrack();
        startPreviewTimer();
      });
    }

    if (el.previewBtnPrev) {
      el.previewBtnPrev.addEventListener('click', () => {
        stopPreviewTimer();
        const firstCard = track.querySelector('.preview-card');
        const step = firstCard ? (firstCard.offsetWidth + 20) : 280;
        track.scrollBy({ left: -step, behavior: 'smooth' });
        startPreviewTimer();
      });
    }

    track.addEventListener('mouseenter', stopPreviewTimer);
    track.addEventListener('mouseleave', startPreviewTimer);
    track.addEventListener('focusin', stopPreviewTimer);
    track.addEventListener('focusout', startPreviewTimer);

    startPreviewTimer();
  }

  // ---------------- 4. CATEGORY CARDS ----------------
  function renderCategoryCards() {
    if (!el.categoryCardsContainer) return;

    const catImages = {
      'Office Chairs': 'assets/products/office_1_1.png',
      'Visitor Chairs': 'assets/products/visitor_1_1_1.png',
      'Lounge & Soft Seating': 'assets/products/soft_p7_1.png',
      'Dining Chairs': 'assets/products/soft_p1_1.png',
      'Stools & Additional Seating': 'assets/products/visitor_6_1_1.png'
    };

    const cardsHtml = state.categories.filter(c => c.id !== 'all').map(cat => {
      const count = state.allProducts.filter(p => p.category === cat.id).length;
      const imgSrc = catImages[cat.id] || 'assets/placeholder.svg';
      const isActive = state.selectedCategory === cat.id;

      return `
        <div class="category-card ${isActive ? 'active' : ''}" data-category="${cat.id}">
          <div class="category-icon-box">
            <img src="${imgSrc}" alt="${cat.name} Collection" onerror="this.src='assets/placeholder.svg'" loading="lazy">
          </div>
          <h3 class="category-name">${cat.name}</h3>
          <span class="category-count">${count} Models</span>
        </div>
      `;
    }).join('');

    el.categoryCardsContainer.innerHTML = cardsHtml;

    el.categoryCardsContainer.querySelectorAll('.category-card').forEach(card => {
      card.addEventListener('click', () => {
        const catId = card.getAttribute('data-category');
        setCategory(catId);
        scrollToCatalogue();
      });
    });
  }

  // ---------------- 5. FILTER PILLS ----------------
  function renderFilterPills() {
    if (!el.filterPillsContainer) return;

    const pillsHtml = state.categories.map(cat => {
      const count = cat.id === 'all'
        ? state.allProducts.length
        : state.allProducts.filter(p => p.category === cat.id).length;
      const isActive = state.selectedCategory === cat.id;

      return `
        <button class="filter-pill ${isActive ? 'active' : ''}" data-category="${cat.id}">
          ${cat.name} (${count})
        </button>
      `;
    }).join('');

    el.filterPillsContainer.innerHTML = pillsHtml;

    el.filterPillsContainer.querySelectorAll('.filter-pill').forEach(pill => {
      pill.addEventListener('click', () => {
        const catId = pill.getAttribute('data-category');
        setCategory(catId);
      });
    });
  }

  // ---------------- 6. FILTER & SORT ENGINE ----------------
  function applyFiltersAndSort() {
    let result = [...state.allProducts];

    if (state.selectedCategory !== 'all') {
      result = result.filter(p => p.category === state.selectedCategory);
    }

    if (state.searchQuery.trim()) {
      const query = state.searchQuery.toLowerCase().trim();
      result = result.filter(p => {
        const code = (p.code || '').toLowerCase();
        const model = (p._internal_model || '').toLowerCase();
        const cat = (p.category || '').toLowerCase();
        const num = String(p.code_number || '');
        const keywords = (p.search_keywords || '').toLowerCase();

        return code.includes(query) ||
               model.includes(query) ||
               cat.includes(query) ||
               num.includes(query) ||
               keywords.includes(query);
      });
    }

    if (state.sortBy === 'price-low') {
      result.sort((a, b) => (a.base_price || 0) - (b.base_price || 0));
    } else if (state.sortBy === 'price-high') {
      result.sort((a, b) => (b.base_price || 0) - (a.base_price || 0));
    } else if (state.sortBy === 'code-asc') {
      result.sort((a, b) => (a.code_number || 0) - (b.code_number || 0));
    }

    state.filteredProducts = result;
    state.currentPage = 1;

    updateFilterUI();
    renderProducts();
  }

  function updateFilterUI() {
    if (el.filterCount) {
      el.filterCount.textContent = `${state.filteredProducts.length} chairs found`;
    }

    if (el.activeFilterName) {
      const activeCat = state.categories.find(c => c.id === state.selectedCategory);
      el.activeFilterName.textContent = activeCat ? activeCat.name : 'All Chairs';
    }

    if (el.btnResetFilter) {
      const isFiltered = state.selectedCategory !== 'all' || state.searchQuery.trim() !== '';
      el.btnResetFilter.style.display = isFiltered ? 'inline-block' : 'none';
    }

    if (el.categoryCardsContainer) {
      el.categoryCardsContainer.querySelectorAll('.category-card').forEach(card => {
        const catId = card.getAttribute('data-category');
        card.classList.toggle('active', catId === state.selectedCategory);
      });
    }

    if (el.filterPillsContainer) {
      el.filterPillsContainer.querySelectorAll('.filter-pill').forEach(pill => {
        const catId = pill.getAttribute('data-category');
        pill.classList.toggle('active', catId === state.selectedCategory);
      });
    }
  }

  // ---------------- 7. RENDER PRODUCTS GRID WITH COMPARE & SAVE ----------------
  function renderProducts() {
    if (!el.productsGrid) return;

    if (state.filteredProducts.length === 0) {
      el.productsGrid.innerHTML = '';
      if (el.emptyState) el.emptyState.style.display = 'block';
      if (el.loadMoreContainer) el.loadMoreContainer.style.display = 'none';
      return;
    }

    if (el.emptyState) el.emptyState.style.display = 'none';

    const visibleCount = state.currentPage * state.pageSize;
    const pagedItems = state.filteredProducts.slice(0, visibleCount);

    const cardsHtml = pagedItems.map(p => {
      const confirmedModel = p._internal_model || '';
      const displayCode = p.code || `SHSE(${p.code_number || 1})`;
      const priceDisplay = p.price_display || `₹${(p.base_price || 0).toLocaleString('en-IN')}`;
      const isSaved = state.savedIds.includes(p.id);
      const isCompared = state.comparedIds.includes(p.id);

      const waMessage = encodeURIComponent(
        `Hello Sri Hanum Sastha Enterprises, I am interested in chair ${displayCode} (Model: ${confirmedModel}) from the ${p.category} category. Please share more details.`
      );
      const waUrl = `https://wa.me/918695706013?text=${waMessage}`;

      return `
        <article class="product-card" data-id="${p.id}">
          <div class="product-image-canvas" onclick="window.location.href='product.html?id=${p.id}'" role="button" tabindex="0" aria-label="View details for ${displayCode}">
            <span class="product-category-badge">${p.category}</span>
            <button class="btn-save-chair ${isSaved ? 'active' : ''}" onclick="event.stopPropagation(); window.catalogApp.toggleSaveChair('${p.id}')" title="${isSaved ? 'Remove from Saved' : 'Save this chair'}" aria-label="Save ${displayCode}">
              ${isSaved ? '❤️' : '🤍'}
            </button>
            <img src="${p.image}" alt="${displayCode} - ${confirmedModel}" loading="lazy" onerror="this.src='assets/placeholder.svg'">
          </div>
          
          <div class="product-content">
            <div class="product-code-row" style="display: flex; justify-content: space-between; align-items: center;">
              <span class="product-code-badge">${displayCode}</span>
              <button class="btn-compare-chair ${isCompared ? 'active' : ''}" onclick="window.catalogApp.toggleCompare('${p.id}')">
                ${isCompared ? '✓ Comparing' : '+ Compare'}
              </button>
            </div>
            
            <h3 class="product-name">${confirmedModel ? confirmedModel : displayCode}</h3>
            
            <div class="product-price-row">
              <span class="product-price-label">Catalogue Rate</span>
              <span class="product-price-val">${priceDisplay}</span>
            </div>

            <div class="product-actions">
              <a href="product.html?id=${p.id}" class="btn btn-outline btn-sm">
                View Details →
              </a>
              <a href="${waUrl}" target="_blank" rel="noopener" class="btn btn-primary btn-sm" aria-label="Enquire about ${displayCode} on WhatsApp">
                💬 WhatsApp
              </a>
            </div>
          </div>
        </article>
      `;
    }).join('');

    el.productsGrid.innerHTML = cardsHtml;

    if (el.loadMoreContainer) {
      if (visibleCount < state.filteredProducts.length) {
        el.loadMoreContainer.style.display = 'flex';
        if (el.paginationInfo) {
          el.paginationInfo.textContent = `Showing ${pagedItems.length} of ${state.filteredProducts.length} models`;
        }
      } else {
        el.loadMoreContainer.style.display = 'none';
      }
    }
  }

  // ---------------- 8. CHAIR COMPARISON SYSTEM ----------------
  function initCompareSystem() {
    renderCompareBar();

    if (el.btnClearCompare) {
      el.btnClearCompare.addEventListener('click', () => {
        state.comparedIds = [];
        sessionStorage.setItem('shse_compare_ids', JSON.stringify([]));
        renderCompareBar();
        renderProducts();
      });
    }

    if (el.btnOpenCompareModal) {
      el.btnOpenCompareModal.addEventListener('click', openCompareModal);
    }

    if (el.compareModalClose) {
      el.compareModalClose.addEventListener('click', closeCompareModal);
    }

    if (el.compareModal) {
      el.compareModal.addEventListener('click', (e) => {
        if (e.target === el.compareModal) closeCompareModal();
      });
    }
  }

  function toggleCompare(chairId) {
    const idx = state.comparedIds.indexOf(chairId);
    if (idx >= 0) {
      state.comparedIds.splice(idx, 1);
    } else {
      if (state.comparedIds.length >= 4) {
        alert('You can compare up to 4 chairs simultaneously.');
        return;
      }
      state.comparedIds.push(chairId);
    }

    sessionStorage.setItem('shse_compare_ids', JSON.stringify(state.comparedIds));
    renderCompareBar();
    renderProducts();

    if (el.compareModal && el.compareModal.classList.contains('open')) {
      renderCompareTable();
    }
  }

  function renderCompareBar() {
    const bar = el.compareBar;
    if (!bar) return;

    if (state.comparedIds.length > 0) {
      bar.classList.add('visible');
      if (el.compareCountText) {
        el.compareCountText.textContent = `Compare (${state.comparedIds.length}/4)`;
      }

      if (el.compareBarThumbs) {
        el.compareBarThumbs.innerHTML = state.comparedIds.map(id => {
          const item = state.allProducts.find(p => p.id === id);
          if (!item) return '';
          return `
            <div class="compare-thumb-slot" title="${item.code} ${item._internal_model}">
              <img src="${item.image}" alt="${item.code}">
            </div>
          `;
        }).join('');
      }
    } else {
      bar.classList.remove('visible');
    }
  }

  function openCompareModal() {
    if (!el.compareModal) return;
    renderCompareTable();
    el.compareModal.classList.add('open');
    document.body.style.overflow = 'hidden';
  }

  function closeCompareModal() {
    if (!el.compareModal) return;
    el.compareModal.classList.remove('open');
    document.body.style.overflow = '';
  }

  function renderCompareTable() {
    const container = el.compareTableContent;
    if (!container) return;

    const items = state.comparedIds.map(id => state.allProducts.find(p => p.id === id)).filter(Boolean);

    if (items.length === 0) {
      container.innerHTML = '<p style="text-align:center; padding: 2rem;">No chairs currently selected for comparison. Add chairs from the catalogue grid.</p>';
      return;
    }

    const html = `
      <div class="compare-table-wrapper">
        <table class="compare-table">
          <thead>
            <tr>
              <th style="width: 140px;">Feature</th>
              ${items.map(item => `
                <th class="compare-col-header" style="min-width: 200px;">
                  <button class="compare-col-remove" onclick="window.catalogApp.toggleCompare('${item.id}')" title="Remove chair">✕</button>
                  <img src="${item.image}" alt="${item.code}" style="height: 110px; width: auto; margin: 0 auto; object-fit: contain;">
                  <div style="font-size: 0.8rem; font-weight: 800; color: var(--forest-green); margin-top: 0.35rem;">${item.code}</div>
                  <div style="font-size: 0.95rem; font-weight: 800; color: var(--text-main);">${item._internal_model || 'Standard'}</div>
                </th>
              `).join('')}
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><strong>Category</strong></td>
              ${items.map(i => `<td>${i.category}</td>`).join('')}
            </tr>
            <tr>
              <td><strong>Listed Rate</strong></td>
              ${items.map(i => `<td><strong style="color: var(--text-main); font-size: 1.05rem;">${i.price_display || '₹' + i.base_price}</strong></td>`).join('')}
            </tr>
            <tr>
              <td><strong>Backrest & Height</strong></td>
              ${items.map(i => `<td>${(i.specs && i.specs['Backrest Height']) || 'Standard'}</td>`).join('')}
            </tr>
            <tr>
              <td><strong>Mechanism</strong></td>
              ${items.map(i => `<td>${(i.specs && i.specs['Mechanism']) || 'Tilt Available'}</td>`).join('')}
            </tr>
            <tr>
              <td><strong>Armrests</strong></td>
              ${items.map(i => `<td>${(i.specs && i.specs['Armrests']) || 'Configurable'}</td>`).join('')}
            </tr>
            <tr>
              <td><strong>Key Features</strong></td>
              ${items.map(i => `<td><ul style="padding-left: 1rem; margin: 0; font-size: 0.8125rem;">${(i.features || []).map(f => `<li>${f}</li>`).join('')}</ul></td>`).join('')}
            </tr>
            <tr>
              <td><strong>Enquiry Action</strong></td>
              ${items.map(i => {
                const waText = encodeURIComponent(`Hello Sri Hanum Sastha Enterprises, I am interested in comparing chair ${i.code} (Model: ${i._internal_model}).`);
                return `
                  <td>
                    <a href="product.html?id=${i.id}" class="btn btn-outline btn-sm btn-block" style="margin-bottom: 0.4rem;">
                      View Details
                    </a>
                    <a href="https://wa.me/918695706013?text=${waText}" target="_blank" rel="noopener" class="btn btn-primary btn-sm btn-block">
                      💬 WhatsApp
                    </a>
                  </td>
                `;
              }).join('')}
            </tr>
          </tbody>
        </table>
      </div>
    `;

    container.innerHTML = html;
  }

  // ---------------- 9. SAVED CHAIRS (FAVOURITES) SYSTEM ----------------
  function initSavedChairsSystem() {
    updateSavedBadge();

    const openBtns = document.querySelectorAll('[data-open-saved]');
    openBtns.forEach(btn => {
      btn.addEventListener('click', openSavedDrawer);
    });

    if (el.savedDrawerClose) {
      el.savedDrawerClose.addEventListener('click', closeSavedDrawer);
    }
  }

  function toggleSaveChair(chairId) {
    const idx = state.savedIds.indexOf(chairId);
    if (idx >= 0) {
      state.savedIds.splice(idx, 1);
    } else {
      state.savedIds.push(chairId);
    }

    localStorage.setItem('shse_saved_chairs', JSON.stringify(state.savedIds));
    updateSavedBadge();
    renderProducts();

    if (el.savedDrawer && el.savedDrawer.classList.contains('open')) {
      renderSavedChairsList();
    }
  }

  function updateSavedBadge() {
    const count = state.savedIds.length;
    document.querySelectorAll('.saved-count-badge').forEach(badge => {
      badge.textContent = count;
      badge.style.display = count > 0 ? 'inline-block' : 'none';
    });
  }

  function openSavedDrawer() {
    if (!el.savedDrawer) return;
    renderSavedChairsList();
    el.savedDrawer.classList.add('open');
    if (el.drawerBackdrop) el.drawerBackdrop.classList.add('open');
    document.body.style.overflow = 'hidden';
  }

  function closeSavedDrawer() {
    if (!el.savedDrawer) return;
    el.savedDrawer.classList.remove('open');
    if (el.drawerBackdrop && !el.mobileDrawer?.classList.contains('open')) {
      el.drawerBackdrop.classList.remove('open');
    }
    document.body.style.overflow = '';
  }

  function renderSavedChairsList() {
    const container = el.savedListContainer;
    if (!container) return;

    const items = state.savedIds.map(id => state.allProducts.find(p => p.id === id)).filter(Boolean);

    if (items.length === 0) {
      container.innerHTML = `
        <div style="text-align: center; padding: 3rem 1rem; color: var(--text-secondary);">
          <div style="font-size: 2rem; margin-bottom: 0.5rem;">🤍</div>
          <p style="font-weight: 700; margin-bottom: 0.25rem;">No saved chairs yet</p>
          <p style="font-size: 0.8125rem;">Click the heart icon on any chair card to bookmark models you want to revisit.</p>
        </div>
      `;
      return;
    }

    container.innerHTML = items.map(item => {
      const waText = encodeURIComponent(`Hello Sri Hanum Sastha Enterprises, I am enquiring about saved chair ${item.code} (${item._internal_model}).`);
      return `
        <div class="saved-chair-item">
          <div class="saved-chair-thumb">
            <img src="${item.image}" alt="${item.code}">
          </div>
          <div style="flex: 1; min-width: 0;">
            <div style="font-size: 0.75rem; font-weight: 700; color: var(--forest-green);">${item.code}</div>
            <div style="font-size: 0.925rem; font-weight: 800; color: var(--text-main); white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
              ${item._internal_model || item.code}
            </div>
            <div style="font-size: 0.8125rem; color: var(--text-muted);">${item.price_display || '₹' + item.base_price}</div>
          </div>
          <div style="display: flex; flex-direction: column; gap: 0.35rem; align-items: flex-end;">
            <a href="product.html?id=${item.id}" class="btn btn-outline btn-sm" style="padding: 0 0.5rem; font-size: 0.75rem;">Details</a>
            <button onclick="window.catalogApp.toggleSaveChair('${item.id}')" style="background: none; border: none; font-size: 0.75rem; color: #DC2626; cursor: pointer;">Remove</button>
          </div>
        </div>
      `;
    }).join('');
  }

  // ---------------- 10. RECENTLY VIEWED TRACKER ----------------
  function initRecentlyViewedSystem() {
    const track = el.recentViewsTrack;
    if (!track) return;

    const items = state.recentlyViewedIds
      .map(id => state.allProducts.find(p => p.id === id))
      .filter(Boolean)
      .slice(0, 8);

    if (items.length > 0 && el.recentViewsSection) {
      el.recentViewsSection.style.display = 'block';
      track.innerHTML = items.map(p => `
        <div class="preview-card" style="flex: 0 0 220px;" onclick="window.location.href='product.html?id=${p.id}'" role="button" tabindex="0">
          <div class="preview-card-canvas" style="height: 160px;">
            <img src="${p.image}" alt="${p.code}" loading="lazy">
          </div>
          <div class="preview-card-body" style="padding: 0.75rem;">
            <span class="preview-card-code">${p.code}</span>
            <div style="font-weight: 800; font-size: 0.9rem; color: var(--text-main); white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
              ${p._internal_model || p.code}
            </div>
            <div style="font-size: 0.85rem; font-weight: 700; margin-top: 0.35rem;">${p.price_display || '₹' + p.base_price}</div>
          </div>
        </div>
      `).join('');
    }
  }

  // ---------------- 11. AI CATALOGUE CHATBOT ----------------
  function initAIChatbot() {
    if (!el.chatWidgetToggle || !el.chatWindow) return;

    el.chatWidgetToggle.addEventListener('click', () => {
      const isOpen = el.chatWindow.classList.contains('open');
      if (isOpen) {
        el.chatWindow.classList.remove('open');
      } else {
        el.chatWindow.classList.add('open');
        el.chatInput?.focus();
      }
    });

    if (el.chatCloseBtn) {
      el.chatCloseBtn.addEventListener('click', () => {
        el.chatWindow.classList.remove('open');
      });
    }

    if (el.chatSendBtn) {
      el.chatSendBtn.addEventListener('click', handleChatSubmit);
    }

    if (el.chatInput) {
      el.chatInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
          e.preventDefault();
          handleChatSubmit();
        }
      });
    }

    // Quick chip buttons
    document.querySelectorAll('.chat-chip').forEach(chip => {
      chip.addEventListener('click', () => {
        const text = chip.getAttribute('data-query');
        if (text && el.chatInput) {
          el.chatInput.value = text;
          handleChatSubmit();
        }
      });
    });
  }

  async function handleChatSubmit() {
    const input = el.chatInput;
    if (!input) return;
    const msg = input.value.trim();
    if (!msg) return;

    input.value = '';

    // Append user message
    appendChatMessage('user', msg);

    // Append loading placeholder
    const loadingId = 'chat-loading-' + Date.now();
    appendChatMessage('bot', '<em>Searching 228 verified catalogue models...</em>', loadingId);

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: msg })
      });

      const loadingEl = document.getElementById(loadingId);
      if (loadingEl) loadingEl.remove();

      if (!res.ok) throw new Error('Chat service error');
      const data = await res.json();

      // Format markdown links into clickable HTML
      let formatted = data.reply
        .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>')
        .replace(/\n/g, '<br>');

      appendChatMessage('bot', formatted);
    } catch (err) {
      const loadingEl = document.getElementById(loadingId);
      if (loadingEl) loadingEl.remove();

      appendChatMessage('bot', '⚠️ Catalogue Assistant is currently operating offline. You can reach our showroom directly at [9688727284](tel:+919688727284) or on [WhatsApp: 8695706013](https://wa.me/918695706013).');
    }
  }

  function appendChatMessage(sender, htmlContent, elementId = null) {
    const msgContainer = el.chatMessages;
    if (!msgContainer) return;

    const div = document.createElement('div');
    div.className = `chat-bubble ${sender}`;
    if (elementId) div.id = elementId;
    div.innerHTML = htmlContent;

    msgContainer.appendChild(div);
    msgContainer.scrollTop = msgContainer.scrollHeight;
  }

  // ---------------- 12. ORIGINAL CHAIR CONCEPTS SECTION ----------------
  async function initConceptsSection() {
    const grid = el.conceptsGrid;
    if (!grid) return;

    try {
      const res = await fetch('/api/concepts');
      if (!res.ok) return;
      const concepts = await res.json();

      grid.innerHTML = concepts.map(c => `
        <article class="concept-card">
          <div class="concept-card-canvas">
            <span class="concept-badge-tag">Design Study</span>
            <img src="${c.image}" alt="${c.name}" loading="lazy">
          </div>
          <div class="concept-body">
            <span class="concepts-badge">Conceptual Visual</span>
            <h3 class="concept-title">${c.name}</h3>
            <div class="concept-subtitle">${c.subtitle}</div>
            <p class="concept-desc">${c.design_intent}</p>
            <div class="concept-tags">
              ${c.materials.map(m => `<span class="concept-tag">${m}</span>`).join('')}
            </div>
            <div style="margin-top: 1rem; padding-top: 0.75rem; border-top: 1px solid var(--border-subtle); font-size: 0.75rem; color: #64748B;">
              * R&D exploratory design study. Not part of commercial production catalogue.
            </div>
          </div>
        </article>
      `).join('');
    } catch (e) {
      console.warn('Concepts could not be loaded:', e);
    }
  }

  // ---------------- 13. MOBILE DRAWER & GENERAL LISTENERS ----------------
  function setupMobileDrawer() {
    if (!el.mobileToggle || !el.mobileDrawer) return;

    function openDrawer() {
      el.mobileDrawer.classList.add('open');
      if (el.drawerBackdrop) el.drawerBackdrop.classList.add('open');
      el.mobileToggle.setAttribute('aria-expanded', 'true');
      document.body.style.overflow = 'hidden';
    }

    function closeDrawer() {
      el.mobileDrawer.classList.remove('open');
      if (el.drawerBackdrop && !el.savedDrawer?.classList.contains('open')) {
        el.drawerBackdrop.classList.remove('open');
      }
      el.mobileToggle.setAttribute('aria-expanded', 'false');
      document.body.style.overflow = '';
    }

    el.mobileToggle.addEventListener('click', openDrawer);
    if (el.drawerCloseBtn) el.drawerCloseBtn.addEventListener('click', closeDrawer);
    if (el.drawerBackdrop) el.drawerBackdrop.addEventListener('click', () => {
      closeDrawer();
      closeSavedDrawer();
    });

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        closeDrawer();
        closeSavedDrawer();
        closeCompareModal();
        if (el.chatWindow) el.chatWindow.classList.remove('open');
      }
    });

    el.mobileDrawer.querySelectorAll('.mobile-nav-link').forEach(link => {
      link.addEventListener('click', closeDrawer);
    });
  }

  function setupEventListeners() {
    let debounceTimer;
    if (el.searchBar) {
      el.searchBar.addEventListener('input', (e) => {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
          state.searchQuery = e.target.value;
          applyFiltersAndSort();
        }, 200);
      });
    }

    if (el.sortSelect) {
      el.sortSelect.addEventListener('change', (e) => {
        state.sortBy = e.target.value;
        applyFiltersAndSort();
      });
    }

    if (el.btnResetFilter) {
      el.btnResetFilter.addEventListener('click', () => {
        state.selectedCategory = 'all';
        state.searchQuery = '';
        if (el.searchBar) el.searchBar.value = '';
        if (el.sortSelect) el.sortSelect.value = 'default';
        state.sortBy = 'default';
        history.replaceState(null, null, ' ');
        applyFiltersAndSort();
      });
    }

    if (el.btnLoadMore) {
      el.btnLoadMore.addEventListener('click', () => {
        state.currentPage++;
        renderProducts();
      });
    }

    document.querySelectorAll('[data-category]').forEach(link => {
      link.addEventListener('click', (e) => {
        const cat = link.getAttribute('data-category');
        if (cat) {
          e.preventDefault();
          setCategory(cat);
          scrollToCatalogue();
        }
      });
    });

    window.addEventListener('hashchange', handleInitialHash);
  }

  function handleInitialHash() {
    const hash = window.location.hash.replace('#', '');
    if (!hash) return;

    const matchedCat = state.categories.find(c => c.hash === hash);
    if (matchedCat) {
      state.selectedCategory = matchedCat.id;
      applyFiltersAndSort();
    }
  }

  function setCategory(catId) {
    state.selectedCategory = catId;
    const catObj = state.categories.find(c => c.id === catId);
    if (catObj && catObj.hash) {
      history.replaceState(null, null, `#${catObj.hash}`);
    } else {
      history.replaceState(null, null, ' ');
    }
    applyFiltersAndSort();
  }

  function scrollToCatalogue() {
    const target = document.getElementById('catalogue') || el.productsGrid;
    if (target) {
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }

  // Expose global methods
  window.catalogApp = {
    setCategory,
    applyFiltersAndSort,
    toggleCompare,
    toggleSaveChair,
    openSavedDrawer,
    closeSavedDrawer,
    openCompareModal,
    closeCompareModal,
    state
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
