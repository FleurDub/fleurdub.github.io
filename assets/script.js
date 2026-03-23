/* =================================================================
   MEMORA DOCS — script.js
   Features:
     · SPA navigation with history.pushState
     · Folder tree (open/close with animation)
     · Markdown rendering (fetch real file + embedded fallback)
     · Floating Table of Contents (IntersectionObserver)
     · ⌘K Command palette with fuzzy search
     · Reading mode overlay (immersive)
     · Reading progress bar (main + reader)
     · Dark/light theme toggle (persisted in localStorage)
     · Font size toggle: sm / md / lg (persisted)
     · Copy code blocks
     · Keyboard shortcuts
     · Mobile hamburger
   ================================================================= */

'use strict';

/* ─────────────────────────────────────────────────────────────
   1. CONFIGURATION
   ───────────────────────────────────────────────────────────── */

/**
 * Search index: each entry is a page node that can be searched.
 * Built from every [data-page] element in the tree + their data-search text.
 * Populated once in init().
 * @type {Array<{page: string, title: string, path: string, keywords: string}>}
 */
let SEARCH_INDEX = [];

/** Active page id */
let currentPage = 'architecture';

/** Is the command palette open? */
let cmdOpen = false;

/** Is the reader overlay open? */
let readerOpen = false;

/** Currently selected result index in ⌘K palette */
let cmdSelectedIdx = -1;

/** IntersectionObserver for ToC tracking */
let tocObserver = null;

/* ─────────────────────────────────────────────────────────────
   2. DOM REFERENCES
   ───────────────────────────────────────────────────────────── */
const html           = document.documentElement;
const main           = document.getElementById('main');
const sidebar        = document.getElementById('sidebar');
const sidebarBackdrop = document.getElementById('sidebar-backdrop');
const hamburger      = document.getElementById('hamburger');
const progressBar    = document.getElementById('progress-bar');

// Command palette
const cmdOverlay     = document.getElementById('cmd-overlay');
const cmdInput       = document.getElementById('cmd-input');
const cmdResults     = document.getElementById('cmd-results');

// Raw file overlay
const rawOverlay     = document.getElementById('raw-overlay');
const rawContent     = document.getElementById('raw-content');
const rawFilename    = document.getElementById('raw-filename');
const rawClose       = document.getElementById('raw-close');
const rawBody        = document.getElementById('raw-body');
/** Is the raw overlay open? */
let rawOpen = false;

// Reader
const readerOverlay  = document.getElementById('reader-overlay');
const readerContent  = document.getElementById('reader-content');
const readerBreadcrumb = document.getElementById('reader-breadcrumb');
const readerProgress = document.getElementById('reader-progress');
const readerClose    = document.getElementById('reader-close');
const readerBody     = document.getElementById('reader-body');
const readerFontSm    = document.getElementById('reader-font-sm');
const readerFontLg    = document.getElementById('reader-font-lg');
const readerFontSerif = document.getElementById('reader-font-serif');
const readerTimeEl    = document.getElementById('reader-time');

// ToC
const tocPanel       = document.getElementById('toc-panel');
const tocList        = document.getElementById('toc-list');

// Controls
const fontDec        = document.getElementById('font-dec');
const fontReset      = document.getElementById('font-reset');
const fontInc        = document.getElementById('font-inc');
const searchTrigger  = document.getElementById('search-trigger');

/* ─────────────────────────────────────────────────────────────
   3. NAVIGATION
   ───────────────────────────────────────────────────────────── */

/**
 * Navigate to a page by id.
 * - Hides all pages, shows the target
 * - Updates sidebar active state
 * - Opens parent folder if needed
 * - Pushes URL state
 * - Loads MD content if needed
 * - Rebuilds ToC
 * @param {string} pageId
 * @param {boolean} [pushState=true]
 */
