/**
 * Sri Hanum Sastha Enterprises - Catalogue Application Engine
 * Fast, Reactive, Robust Vanilla JS
 * Strictly displays only SHSE codes (e.g. Office Chairs — SHSE(1))
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
    modalCard: document.getElementById('modalCard'),
    modalCloseBtn: document.getElementById('modalCloseBtn'),
    mobileToggle: document.getElementById('mobileToggle'),
    mobileDrawer: document.getElementById('mobileDrawer'),
    drawerBackdrop: document.getElementById('drawerBackdrop'),
    drawerCloseBtn: document.getElementById('drawerCloseBtn')
  };

  // 1. Initialize Application
  async function init() {
    try {
      const response = await fetch('assets/catalog.json');
      if (!response.ok) throw new Error('Failed to load catalogue dataset');
      state.allProducts = await response.json();
      
      renderCategoryCards();
      renderFilterPills();
      setupEventListeners();
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

  // 2. Render Category Cards in Hero/Showcase
  function renderCategoryCards() {
    if (!el.categoryCardsContainer) return;
    
    // Representative category preview images
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

  // 3. Render Filter Pills in Toolbar
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

  // 4. Set Active Category & Update URL Hash
  function setCategory(catId) {
    state.selectedCategory = catId;
    state.currentPage = 1;

    const catObj = state.categories.find(c => c.id === catId);
    if (catObj && catObj.hash) {
      history.replaceState(null, '', `#${catObj.hash}`);
    } else {
      history.replaceState(null, '', window.location.pathname);
    }

    updateActiveFilterUI();
    applyFiltersAndSort();
  }

  function updateActiveFilterUI() {
    if (el.filterPillsContainer) {
      el.filterPillsContainer.querySelectorAll('.filter-pill').forEach(pill => {
        const c = pill.getAttribute('data-category');
        pill.classList.toggle('active', c === state.selectedCategory);
      });
    }

    if (el.categoryCardsContainer) {
      el.categoryCardsContainer.querySelectorAll('.category-card').forEach(card => {
        const c = card.getAttribute('data-category');
        card.classList.toggle('active', c === state.selectedCategory);
      });
    }
  }

  // 5. Apply Filtering, Searching & Sorting (STRICTLY HIDES ORIGINAL MODEL NAMES)
  function applyFiltersAndSort() {
    let result = [...state.allProducts];

    // Filter by Category
    if (state.selectedCategory !== 'all') {
      result = result.filter(p => p.category === state.selectedCategory);
    }

    // Filter by Search Query (SEARCH ONLY CODES, CATEGORIES, AND FEATURES)
    if (state.searchQuery.trim()) {
      const q = state.searchQuery.toLowerCase().trim();
      result = result.filter(p => {
        const codeMatch = p.code.toLowerCase().includes(q) || String(p.code_number) === q;
        const displayNameMatch = p.display_name.toLowerCase().includes(q);
        const catMatch = p.category.toLowerCase().includes(q);
        const optMatch = p.options && p.options.some(o => o.variant.toLowerCase().includes(q));
        const featMatch = p.features && p.features.some(f => f.toLowerCase().includes(q));
        return codeMatch || displayNameMatch || catMatch || optMatch || featMatch;
      });
    }

    // Sort Results
    if (state.sortBy === 'price-low') {
      result.sort((a, b) => (a.base_price || 999999) - (b.base_price || 999999));
    } else if (state.sortBy === 'price-high') {
      result.sort((a, b) => (b.base_price || 0) - (a.base_price || 0));
    } else if (state.sortBy === 'code-asc') {
      result.sort((a, b) => a.code_number - b.code_number);
    }

    state.filteredProducts = result;
    renderProducts();
    updateToolbarStatus();
  }

  // 6. Render Product Cards Grid (Displaying ONLY SHSE Codes)
  function renderProducts() {
    if (!el.productsGrid) return;

    if (state.filteredProducts.length === 0) {
      el.productsGrid.style.display = 'none';
      if (el.emptyState) el.emptyState.style.display = 'block';
      if (el.loadMoreContainer) el.loadMoreContainer.style.display = 'none';
      return;
    }

    el.productsGrid.style.display = 'grid';
    if (el.emptyState) el.emptyState.style.display = 'none';

    // Pagination slice
    const totalToShow = state.currentPage * state.pageSize;
    const paginatedItems = state.filteredProducts.slice(0, totalToShow);

    const cardsHtml = paginatedItems.map(p => {
      let variantsHtml = '';
      if (p.options && p.options.length > 1) {
        variantsHtml = p.options.slice(0, 3).map(o => `
          <span class="variant-tag">${escapeHtml(o.variant)}</span>
        `).join('');
        if (p.options.length > 3) {
          variantsHtml += `<span class="variant-tag">+${p.options.length - 3} more</span>`;
        }
      } else if (p.features && p.features.length) {
        variantsHtml = p.features.slice(0, 2).map(f => `
          <span class="variant-tag">${escapeHtml(f)}</span>
        `).join('');
      }

      const hasDiagram = !!p.diagram;

      return `
        <article class="product-card" data-id="${p.id}">
          <div class="product-image-canvas" onclick="window.catalogApp.openModal('${p.id}')">
            <span class="product-category-badge">${escapeHtml(p.category)}</span>
            ${hasDiagram ? `<span class="diagram-indicator" title="Technical schematic available">📐 Specs</span>` : ''}
            <img src="${p.image}" alt="${escapeHtml(p.display_name)}" onerror="this.src='assets/placeholder.svg'" loading="lazy">
          </div>
          
          <div class="product-content">
            <h3 class="product-name" title="${escapeHtml(p.display_name)}">
              ${escapeHtml(p.display_name)}
            </h3>
            
            <div class="product-price-row">
              <span class="product-price-label">Catalogue Rate</span>
              <span class="product-price-val">${p.price_display}</span>
            </div>

            <div class="product-variants-tags">
              ${variantsHtml}
            </div>

            <div class="product-actions">
              <button class="btn btn-outline btn-sm" onclick="window.catalogApp.openModal('${p.id}')">
                View Details
              </button>
              <a href="tel:9688727284" class="btn btn-primary btn-sm">
                📞 Call Enquire
              </a>
            </div>
          </div>
        </article>
      `;
    }).join('');

    el.productsGrid.innerHTML = cardsHtml;

    if (el.loadMoreContainer) {
      if (totalToShow < state.filteredProducts.length) {
        el.loadMoreContainer.style.display = 'flex';
        el.paginationInfo.textContent = `Showing ${paginatedItems.length} of ${state.filteredProducts.length} models`;
      } else {
        el.loadMoreContainer.style.display = 'none';
      }
    }
  }

  // 7. Update Filter Status Bar
  function updateToolbarStatus() {
    if (el.filterCount) {
      el.filterCount.textContent = `${state.filteredProducts.length} chairs found`;
    }
    if (el.activeFilterName) {
      const activeObj = state.categories.find(c => c.id === state.selectedCategory);
      el.activeFilterName.textContent = activeObj ? activeObj.name : 'Catalogue';
    }
    if (el.btnResetFilter) {
      const isFiltered = state.selectedCategory !== 'all' || state.searchQuery.trim() !== '';
      el.btnResetFilter.style.display = isFiltered ? 'inline-flex' : 'none';
    }
  }

  // 8. Open Product Modal (ONLY Displays SHSE Code & Specifications)
  function openModal(productId) {
    const prod = state.allProducts.find(p => p.id === productId);
    if (!prod || !el.productModal) return;

    let optionsRows = '';
    if (prod.options && prod.options.length) {
      optionsRows = prod.options.map(o => `
        <tr>
          <td><strong>${escapeHtml(o.variant)}</strong></td>
          <td style="text-align: right; font-weight: 700; color: var(--primary);">₹${o.price.toLocaleString('en-IN')}</td>
        </tr>
      `).join('');
    }

    let specsRows = '';
    if (prod.specs && Object.keys(prod.specs).length) {
      specsRows = Object.entries(prod.specs).map(([key, val]) => `
        <div class="spec-item">
          <strong>${escapeHtml(key)}:</strong> <span>${escapeHtml(val)}</span>
        </div>
      `).join('');
    }

    let diagramHtml = '';
    if (prod.diagram) {
      diagramHtml = `
        <div class="modal-diagram-box">
          <h4>Technical Schematic & Dimensions</h4>
          <img src="${prod.diagram}" alt="${escapeHtml(prod.display_name)} Dimensions" onerror="this.style.display='none'">
        </div>
      `;
    }

    const modalBodyHtml = `
      <div class="modal-gallery">
        <div class="modal-main-img">
          <img src="${prod.image}" alt="${escapeHtml(prod.display_name)}" onerror="this.src='assets/placeholder.svg'">
        </div>
        ${diagramHtml}
      </div>

      <div class="modal-details">
        <span class="modal-category">${escapeHtml(prod.category)}</span>
        <h2 class="modal-title">${escapeHtml(prod.display_name)}</h2>

        <div class="modal-price-box">
          <div>
            <span style="font-size: 0.8rem; text-transform: uppercase; color: var(--accent-text); font-weight: 700;">Starting Listed Price</span>
            <div class="price-num">${prod.price_display}</div>
          </div>
          <span style="font-size: 0.8rem; color: var(--accent-text); text-align: right; max-width: 150px; line-height: 1.3;">Confirm current rate via direct call</span>
        </div>

        ${optionsRows ? `
          <h4 style="font-size: 0.875rem; text-transform: uppercase; color: var(--primary); margin-bottom: 0.5rem; letter-spacing: 0.5px;">Configurations & Variants</h4>
          <table class="modal-options-table">
            <thead>
              <tr>
                <th>Configuration / Specification</th>
                <th style="text-align: right;">Listed Price</th>
              </tr>
            </thead>
            <tbody>
              ${optionsRows}
            </tbody>
          </table>
        ` : ''}

        ${specsRows ? `
          <h4 style="font-size: 0.875rem; text-transform: uppercase; color: var(--primary); margin-bottom: 0.5rem; letter-spacing: 0.5px;">Technical Specifications</h4>
          <div class="modal-specs-list">
            <div class="spec-item">
              <strong>Product Code:</strong> <span>${escapeHtml(prod.code)}</span>
            </div>
            ${specsRows}
          </div>
        ` : ''}

        <div class="modal-cta-box">
          <div class="modal-phone-btns">
            <a href="tel:9688727284" class="btn btn-call-gold">
              📞 Call 9688727284
            </a>
            <a href="tel:8695706013" class="btn btn-dark">
              📞 Call 8695706013
            </a>
          </div>
          <p class="modal-cta-note">
            Mention product code <strong>"${escapeHtml(prod.display_name)}"</strong> when calling our Coimbatore office for quotation and stock availability.
          </p>
        </div>
      </div>
    `;

    const bodyContainer = el.productModal.querySelector('.modal-body');
    if (bodyContainer) bodyContainer.innerHTML = modalBodyHtml;

    el.productModal.classList.add('open');
    document.body.style.overflow = 'hidden';
  }

  function closeModal() {
    if (!el.productModal) return;
    el.productModal.classList.remove('open');
    document.body.style.overflow = '';
  }

  // 9. Setup Event Listeners
  function setupEventListeners() {
    if (el.searchBar) {
      el.searchBar.addEventListener('input', (e) => {
        state.searchQuery = e.target.value;
        state.currentPage = 1;
        applyFiltersAndSort();
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
        state.currentPage = 1;
        history.replaceState(null, '', window.location.pathname);
        updateActiveFilterUI();
        applyFiltersAndSort();
      });
    }

    if (el.btnLoadMore) {
      el.btnLoadMore.addEventListener('click', () => {
        state.currentPage++;
        renderProducts();
      });
    }

    if (el.modalCloseBtn) {
      el.modalCloseBtn.addEventListener('click', closeModal);
    }
    if (el.productModal) {
      el.productModal.addEventListener('click', (e) => {
        if (e.target === el.productModal) closeModal();
      });
    }
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') closeModal();
    });

    if (el.mobileToggle && el.mobileDrawer) {
      el.mobileToggle.addEventListener('click', () => {
        el.mobileDrawer.classList.add('open');
        if (el.drawerBackdrop) el.drawerBackdrop.classList.add('open');
      });
    }
    if (el.drawerCloseBtn) {
      el.drawerCloseBtn.addEventListener('click', closeDrawer);
    }
    if (el.drawerBackdrop) {
      el.drawerBackdrop.addEventListener('click', closeDrawer);
    }

    document.querySelectorAll('.mobile-nav-link').forEach(link => {
      link.addEventListener('click', (e) => {
        const cat = link.getAttribute('data-category');
        if (cat) {
          e.preventDefault();
          setCategory(cat);
          closeDrawer();
          scrollToCatalogue();
        }
      });
    });

    document.querySelectorAll('.nav-link[data-category]').forEach(link => {
      link.addEventListener('click', (e) => {
        e.preventDefault();
        const cat = link.getAttribute('data-category');
        setCategory(cat);
        scrollToCatalogue();
      });
    });

    window.addEventListener('hashchange', handleInitialHash);
  }

  function closeDrawer() {
    if (el.mobileDrawer) el.mobileDrawer.classList.remove('open');
    if (el.drawerBackdrop) el.drawerBackdrop.classList.remove('open');
  }

  function scrollToCatalogue() {
    const sec = document.getElementById('catalogue');
    if (sec) {
      const topOffset = sec.getBoundingClientRect().top + window.pageYOffset - 90;
      window.scrollTo({ top: topOffset, behavior: 'smooth' });
    }
  }

  function handleInitialHash() {
    const hash = window.location.hash.replace('#', '');
    if (!hash) return;

    if (hash.startsWith('product-')) {
      const prodId = hash.replace('product-', '');
      setTimeout(() => openModal(prodId), 150);
      return;
    }

    const matchedCat = state.categories.find(c => c.hash === hash);
    if (matchedCat) {
      state.selectedCategory = matchedCat.id;
      updateActiveFilterUI();
      applyFiltersAndSort();
    }
  }

  function escapeHtml(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  window.catalogApp = {
    openModal,
    closeModal,
    setCategory
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
