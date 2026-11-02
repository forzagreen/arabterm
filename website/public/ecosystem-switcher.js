// ecosystem-switcher.js — «أدوات الحوسبة»: the menu that links every site of
// the ecosystem to the others.
//
// One self-contained file, deliberately dependency-free (no framework, no
// build step, ES2015 syntax, shadow DOM so the host page's CSS does not leak
// in and ours does not leak out). The SAME file is copied verbatim into each
// site (wikitermbase, farahidi-js, mazini-js, ar-plurals, arabterm,
// ar-senses, gen-ar); when the list of tools changes, update it here and
// copy the file over. The canonical copy lives in the wikitermbase repo.
//
// Usage on a plain site:
//   <script defer src="ecosystem-switcher.js"></script>
//   <ecosystem-switcher current="mazini"></ecosystem-switcher>
// In wikitermbase it is imported once from main.jsx and used the same way.
//
// Attributes:
//   current  – the `id` of the tool the page belongs to (highlighted, not
//              repeated as a link).
//   active   – present when the page is the ecosystem page itself, so the
//              button reads as the current nav item.
//
// Colour scheme: `data-theme="dark|light"` on <html> wins (the GitHub Pages
// sites and arabterm set it before paint), then Bootstrap's `data-bs-theme`
// (ar-senses); otherwise a `dark` class on <html> (wikitermbase, Tailwind);
// otherwise light.
//
// A host whose header is not the page colour (ar-senses' blue navbar) sets
// the button's colours from its own stylesheet; the panel keeps its own:
//   ecosystem-switcher { --es-btn-text: #fff; --es-btn-hover: rgba(255,255,255,.15); }
(function () {
  if (typeof window === 'undefined' || !window.customElements) return;
  if (window.customElements.get('ecosystem-switcher')) return;

  var NAME = 'أدوات الحوسبة';
  var TAGLINE = 'منظومة مفتوحة المصدر لحوسبة اللغة العربية';
  var ABOUT_URL = 'https://wikitermbase.toolforge.org/tools';

  // Three levels, in the ecosystem page's order. `tag` is the one-line role
  // shown under the name; keep it to a few words so rows stay one line.
  var LEVELS = [
    {
      title: 'المستوى الصرفي',
      tools: [
        { id: 'farahidi', name: 'الفراهيدي', latin: 'farahidi', tag: 'محلّل صرفي', url: 'https://forzagreen.github.io/farahidi-js/' },
        { id: 'mazini', name: 'المازني', latin: 'mazini', tag: 'مصرّف الأفعال', url: 'https://forzagreen.github.io/mazini-js/' },
        { id: 'ar-conjugation', name: 'جداول تصريف الأفعال', latin: 'ar-conjugation', tag: 'بيانات التصريف', url: 'https://forzagreen.github.io/ar-conjugation/' },
        { id: 'arabic-morphology', name: 'جداول الأفعال العربية', latin: 'arabic-morphology', tag: 'إحصاءات الأفعال والجذور بالمعاجم العربية', url: 'https://m-bakni.github.io/arabic-morphology/' },
        { id: 'ar-plurals', name: 'جموع التكسير', latin: 'ar-plurals', tag: 'أوزان المفرد والجمع', url: 'https://forzagreen.github.io/ar-plurals/' },
      ],
    },
    {
      title: 'المستوى الدلالي',
      tools: [
        { id: 'ar-senses', name: 'مراجعة المعاني', latin: 'ar-senses', tag: 'معاني الأفعال إلى ويكي بيانات', url: 'https://ar-senses.toolforge.org/' },
      ],
    },
    {
      title: 'المستوى المعجمي',
      tools: [
        { id: 'wikitermbase', name: 'مسرد الويكي', latin: 'wikitermbase', tag: 'بحث في المعاجم المصطلحية', url: 'https://wikitermbase.toolforge.org/' },
        { id: 'gen-ar', name: 'توليد الكلمات العربية', latin: 'gen-ar', tag: 'اقتراح ألفاظ لمصطلح', url: 'https://genar.waeltellat.com/' },
        { id: 'arabterm', name: 'قاعدة معطيات المعاجم', latin: 'arabterm', tag: 'الملفات المصدرية للمداخل المعجمية', url: 'https://forzagreen.github.io/arabterm/' },
      ],
    },
  ];

  var GRID_ICON =
    '<svg viewBox="0 0 24 24" width="22" height="22" fill="currentColor" aria-hidden="true">' +
    '<circle cx="5" cy="5" r="2"/><circle cx="12" cy="5" r="2"/><circle cx="19" cy="5" r="2"/>' +
    '<circle cx="5" cy="12" r="2"/><circle cx="12" cy="12" r="2"/><circle cx="19" cy="12" r="2"/>' +
    '<circle cx="5" cy="19" r="2"/><circle cx="12" cy="19" r="2"/><circle cx="19" cy="19" r="2"/></svg>';

  // Small "opens elsewhere" arrow at the end of each row.
  var LINK_ICON =
    '<svg class="m" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' +
    '<path d="M7 17 17 7M8 7h9v9"/></svg>';

  var STYLE =
    ':host{position:relative;display:inline-block;font:inherit;direction:rtl;--es-btn-text:var(--es-text);--es-btn-hover:var(--es-hover);' +
    '--es-text:#1f2937;--es-muted:#6b7280;--es-bg:#fff;--es-border:#e5e7eb;--es-hover:#f3f4f6;' +
    '--es-accent:#1d4ed8;--es-accent-bg:#dbeafe;--es-band:#f9fafb;--es-shadow:0 10px 30px rgba(0,0,0,.15)}' +
    ':host([dark]){--es-text:#e5e7eb;--es-muted:#9ca3af;--es-bg:#1f2937;--es-border:#374151;--es-hover:#374151;' +
    '--es-accent:#bfdbfe;--es-accent-bg:rgba(30,58,138,.5);--es-band:#111827;--es-shadow:0 10px 30px rgba(0,0,0,.5)}' +
    '*{box-sizing:border-box}' +
    'button{display:inline-flex;align-items:center;gap:.375rem;border:0;border-radius:9999px;padding:.5rem .625rem;' +
    'background:transparent;color:var(--es-btn-text);font:inherit;font-size:.875rem;font-weight:500;cursor:pointer;line-height:1}' +
    'button:hover,button[aria-expanded="true"]{background:var(--es-btn-hover)}' +
    ':host([active]) button{background:var(--es-accent-bg);color:var(--es-accent)}' +
    'button:focus-visible{outline:2px solid var(--es-accent);outline-offset:2px}' +
    '@media (max-width:639px){.label{display:none}}' +
    '.panel{position:absolute;top:calc(100% + .5rem);z-index:1000;width:min(22rem,calc(100vw - 2rem));' +
    'background:var(--es-bg);color:var(--es-text);border:1px solid var(--es-border);border-radius:.75rem;' +
    'box-shadow:var(--es-shadow);padding:0 0 .25rem;text-align:start;overflow:hidden}' +
    '.panel[hidden]{display:none}.panel.left{left:0}.panel.right{right:0}.panel.fixed{position:fixed;left:1rem;right:1rem;width:auto}' +
    '.head{padding:.5rem 1rem;background:var(--es-band);border-bottom:1px solid var(--es-border);font-size:.75rem;color:var(--es-muted)}' +
    '.head b{font-weight:600;color:var(--es-text)}.head b::after{content:" · "}' +
    '.body{max-height:calc(100vh - 10rem);overflow-y:auto}' +
    'h3{margin:0;padding:.3rem 1rem;background:var(--es-band);border-top:1px solid var(--es-border);border-bottom:1px solid var(--es-border);' +
    'font-size:.6875rem;font-weight:600;color:var(--es-muted)}' +
    '.body h3:first-child{border-top:0}ul{padding:.25rem 0}' +
    'ul{list-style:none;margin:0}' +
    'a{position:relative;display:block;padding:.375rem 1rem;padding-inline-end:2.25rem;color:inherit;text-decoration:none;line-height:1.35}' +
    'a .m{position:absolute;inset-inline-end:.875rem;top:.6rem;width:14px;height:14px;color:var(--es-muted);opacity:.6}a:hover .m{opacity:1}' +
    'a:hover,a:focus-visible{background:var(--es-hover);outline:none}' +
    'a[aria-current]{background:var(--es-accent-bg);color:var(--es-accent)}' +
    'a .n{font-weight:600}a .t{display:block;font-size:.75rem;color:var(--es-muted)}' +
    'a[aria-current] .t{color:inherit;opacity:.8}' +
    'a .l{margin:0 .5rem;font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:.6875rem;color:var(--es-muted);direction:ltr;unicode-bidi:isolate}' +
    '.foot{border-top:1px solid var(--es-border);padding-top:.25rem}' +
    '.foot a{display:flex;justify-content:space-between;font-size:.8125rem;font-weight:600}';

  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
    });
  }

  function render(current) {
    var html = '<div class="head"><b>' + esc(NAME) + '</b><span>' + esc(TAGLINE) + '</span></div><div class="body">';
    LEVELS.forEach(function (level) {
      html += '<h3>' + esc(level.title) + '</h3><ul>';
      level.tools.forEach(function (t) {
        var isCurrent = t.id === current;
        html +=
          '<li><a href="' + esc(t.url) + '"' +
          (isCurrent ? ' aria-current="page"' : ' target="_blank" rel="noopener"') + '>' +
          (isCurrent ? '' : LINK_ICON) +
          '<span class="n">' + esc(t.name) + '</span>' +
          '<span class="l">' + esc(t.latin) + '</span>' +
          '<span class="t">' + esc(t.tag) + '</span></a></li>';
      });
      html += '</ul>';
    });
    html +=
      '</div><div class="foot"><a href="' + esc(ABOUT_URL) + '"' +
      (current === 'wikitermbase' ? '' : ' target="_blank" rel="noopener"') +
      '><span>عن المنظومة وكل الأدوات</span><span aria-hidden="true">←</span></a></div>';
    return html;
  }

  function isDark() {
    var html = document.documentElement;
    var t = html.getAttribute('data-theme') || html.getAttribute('data-bs-theme');
    if (t === 'dark') return true;
    if (t === 'light') return false;
    return html.classList.contains('dark');
  }

  class EcosystemSwitcher extends HTMLElement {}

  EcosystemSwitcher.prototype.connectedCallback = function () {
    var self = this;
    if (!this.shadowRoot) {
      var root = this.attachShadow({ mode: 'open' });
      root.innerHTML =
        '<style>' + STYLE + '</style>' +
        '<button type="button" aria-haspopup="true" aria-expanded="false" title="' + esc(NAME) + '">' +
        GRID_ICON + '<span class="label">' + esc(NAME) + '</span></button>' +
        '<div class="panel right" role="menu" hidden></div>';
      this._button = root.querySelector('button');
      this._panel = root.querySelector('.panel');
      this._button.addEventListener('click', function () {
        self.toggle();
      });
      this._onDocDown = function (e) {
        if (e.composedPath().indexOf(self) === -1) self.close();
      };
      this._onKey = function (e) {
        if (e.key === 'Escape' && self.isOpen()) {
          self.close();
          self._button.focus();
        }
      };
    }
    this._panel.innerHTML = render(this.getAttribute('current'));
    this._syncTheme();
    this._observer = new MutationObserver(function () {
      self._syncTheme();
    });
    this._observer.observe(document.documentElement, { attributes: true, attributeFilter: ['class', 'data-theme', 'data-bs-theme'] });
  };

  EcosystemSwitcher.prototype.disconnectedCallback = function () {
    this.close();
    if (this._observer) this._observer.disconnect();
  };

  EcosystemSwitcher.prototype._syncTheme = function () {
    if (isDark()) this.setAttribute('dark', '');
    else this.removeAttribute('dark');
  };

  EcosystemSwitcher.prototype.isOpen = function () {
    return !this._panel.hidden;
  };

  EcosystemSwitcher.prototype.open = function () {
    // Anchor the panel to whichever side of the button is nearer the
    // viewport edge, so it never overflows the screen.
    var r = this._button.getBoundingClientRect();
    var margin = 16;
    var width = Math.min(22 * 16, window.innerWidth - 2 * margin);
    var side;
    if (r.left + width <= window.innerWidth - margin) side = 'left';
    else if (r.right - width >= margin) side = 'right';
    else side = 'fixed';
    this._panel.className = 'panel ' + side;
    this._panel.style.top = side === 'fixed' ? r.bottom + 8 + 'px' : '';
    this._panel.hidden = false;
    this._button.setAttribute('aria-expanded', 'true');
    document.addEventListener('pointerdown', this._onDocDown);
    document.addEventListener('keydown', this._onKey);
  };

  EcosystemSwitcher.prototype.close = function () {
    if (!this._panel || this._panel.hidden) return;
    this._panel.hidden = true;
    this._button.setAttribute('aria-expanded', 'false');
    document.removeEventListener('pointerdown', this._onDocDown);
    document.removeEventListener('keydown', this._onKey);
  };

  EcosystemSwitcher.prototype.toggle = function () {
    if (this.isOpen()) this.close();
    else this.open();
  };

  window.customElements.define('ecosystem-switcher', EcosystemSwitcher);
})();