function navigateTo(pageId, pushState = true) {
  const target = document.getElementById('page-' + pageId);
  if (!target) return;

  // Hide all pages
  document.querySelectorAll('.doc-page').forEach(p => {
    p.classList.remove('is-active');
  });

  // Show target with animation
  target.classList.add('is-active');
  currentPage = pageId;

  // Scroll main to top
  main.scrollTo({ top: 0 });

  // Update sidebar active file
  document.querySelectorAll('.tree-file').forEach(btn => {
    btn.classList.toggle('is-active', btn.dataset.page === pageId);
  });

  // Auto-open parent folder for the active file
  const activeFile = document.querySelector(`.tree-file[data-page="${pageId}"]`);
  if (activeFile) {
    const parentChildren = activeFile.closest('.tree-children');
    if (parentChildren && !parentChildren.classList.contains('is-open')) {
      const folderId = parentChildren.id.replace('dir-', '');
      openFolder(folderId);
    }
  }

  // URL state
  if (pushState) {
    const path = pageId.replace(/-/g, '/').replace(/ref\//g, 'reference/');
    history.pushState({ page: pageId }, '', '#' + pageId);
  }

  // Load Markdown for MD pages
  if (target.classList.contains('md-page')) {
    loadMarkdown(target);
  } else {
    // Enhance static code blocks on bento pages
    enhanceCodeBlocks(target);
    processBlockquotes(target);
  }

  // Rebuild Table of Contents
  rebuildToc(target);

  // Close mobile sidebar
  if (window.innerWidth <= 768) closeMobileSidebar();
}

/* ─────────────────────────────────────────────────────────────
   4. FOLDER TREE
   ───────────────────────────────────────────────────────────── */

/** Open a folder by its folder id string */
function openFolder(folderId) {
  const children = document.getElementById('dir-' + folderId);
  const btn = document.querySelector(`.tree-folder[data-folder="${folderId}"]`);
  if (!children || !btn) return;
  children.classList.add('is-open');
  btn.classList.add('is-open');
  const caret = btn.querySelector('.ico-caret');
  if (caret) caret.classList.add('is-open');
}

/** Toggle a folder open/closed */
function toggleFolder(folderId) {
  const children = document.getElementById('dir-' + folderId);
  const btn = document.querySelector(`.tree-folder[data-folder="${folderId}"]`);
  if (!children || !btn) return;

  const isOpen = children.classList.contains('is-open');
  children.classList.toggle('is-open', !isOpen);
  btn.classList.toggle('is-open', !isOpen);
  const caret = btn.querySelector('.ico-caret');
  if (caret) caret.classList.toggle('is-open', !isOpen);
}

/* ─────────────────────────────────────────────────────────────
   5. MARKDOWN LOADING
   ───────────────────────────────────────────────────────────── */

/**
 * Fetch and render a .md file into the .md-render zone of a page.
 * Strategy:
 *   1. Try to fetch the real file from the same directory (works when
 *      the HTML is served via HTTP/file server).
 *   2. If fetch fails (offline / file:// with CORS), fall back to
 *      the data-md-content attribute if present, or show a placeholder.
 *
 * @param {HTMLElement} pageEl - the .doc-page element
 */
async function loadMarkdown(pageEl) {
  const renderZone = pageEl.querySelector('.md-render');
  if (!renderZone) return;

  // Already rendered — skip
  if (renderZone.dataset.loaded === 'true') {
    rebuildToc(pageEl);
    return;
  }

  const filePath = pageEl.dataset.path;
  if (!filePath) {
    renderZone.innerHTML = pendingPlaceholder(pageEl.dataset.title || 'this document');
    return;
  }

  // Show skeleton loader while fetching
  renderZone.innerHTML = skeletonLoader();

  let markdown = null;

  // ── Strategy 1: Fetch real file ────────────────────────────
  try {
    const res = await fetch(filePath, { cache: 'no-store' });
    if (res.ok) {
      markdown = await res.text();
    }
  } catch (_) {
    // Fetch failed (file:// or network error) — fall through to fallback
  }

  // ── Strategy 2: Embedded fallback via data-md-content ──────
  if (!markdown && pageEl.dataset.mdContent) {
    markdown = pageEl.dataset.mdContent;
  }

  // ── Strategy 3: Inline <script type="text/plain"> ──────────
  if (!markdown) {
    const inlineEl = document.getElementById('md-' + pageEl.id.replace('page-', ''));
    if (inlineEl) markdown = inlineEl.textContent.trim();
  }

  // ── Render or placeholder ───────────────────────────────────
  if (markdown) {
    renderZone.innerHTML = renderMarkdown(markdown);
    renderZone.dataset.loaded = 'true';
    processBlockquotes(renderZone);
    wrapTables(renderZone);
    enhanceCodeBlocks(renderZone);
    addAnchorButtons(renderZone);
    rebuildToc(pageEl);
  } else {
    renderZone.innerHTML = pendingPlaceholder(filePath);
  }
}

/**
 * Render Markdown string to HTML using marked.js.
 * @param {string} md
 * @returns {string} HTML string
 */
function renderMarkdown(md) {
  if (typeof marked === 'undefined') {
    return `<p style="color:var(--ink-faint)">marked.js not loaded — check CDN connection.</p>`;
  }
  marked.setOptions({
    breaks: true,
    gfm: true,
  });
  return marked.parse(md);
}

/** Skeleton loader HTML (shimmer bars) */
function skeletonLoader() {
  return `
    <div class="skeleton-wrap" aria-busy="true" aria-label="Loading document…">
      <div class="sk-line sk-w-60"></div>
      <div class="sk-line sk-w-40" style="margin-top:8px"></div>
      <div class="sk-line sk-w-80" style="margin-top:24px"></div>
      <div class="sk-line sk-w-100" style="margin-top:8px"></div>
      <div class="sk-line sk-w-90" style="margin-top:8px"></div>
      <div class="sk-line sk-w-70" style="margin-top:8px"></div>
      <div class="sk-line sk-w-100" style="margin-top:8px"></div>
    </div>`;
}

/** Placeholder HTML when no MD file found */
function pendingPlaceholder(filePath) {
  return `
    <div class="md-placeholder">
      <div class="placeholder-icon">
        <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" opacity=".3">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
          <polyline points="14 2 14 8 20 8"/>
          <line x1="16" y1="13" x2="8" y2="13"/>
          <line x1="16" y1="17" x2="8" y2="17"/>
          <polyline points="10 9 9 9 8 9"/>
        </svg>
      </div>
      <p class="placeholder-title">Content pending</p>
      <p class="placeholder-desc">Place <code>${filePath}</code> in the same folder as this HTML file — it will render automatically.</p>
    </div>`;
}

/**
 * Add copy buttons to all <pre><code> blocks in a render zone.
 * @param {HTMLElement} zone
 */
function enhanceCodeBlocks(zone) {
  zone.querySelectorAll('pre').forEach(pre => {
    if (pre.querySelector('.code-copy-btn')) return; // already done

    const code = pre.querySelector('code');

    // Language badge + Prism highlighting
    if (code) {
      const langMatch = code.className.match(/language-(\w+)/);
      if (langMatch) {
        const badge = document.createElement('span');
        badge.className = 'code-lang-badge';
        badge.textContent = langMatch[1];
        pre.style.position = 'relative';
        pre.appendChild(badge);

        if (typeof Prism !== 'undefined') {
          Prism.highlightElement(code);
        }
      }
    }

    // Copy button
    const btn = document.createElement('button');
    btn.className = 'code-copy-btn';
    btn.textContent = 'Copy';
    btn.addEventListener('click', () => {
      const text = code ? code.innerText : pre.innerText;
      navigator.clipboard.writeText(text).then(() => {
        btn.textContent = 'Copied ✓';
        btn.classList.add('copied');
        setTimeout(() => { btn.textContent = 'Copy'; btn.classList.remove('copied'); }, 2000);
      });
    });
    pre.style.position = 'relative';
    pre.appendChild(btn);
  });
}

/**
 * Wrap all tables in a scroll container for overflow on mobile.
 * @param {HTMLElement} zone
 */
function wrapTables(zone) {
  zone.querySelectorAll('table').forEach(table => {
    if (table.parentElement.classList.contains('table-scroll')) return;
    const wrapper = document.createElement('div');
    wrapper.className = 'table-scroll';
    table.parentNode.insertBefore(wrapper, table);
    wrapper.appendChild(table);
  });
}

/**
 * Detect semantic blockquotes (Note / Tip / Warning) and add the right class.
 * Matches: > **Note:** / > **Tip:** / > **Warning:**
 * @param {HTMLElement} zone
 */
function processBlockquotes(zone) {
  const types = {
    'note': 'bq-note',
    'tip': 'bq-tip',
    'info': 'bq-note',
    'warning': 'bq-warning',
    'caution': 'bq-warning',
    'important': 'bq-warning',
  };

  zone.querySelectorAll('blockquote').forEach(bq => {
    const firstPara = bq.querySelector('p');
    if (!firstPara) return;
    const firstStrong = firstPara.querySelector('strong:first-child');
    if (!firstStrong) return;

    const label = firstStrong.textContent.replace(/:$/, '').trim().toLowerCase();
    const cls = types[label];
    if (!cls) return;

    bq.classList.add(cls);

    // Replace <strong> with a styled badge span
    const badge = document.createElement('span');
    badge.className = 'bq-label';
    badge.textContent = firstStrong.textContent;
    firstPara.insertBefore(badge, firstPara.firstChild);
    firstStrong.remove();
  });
}

/**
 * Estimate reading time from rendered HTML.
 * @param {string} html
 * @returns {string} e.g. "4 min read"
 */
function estimateReadingTime(html) {
  const text = html.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim();
  const words = text.split(' ').filter(Boolean).length;
  const mins = Math.max(1, Math.round(words / 220));
  return mins + ' min read';
}

/**
 * Add anchor-copy buttons to h2 elements for shareable links.
 * @param {HTMLElement} zone
 */
function addAnchorButtons(zone) {
  zone.querySelectorAll('h2, h3').forEach((h, i) => {
    if (h.querySelector('.anchor-btn')) return; // already done
    if (!h.id) {
      h.id = 'section-' + i + '-' + h.textContent.toLowerCase().replace(/[^a-z0-9]+/g, '-').slice(0, 40);
    }
    const btn = document.createElement('button');
    btn.className = 'anchor-btn';
    btn.textContent = '#';
    btn.title = 'Copy section link';
    btn.addEventListener('click', () => {
      const url = window.location.href.split('#')[0] + '#' + h.id;
      navigator.clipboard.writeText(url).then(() => {
        btn.textContent = '✓';
        setTimeout(() => { btn.textContent = '#'; }, 1500);
      });
    });
    h.appendChild(btn);
  });
}

/* ─────────────────────────────────────────────────────────────
   6. TABLE OF CONTENTS (floating, IntersectionObserver)
   ───────────────────────────────────────────────────────────── */

/**
 * Build floating ToC from h2/h3 headings in the active page.
 * Uses IntersectionObserver to highlight the active heading.
 * @param {HTMLElement} pageEl
 */
function rebuildToc(pageEl) {
  // Disconnect previous observer
  if (tocObserver) {
    tocObserver.disconnect();
    tocObserver = null;
  }

  tocList.innerHTML = '';

  // Collect h2 and h3 headings
  const headings = pageEl.querySelectorAll('h2, h3');

  if (headings.length < 2) {
    // Not enough headings — hide ToC panel
    tocPanel.classList.remove('is-visible');
    return;
  }

  tocPanel.classList.add('is-visible');

  // Build anchor links
  const links = [];
  headings.forEach((h, i) => {
    // Assign id if missing
    if (!h.id) {
      h.id = 'h-' + i + '-' + h.textContent.toLowerCase().replace(/[^a-z0-9]+/g, '-').slice(0, 40);
    }

    const a = document.createElement('a');
    a.href = '#' + h.id;
    a.className = 'toc-link' + (h.tagName === 'H3' ? ' toc-h3' : '');
    a.textContent = h.textContent.replace(/#$/, '').trim(); // strip trailing anchor char
    a.dataset.target = h.id;

    a.addEventListener('click', e => {
      e.preventDefault();
      const target = document.getElementById(h.id);
      if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });

    tocList.appendChild(a);
    links.push(a);
  });

  // IntersectionObserver — highlight active section
  tocObserver = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        links.forEach(a => a.classList.remove('is-active'));
        const active = links.find(a => a.dataset.target === entry.target.id);
        if (active) active.classList.add('is-active');
      }
    });
  }, {
    root: main,
    rootMargin: '-20% 0px -70% 0px',
    threshold: 0,
  });

  headings.forEach(h => tocObserver.observe(h));
}

