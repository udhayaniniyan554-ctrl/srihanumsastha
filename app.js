/**
 * Sri Hanum Sastha Enterprises — Commercial Seating Showroom
 * Fast, Robust Vanilla JavaScript Application Engine
 * Automatic Hero Chair Carousel (2s) & Moving Product Preview (2s)
 */

(function () {
  'use strict';

  // State Management
  const state = {
    allProducts: [],
    filteredProducts: [],
    selectedCategory: 'all',
    searchQuery: '',
    sortBy: 'default',
    currentPage: 1,
    pageSize: 24,
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
    productModal: document.getElementById('productModal'),
    modalCloseBtn: document.getElementById('modalCloseBtn'),
    mobileToggle: document.getElementById('mobileToggle'),
    mobileDrawer: document.getElementById('mobileDrawer'),
    drawerBackdrop: document.getElementById('drawerBackdrop'),
    drawerCloseBtn: document.getElementById('drawerCloseBtn'),
    heroCarousel: document.getElementById('heroCarousel'),
    previewTrack: document.getElementById('previewTrack'),
    previewBtnPrev: document.getElementById('previewBtnPrev'),
    previewBtnNext: document.getElementById('previewBtnNext')
  };

  // Timers
  let heroTimer = null;
  let previewTimer = null;

  // 1. Initialize Application
  async function init() {
    try {
      const response = await fetch('assets/catalog.json');
      if (!response.ok) throw new Error('Failed to load catalogue dataset');
      state.allProducts = await response.json();

      initHeroCarousel();
      initProductPreviewTrack();
      renderCategoryCards();
      renderFilterPills();
      setupEventListeners();
      setupMobileDrawer();
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

    // Build indicator dots dynamically
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

    // Preload all slide images into memory
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

    // Button actions
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

    // Touch gesture swipe support
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

    // Start 2-second timer
    startHeroTimer();
  }

  // ---------------- 3. MOVING PRODUCT PREVIEW TRACK (2s) ----------------
  function initProductPreviewTrack() {
    const track = el.previewTrack;
    if (!track) return;

    // Curated authentic products across categories
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

    // Render cards into track
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

    // Preload preview images
    previewItems.forEach(p => {
      const img = new Image();
      img.src = p.image;
    });

    const PREVIEW_INTERVAL = 2000; // Exact 2-second automatic step

    function advanceTrack() {
      if (!track) return;
      const firstCard = track.querySelector('.preview-card');
      if (!firstCard) return;
      const step = firstCard.offsetWidth + 20; // Card width + gap
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

    // Manual navigation buttons
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

    // Pause on hover & focus
    track.addEventListener('mouseenter', stopPreviewTimer);
    track.addEventListener('mouseleave', startPreviewTimer);
    track.addEventListener('focusin', stopPreviewTimer);
    track.addEventListener('focusout', startPreviewTimer);

    // Start 2-second timer
    startPreviewTimer();
  }

  // ---------------- 4. CATEGORY CARDS SHOWCASE ----------------
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

  // ---------------- 5. FILTER PILLS IN TOOLBAR ----------------
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

  // ---------------- 6. FILTERING & SORTING ENGINE ----------------
  function applyFiltersAndSort() {
    let result = [...state.allProducts];

    // Category Filter
    if (state.selectedCategory !== 'all') {
      result = result.filter(p => p.category === state.selectedCategory);
    }

    // Search Query Filter
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

    // Sorting
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

  // ---------------- 7. UPDATE FILTER UI ----------------
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

    // Update Category Cards active state
    if (el.categoryCardsContainer) {
      el.categoryCardsContainer.querySelectorAll('.category-card').forEach(card => {
        const catId = card.getAttribute('data-category');
        card.classList.toggle('active', catId === state.selectedCategory);
      });
    }

    // Update Filter Pills active state
    if (el.filterPillsContainer) {
      el.filterPillsContainer.querySelectorAll('.filter-pill').forEach(pill => {
        const catId = pill.getAttribute('data-category');
        pill.classList.toggle('active', catId === state.selectedCategory);
      });
    }
  }

  // ---------------- 8. RENDER PRODUCTS GRID ----------------
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

      // WhatsApp URL: strictly 8695706013 with prefilled message
      const waMessage = encodeURIComponent(
        `Hello Sri Hanum Sastha Enterprises, I am interested in chair ${displayCode} (Model: ${confirmedModel}) from the ${p.category} category. Please share more details.`
      );
      const waUrl = `https://wa.me/918695706013?text=${waMessage}`;

      return `
        <article class="product-card" data-id="${p.id}">
          <div class="product-image-canvas" onclick="window.location.href='product.html?id=${p.id}'" role="button" tabindex="0" aria-label="View details for ${displayCode}">
            <span class="product-category-badge">${p.category}</span>
            <img src="${p.image}" alt="${displayCode} - ${confirmedModel}" loading="lazy" onerror="this.src='assets/placeholder.svg'">
          </div>
          
          <div class="product-content">
            <div class="product-code-row">
              <span class="product-code-badge">${displayCode}</span>
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

    // Load More Pagination
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

  // ---------------- 9. EVENT LISTENERS ----------------
  function setupEventListeners() {
    // Search input with debounce
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

    // Sort select
    if (el.sortSelect) {
      el.sortSelect.addEventListener('change', (e) => {
        state.sortBy = e.target.value;
        applyFiltersAndSort();
      });
    }

    // Reset filter button
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

    // Load more button
    if (el.btnLoadMore) {
      el.btnLoadMore.addEventListener('click', () => {
        state.currentPage++;
        renderProducts();
      });
    }

    // Category navigation links
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

    // Hash change event
    window.addEventListener('hashchange', handleInitialHash);
  }

  // ---------------- 10. MOBILE OFF-CANVAS DRAWER ----------------
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
      if (el.drawerBackdrop) el.drawerBackdrop.classList.remove('open');
      el.mobileToggle.setAttribute('aria-expanded', 'false');
      document.body.style.overflow = '';
    }

    el.mobileToggle.addEventListener('click', openDrawer);
    if (el.drawerCloseBtn) el.drawerCloseBtn.addEventListener('click', closeDrawer);
    if (el.drawerBackdrop) el.drawerBackdrop.addEventListener('click', closeDrawer);

    // Close on escape key
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && el.mobileDrawer.classList.contains('open')) {
        closeDrawer();
      }
    });

    // Close on mobile link clicks
    el.mobileDrawer.querySelectorAll('.mobile-nav-link').forEach(link => {
      link.addEventListener('click', closeDrawer);
    });
  }

  // ---------------- 11. HASH ROUTING ----------------
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

  // Expose API globally
  window.catalogApp = {
    setCategory,
    applyFiltersAndSort,
    state
  };

  // Launch when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