/* ─────────────────────────────────────────────────────────────
   7. READING PROGRESS BAR
   ───────────────────────────────────────────────────────────── */

/** Update the global progress bar based on main scroll position */
function updateProgress() {
  const el = main;
  const scrollTop = el.scrollTop;
  const scrollHeight = el.scrollHeight - el.clientHeight;
  const pct = scrollHeight > 0 ? (scrollTop / scrollHeight) * 100 : 0;
  progressBar.style.width = pct + '%';
}

/** Update reader progress bar */
function updateReaderProgress() {
  const scrollTop = readerBody.scrollTop;
  const scrollHeight = readerBody.scrollHeight - readerBody.clientHeight;
  const pct = scrollHeight > 0 ? (scrollTop / scrollHeight) * 100 : 0;
  readerProgress.style.width = pct + '%';
}

main.addEventListener('scroll', updateProgress, { passive: true });
readerBody.addEventListener('scroll', updateReaderProgress, { passive: true });

/* ─────────────────────────────────────────────────────────────
   8. RAW FILE OVERLAY
   ───────────────────────────────────────────────────────────── */

/**
 * Open the raw overlay and display the given .md file as plain text.
 * @param {string} filePath - path to the .md file (e.g. "docs/my-file.md")
 */
async function openRaw(filePath) {
  rawFilename.textContent = filePath.split('/').pop();
  rawContent.textContent  = 'Chargement…';

  rawOverlay.setAttribute('aria-hidden', 'false');
  rawOverlay.classList.add('is-open');
  rawBody.scrollTop = 0;
  rawOpen = true;
  rawClose.focus();
  document.body.style.overflow = 'hidden';

  try {
    const res = await fetch(filePath, { cache: 'no-store' });
    if (res.ok) {
      rawContent.textContent = await res.text();
    } else {
      rawContent.textContent = `Erreur ${res.status} — impossible de charger le fichier.`;
    }
  } catch (_) {
    rawContent.textContent = 'Impossible de charger le fichier (erreur réseau).';
  }
}

/** Close raw overlay */
function closeRaw() {
  rawOverlay.setAttribute('aria-hidden', 'true');
  rawOverlay.classList.remove('is-open');
  rawOpen = false;
  document.body.style.overflow = '';
}

rawClose.addEventListener('click', closeRaw);

/* ─────────────────────────────────────────────────────────────
   8b. READING MODE (immersive overlay)
   ───────────────────────────────────────────────────────────── */

/**
 * Open the immersive reader for the given page id.
 * Copies the rendered Markdown (or bento content) into the overlay.
 * @param {string} pageId
 */
async function openReader(pageId) {
  const pageEl = document.getElementById('page-' + pageId);
  if (!pageEl) return;

  // Load MD first if not yet done
  if (pageEl.classList.contains('md-page')) {
    await loadMarkdown(pageEl);
  }

  // Get content — prefer .md-render, fall back to full page text
  const mdZone = pageEl.querySelector('.md-render');
  const heroTitle = pageEl.querySelector('.hero-h1');

  // Build reader breadcrumb
  const bcTrail = pageEl.querySelector('.bc-trail');
  readerBreadcrumb.textContent = bcTrail ? bcTrail.textContent.trim() : pageEl.dataset.title || '';

  // Inject content
  if (mdZone && mdZone.dataset.loaded === 'true') {
    readerContent.innerHTML = mdZone.innerHTML;
  } else if (mdZone && mdZone.querySelector('.md-placeholder')) {
    // Placeholder — show message
    readerContent.innerHTML = `<p style="color:var(--ink-faint);font-style:italic;text-align:center;padding:60px 0">No content loaded yet for this document.</p>`;
  } else {
    // For the architecture bento page — build prose from headings/text
    readerContent.innerHTML = buildProseFromBento(pageEl);
  }

  // Post-process reader content
  processBlockquotes(readerContent);
  wrapTables(readerContent);
  enhanceCodeBlocks(readerContent);

  // Reading time
  if (readerTimeEl) {
    readerTimeEl.textContent = estimateReadingTime(readerContent.innerHTML);
  }

  // Show overlay
  readerOverlay.setAttribute('aria-hidden', 'false');
  readerOverlay.classList.add('is-open');
  readerBody.scrollTop = 0;
  readerProgress.style.width = '0%';
  readerOpen = true;

  // Trap focus
  readerClose.focus();
  document.body.style.overflow = 'hidden';
}

/** Close reader overlay */
function closeReader() {
  readerOverlay.setAttribute('aria-hidden', 'true');
  readerOverlay.classList.remove('is-open');
  readerOpen = false;
  document.body.style.overflow = '';
}

/**
 * Build simplified prose HTML from a bento page
 * (for pages without a .md-render zone, like architecture).
 * @param {HTMLElement} pageEl
 * @returns {string} HTML
 */
function buildProseFromBento(pageEl) {
  const title = pageEl.querySelector('.hero-h1');
  const lead = pageEl.querySelector('.hero-lead');
  let html = '';

  if (title) html += `<h1>${title.innerHTML}</h1>`;
  if (lead)  html += `<p class="reader-lead">${lead.textContent}</p>`;

  // Extract card content
  pageEl.querySelectorAll('.bento-card').forEach(card => {
    if (card.classList.contains('card-hero')) return; // already handled

    const label = card.querySelector('.card-label');
    const cardTitle = card.querySelector('.card-title, h3, h4');
    const paras = card.querySelectorAll('p:not(.card-label):not(.card-title)');

    if (label) html += `<h3>${label.textContent}</h3>`;
    if (cardTitle) html += `<h4>${cardTitle.textContent}</h4>`;
    paras.forEach(p => { html += `<p>${p.textContent}</p>`; });

    // Checklists
    const listItems = card.querySelectorAll('li');
    if (listItems.length) {
      html += '<ul>';
      listItems.forEach(li => { html += `<li>${li.textContent}</li>`; });
      html += '</ul>';
    }
  });

  return html || '<p>No content available.</p>';
}

readerClose.addEventListener('click', closeReader);
readerFontSm.addEventListener('click', () => setFontSize('sm'));
readerFontLg.addEventListener('click', () => setFontSize('lg'));

if (readerFontSerif) {
  readerFontSerif.addEventListener('click', () => {
    const isSerif = readerOverlay.classList.toggle('is-serif');
    readerFontSerif.classList.toggle('is-active', isSerif);
  });
}

/* ─────────────────────────────────────────────────────────────
   9. COMMAND PALETTE (⌘K)
   ───────────────────────────────────────────────────────────── */

/** Open the command palette */
function openCmd() {
  cmdOverlay.setAttribute('aria-hidden', 'false');
  cmdOverlay.classList.add('is-open');
  cmdInput.value = '';
  cmdOpen = true;
  cmdSelectedIdx = -1;
  renderCmdResults('');
  requestAnimationFrame(() => cmdInput.focus());
  document.body.style.overflow = 'hidden';
}

/** Close the command palette */
function closeCmd() {
  cmdOverlay.setAttribute('aria-hidden', 'true');
  cmdOverlay.classList.remove('is-open');
  cmdOpen = false;
  document.body.style.overflow = '';
}

/**
 * Render search results in the palette.
 * @param {string} query
 */
function renderCmdResults(query) {
  const q = query.toLowerCase().trim();

  // Filter + score results
  let results = SEARCH_INDEX.filter(item => {
    if (!q) return true;
    return (
      item.title.toLowerCase().includes(q) ||
      item.path.toLowerCase().includes(q) ||
      item.keywords.toLowerCase().includes(q)
    );
  });

  // Cap at 10
  results = results.slice(0, 10);
  cmdSelectedIdx = results.length > 0 ? 0 : -1;

  cmdResults.innerHTML = '';

  if (results.length === 0) {
    cmdResults.innerHTML = `<li class="cmd-no-results">No results for "<strong>${escHtml(query)}</strong>"</li>`;
    return;
  }

  results.forEach((item, i) => {
    const li = document.createElement('li');
    li.className = 'cmd-item' + (i === 0 ? ' is-selected' : '');
    li.setAttribute('role', 'option');
    li.dataset.page = item.page;

    // Highlight matched query in title
    const titleHl = q ? highlightMatch(item.title, q) : escHtml(item.title);
    const pathHl  = q ? highlightMatch(item.path, q)  : escHtml(item.path);

    li.innerHTML = `
      <div class="cmd-item-icon">
        <svg width="12" height="12" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.3">
          <path d="M3 2h7l3 3v9H3V2z"/><path d="M10 2v3h3"/>
        </svg>
      </div>
      <div class="cmd-item-text">
        <div class="cmd-item-title">${titleHl}</div>
        <div class="cmd-item-sub">${pathHl}</div>
      </div>`;

    li.addEventListener('mouseenter', () => {
      document.querySelectorAll('.cmd-item').forEach((el, j) => {
        el.classList.toggle('is-selected', j === i);
      });
      cmdSelectedIdx = i;
    });

    li.addEventListener('click', () => {
      navigateTo(item.page);
      closeCmd();
    });

    cmdResults.appendChild(li);
  });
}

/** Highlight query match within text (returns safe HTML) */
function highlightMatch(text, query) {
  const idx = text.toLowerCase().indexOf(query.toLowerCase());
  if (idx === -1) return escHtml(text);
  return escHtml(text.slice(0, idx))
    + '<mark>' + escHtml(text.slice(idx, idx + query.length)) + '</mark>'
    + escHtml(text.slice(idx + query.length));
}

/** Escape HTML special chars */
function escHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

cmdInput.addEventListener('input', e => renderCmdResults(e.target.value));

// Keyboard navigation in palette
cmdInput.addEventListener('keydown', e => {
  const items = cmdResults.querySelectorAll('.cmd-item');
  if (!items.length) return;

  if (e.key === 'ArrowDown') {
    e.preventDefault();
    cmdSelectedIdx = (cmdSelectedIdx + 1) % items.length;
  } else if (e.key === 'ArrowUp') {
    e.preventDefault();
    cmdSelectedIdx = (cmdSelectedIdx - 1 + items.length) % items.length;
  } else if (e.key === 'Enter') {
    e.preventDefault();
    const selected = items[cmdSelectedIdx];
    if (selected) {
      navigateTo(selected.dataset.page);
      closeCmd();
    }
    return;
  }

  items.forEach((el, i) => el.classList.toggle('is-selected', i === cmdSelectedIdx));
  items[cmdSelectedIdx]?.scrollIntoView({ block: 'nearest' });
});

// Close on overlay backdrop click
cmdOverlay.addEventListener('click', e => {
  if (e.target === cmdOverlay) closeCmd();
});

searchTrigger.addEventListener('click', openCmd);


/* ─────────────────────────────────────────────────────────────
   11. FONT SIZE (sm / md / lg)
   ───────────────────────────────────────────────────────────── */
const FONT_SIZES = ['sm', 'md', 'lg'];

function setFontSize(size) {
  if (!FONT_SIZES.includes(size)) return;
  html.setAttribute('data-font-size', size);
  localStorage.setItem('memora-font-size', size);
}

function stepFontSize(dir) {
  const current = html.getAttribute('data-font-size') || 'md';
  const idx = FONT_SIZES.indexOf(current);
  const next = FONT_SIZES[Math.max(0, Math.min(FONT_SIZES.length - 1, idx + dir))];
  setFontSize(next);
}

fontDec.addEventListener('click',   () => stepFontSize(-1));
fontReset.addEventListener('click', () => setFontSize('md'));
fontInc.addEventListener('click',   () => stepFontSize(+1));

/* ─────────────────────────────────────────────────────────────
   12. MOBILE HAMBURGER
   ───────────────────────────────────────────────────────────── */
function closeMobileSidebar() {
  sidebar.classList.remove('is-open');
  hamburger.setAttribute('aria-expanded', 'false');
  if (sidebarBackdrop) sidebarBackdrop.classList.remove('is-active');
}

hamburger.addEventListener('click', () => {
  const isOpen = sidebar.classList.toggle('is-open');
  hamburger.setAttribute('aria-expanded', String(isOpen));
  if (sidebarBackdrop) sidebarBackdrop.classList.toggle('is-active', isOpen);
});

if (sidebarBackdrop) {
  sidebarBackdrop.addEventListener('click', closeMobileSidebar);
}

main.addEventListener('click', () => {
  if (window.innerWidth <= 768) closeMobileSidebar();
});

/* ─────────────────────────────────────────────────────────────
   13. GLOBAL KEYBOARD SHORTCUTS
   ───────────────────────────────────────────────────────────── */
document.addEventListener('keydown', e => {
  // ⌘K or Ctrl+K → open palette
  if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
    e.preventDefault();
    cmdOpen ? closeCmd() : openCmd();
    return;
  }

  // Escape → close palette or reader
  if (e.key === 'Escape') {
    if (cmdOpen)    { closeCmd();    return; }
    if (rawOpen)    { closeRaw();    return; }
    if (readerOpen) { closeReader(); return; }
  }

  // "/" → open palette (when not typing in an input)
  if (e.key === '/' && document.activeElement.tagName !== 'INPUT') {
    e.preventDefault();
    openCmd();
  }

  // j / k → scroll in reader (vim-style)
  if (readerOpen && !cmdOpen && document.activeElement.tagName !== 'INPUT') {
    if (e.key === 'j') readerBody.scrollBy({ top: 100,  behavior: 'smooth' });
    if (e.key === 'k') readerBody.scrollBy({ top: -100, behavior: 'smooth' });
  }
});

/* ─────────────────────────────────────────────────────────────
   14. "READING MODE" BUTTON HANDLER
   Delegated on document — handles all .btn-immersive clicks
   ───────────────────────────────────────────────────────────── */
document.addEventListener('click', e => {
  const btn = e.target.closest('.btn-immersive');
  if (btn && btn.dataset.page) {
    openReader(btn.dataset.page);
  }
});

/* ─────────────────────────────────────────────────────────────
   14b. "RAW FILE" BUTTON HANDLER
   Delegated on document — handles all .btn-raw clicks
   ───────────────────────────────────────────────────────────── */
document.addEventListener('click', e => {
  const btn = e.target.closest('.btn-raw');
  if (btn && btn.dataset.src) {
    openRaw(btn.dataset.src);
  }
});

/* ─────────────────────────────────────────────────────────────
   15. TREE FOLDER CLICKS
   ───────────────────────────────────────────────────────────── */
document.querySelectorAll('.tree-folder').forEach(btn => {
  btn.addEventListener('click', () => toggleFolder(btn.dataset.folder));
});

/* ─────────────────────────────────────────────────────────────
   16. TREE FILE CLICKS
   ───────────────────────────────────────────────────────────── */
document.querySelectorAll('.tree-file[data-page]').forEach(btn => {
  btn.addEventListener('click', () => navigateTo(btn.dataset.page));
});

/* ─────────────────────────────────────────────────────────────
   17. HISTORY (back/forward support)
   ───────────────────────────────────────────────────────────── */
window.addEventListener('popstate', e => {
  if (e.state && e.state.page) {
    navigateTo(e.state.page, false);
  }
});

/* ─────────────────────────────────────────────────────────────
   18. SKELETON & PLACEHOLDER CSS (injected dynamically)
   ───────────────────────────────────────────────────────────── */
(function injectDynamicStyles() {
  const style = document.createElement('style');
  style.textContent = `
    /* Skeleton loader */
    .skeleton-wrap { padding: 8px 0; }
    .sk-line {
      height: 13px;
      background: linear-gradient(90deg, var(--border) 25%, var(--border2) 50%, var(--border) 75%);
      background-size: 200% 100%;
      border-radius: 4px;
      animation: sk-shimmer 1.6s ease-in-out infinite;
    }
    .sk-w-40  { width: 40%; }
    .sk-w-60  { width: 60%; }
    .sk-w-70  { width: 70%; }
    .sk-w-80  { width: 80%; }
    .sk-w-90  { width: 90%; }
    .sk-w-100 { width: 100%; }

    @keyframes sk-shimmer {
      0%   { background-position: 200% 0; }
      100% { background-position: -200% 0; }
    }

    /* Placeholder */
    .md-placeholder {
      text-align: center;
      padding: 48px 24px;
    }
    .placeholder-icon { margin-bottom: 14px; color: var(--ink-faint); }
    .placeholder-title {
      font-family: 'Nunito', sans-serif;
      font-size: 17px;
      font-weight: 600;
      color: var(--ink-light);
      margin-bottom: 8px;
    }
    .placeholder-desc {
      font-size: 12.5px;
      color: var(--ink-faint);
      line-height: 1.65;
      max-width: 380px;
      margin: 0 auto;
    }
    .placeholder-desc code {
      font-family: 'Fira Code', monospace;
      font-size: 11px;
      background: var(--bg2);
      border: 1px solid var(--border2);
      border-radius: 3px;
      padding: 0 5px;
      color: var(--ink);
    }

    /* Command palette: no results */
    .cmd-no-results {
      padding: 20px 16px;
      font-size: 13px;
      color: var(--ink-faint);
      text-align: center;
    }

    /* Reader lead paragraph */
    .reader-lead {
      font-size: 17px;
      color: var(--ink-light);
      line-height: 1.7;
      margin-bottom: 32px;
      padding-bottom: 24px;
      border-bottom: 1px solid var(--border);
    }
  `;
  document.head.appendChild(style);
})();

/* ─────────────────────────────────────────────────────────────
   19. INIT — run once DOM ready
   ───────────────────────────────────────────────────────────── */
function init() {
  // ── Configure Prism autoloader ──────────────────────────────
  if (typeof Prism !== 'undefined' && Prism.plugins && Prism.plugins.autoloader) {
    Prism.plugins.autoloader.languages_path =
      'https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/';
  }

  // ── Restore persisted preferences ──────────────────────────

  const savedFont = localStorage.getItem('memora-font-size');
  if (savedFont) setFontSize(savedFont);

  // ── Build search index from tree file buttons ───────────────
  document.querySelectorAll('.tree-file[data-page]').forEach(btn => {
    const pageEl = document.getElementById('page-' + btn.dataset.page);
    const heroTitle = pageEl && pageEl.querySelector('.hero-h1');

    SEARCH_INDEX.push({
      page:     btn.dataset.page,
      title:    btn.querySelector('span, code') ? btn.textContent.trim() : btn.textContent.trim(),
      path:     btn.dataset.path || '',
      keywords: btn.dataset.search || '',
      label:    heroTitle ? heroTitle.textContent.replace(/\s+/g, ' ').trim() : '',
    });
  });

  // ── Navigate to hash on load ────────────────────────────────
  const hash = window.location.hash.slice(1);
  if (hash && document.getElementById('page-' + hash)) {
    navigateTo(hash, false);
  } else {
    // Default page
    navigateTo('architecture', false);
    history.replaceState({ page: 'architecture' }, '', '#architecture');
  }
}

// Run init when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}