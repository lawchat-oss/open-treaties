"""Generate static HTML site for GitHub Pages.

Produces:
  docs/index.html          — landing page with treaty categories
  docs/treaties/{key}.html — one page per treaty with article TOC
"""

import json
import os
from pathlib import Path

DATA = Path("data")
DOCS = Path("docs")
TREATIES_DIR = DOCS / "treaties"

# ── Category ordering (based on intl law textbook structure) ──
CATEGORIES = [
    {
        "id": "un-system",
        "name_zh": "基礎體制",
        "name_en": "UN System",
        "keys": ["un-charter", "icj-statute"],
    },
    {
        "id": "treaty-law",
        "name_zh": "條約法",
        "name_en": "Treaty Law",
        "keys": ["vclt"],
    },
    {
        "id": "human-rights",
        "name_zh": "人權法",
        "name_en": "Human Rights",
        "keys": [
            "udhr", "iccpr", "icescr",
            "iccpr-op1", "iccpr-op2", "op-icescr",
            "cedaw", "crc", "crpd", "cat", "icerd",
        ],
    },
    {
        "id": "law-of-the-sea",
        "name_zh": "海洋法",
        "name_en": "Law of the Sea",
        "keys": ["unclos"],
    },
    {
        "id": "diplomatic",
        "name_zh": "外交領事法",
        "name_en": "Diplomatic & Consular",
        "keys": ["vcdr", "vccr"],
    },
    {
        "id": "ihl",
        "name_zh": "國際人道法",
        "name_en": "IHL",
        "keys": ["gc-i", "gc-ii", "gc-iii", "gc-iv", "gc-ap1", "gc-ap2"],
    },
    {
        "id": "criminal",
        "name_zh": "國際刑法",
        "name_en": "International Criminal Law",
        "keys": ["rome-statute", "genocide"],
    },
    {
        "id": "refugee",
        "name_zh": "難民法",
        "name_en": "Refugee Law",
        "keys": ["refugee"],
    },
    {
        "id": "anti-corruption",
        "name_zh": "反貪腐",
        "name_en": "Anti-Corruption",
        "keys": ["uncac"],
    },
    {
        "id": "space",
        "name_zh": "太空法",
        "name_en": "Space Law",
        "keys": ["outer-space"],
    },
]

# ── Load data ──
treaties = {}
for f in DATA.glob("*.json"):
    with open(f, encoding="utf-8") as fh:
        treaties[f.stem] = json.load(fh)


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


# ── Shared HTML pieces ──

FONTS = '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=EB+Garamond:wght@400;500;600;700&family=Lato:wght@300;400;700&display=swap" rel="stylesheet">'

TAILWIND = '<script src="https://cdn.tailwindcss.com"></script>'

TW_CONFIG = """<script>
tailwind.config={theme:{extend:{colors:{primary:'#1E40AF','primary-light':'#3B82F6',accent:'#F59E0B',surface:'#F8FAFC','text-heading':'#1E3A8A','text-body':'#334155','text-muted':'#64748B',sidebar:'#F1F5F9','sidebar-hover':'#E2E8F0','sidebar-active':'#DBEAFE'},fontFamily:{heading:['"EB Garamond"','Georgia','serif'],body:['Lato','system-ui','sans-serif']}}}}
</script>"""

STYLE = """<style>
html{scroll-behavior:smooth}
.sidebar-scroll::-webkit-scrollbar{width:4px}
.sidebar-scroll::-webkit-scrollbar-thumb{background:#CBD5E1;border-radius:2px}
.art-target:target{background:#DBEAFE;border-left:3px solid #1E40AF;margin-left:-3px}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
</style>"""

FOOTER = """<footer class="mt-12 py-6 border-t border-gray-200 text-center text-xs text-text-muted">
Data: <a href="https://creativecommons.org/publicdomain/zero/1.0/" class="text-primary hover:underline" target="_blank" rel="noopener">CC0 1.0</a> · Code: <a href="https://opensource.org/licenses/MIT" class="text-primary hover:underline" target="_blank" rel="noopener">MIT</a> · <a href="https://github.com/lawchat-oss/open-treaties" class="text-primary hover:underline" target="_blank" rel="noopener">GitHub</a><br>
Maintained by <a href="https://lawchat.com.tw" class="text-primary hover:underline" target="_blank" rel="noopener">lawchat.com.tw</a>
</footer>"""


# ── Generate index.html ──

def gen_index():
    cats_html = ""
    total_treaties = 0
    total_articles = 0

    for cat in CATEGORIES:
        cats_html += f'<div class="mb-6">\n'
        cats_html += f'<h2 class="font-heading text-lg font-bold text-text-heading mb-3">{esc(cat["name_zh"])} <span class="text-sm font-normal text-text-muted">{esc(cat["name_en"])}</span></h2>\n'
        cats_html += '<div class="grid grid-cols-1 sm:grid-cols-2 gap-3">\n'

        for key in cat["keys"]:
            t = treaties.get(key)
            if not t:
                continue
            total_treaties += 1
            total_articles += t["total_articles"]
            cats_html += f'''<a href="treaties/{key}.html" class="group block p-4 bg-white rounded-xl border border-gray-200 hover:border-primary-light hover:shadow-md cursor-pointer transition-all duration-200">
  <div class="font-heading text-base font-semibold text-text-heading group-hover:text-primary transition-colors duration-200">{esc(t["treaty_zh"])}</div>
  <div class="text-xs text-text-muted mt-0.5">{esc(t["treaty_en"])}</div>
  <div class="text-xs text-text-muted mt-2">{t["total_articles"]} 條 Articles</div>
</a>\n'''
        cats_html += '</div>\n</div>\n'

    html = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Open Treaties — 國際公約中英雙語資料集</title>
<meta name="description" content="28 部國際公約、1,914 條條文的結構化中英雙語查詢。免費開源。">
{FONTS}
{TAILWIND}
{TW_CONFIG}
{STYLE}
</head>
<body class="bg-surface text-text-body font-body antialiased">
<div class="max-w-4xl mx-auto px-4 sm:px-8 py-8 sm:py-12">

<header class="mb-10">
  <h1 class="font-heading text-3xl sm:text-4xl font-bold text-text-heading mb-2">Open Treaties</h1>
  <p class="text-text-muted text-lg mb-6">國際公約中英雙語結構化資料集 · Bilingual International Treaty Corpus</p>
  <div class="flex gap-6 mb-6">
    <div><span class="text-2xl font-bold text-primary font-heading">{total_treaties}</span> <span class="text-sm text-text-muted">公約</span></div>
    <div><span class="text-2xl font-bold text-primary font-heading">{total_articles:,}</span> <span class="text-sm text-text-muted">條文</span></div>
    <div><span class="text-2xl font-bold text-primary font-heading">ZH/EN</span> <span class="text-sm text-text-muted">雙語</span></div>
  </div>
  <div class="flex flex-wrap gap-3">
    <a href="https://github.com/lawchat-oss/open-treaties" target="_blank" rel="noopener" class="inline-flex items-center gap-2 px-4 py-2 bg-white border border-gray-200 rounded-lg text-sm text-text-heading hover:border-primary-light hover:shadow-sm cursor-pointer transition-all duration-200">
      <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/></svg>
      GitHub
    </a>
    <span class="inline-flex items-center px-4 py-2 bg-white border border-gray-200 rounded-lg text-sm text-text-muted">CC0 1.0 + MIT</span>
  </div>
</header>

{cats_html}

{FOOTER}
</div>
</body>
</html>"""

    (DOCS / "index.html").write_text(html, encoding="utf-8")
    print(f"  index.html ({total_treaties} treaties, {total_articles} articles)")


# ── Generate treaty pages ──

def gen_treaty_page(key):
    t = treaties[key]
    cat = next((c for c in CATEGORIES if key in c["keys"]), None)
    cat_name = f'{cat["name_zh"]} {cat["name_en"]}' if cat else ""

    # Article TOC
    toc_items = ""
    for a in t["articles"]:
        title_zh = a.get("title_zh", "")
        toc_label = f'第{esc(a["article"])}條'
        toc_suffix = f' {esc(title_zh)}' if title_zh else ""
        toc_items += f'<a href="#art-{esc(a["article"])}" class="block px-2 py-0.5 text-xs text-text-muted hover:text-primary hover:bg-sidebar-hover rounded cursor-pointer transition-colors duration-150 truncate" title="{toc_label}{toc_suffix}">{toc_label}{toc_suffix}</a>\n'

    # Preamble
    preamble_html = ""
    if t.get("preamble_zh") or t.get("preamble_en"):
        preamble_html = f'''<details class="mb-6 bg-white rounded-xl border border-gray-200 overflow-hidden" id="preamble">
  <summary class="px-5 py-3 text-sm font-medium text-text-heading cursor-pointer hover:bg-gray-50 transition-colors duration-150">序言 Preamble</summary>
  <div class="px-5 py-4 border-t border-gray-100 space-y-4">
    <div class="zh-content text-sm whitespace-pre-wrap leading-relaxed">{esc(t.get("preamble_zh", ""))}</div>
    <div class="en-content text-sm whitespace-pre-wrap leading-relaxed text-text-muted hidden">{esc(t.get("preamble_en", ""))}</div>
  </div>
</details>'''

    # Articles
    articles_html = ""
    for i, a in enumerate(t["articles"]):
        art_id = f'art-{a["article"]}'
        title_zh = a.get("title_zh", "")
        title_en = a.get("title_en", "")
        title_html = ""
        if title_zh or title_en:
            title_html = f'<div class="text-sm font-medium text-text-heading zh-content">{esc(title_zh)}</div>' if title_zh else ""
            title_html += f'<div class="text-sm font-medium text-text-muted en-content hidden">{esc(title_en)}</div>' if title_en else ""
        articles_html += f'''<div id="{art_id}" class="art-target py-4 border-b border-gray-100 scroll-mt-16">
  <div class="flex items-baseline gap-2 mb-1">
    <a href="#{art_id}" class="font-heading text-base font-bold text-primary hover:underline cursor-pointer">第{esc(a["article"])}條</a>
    <span class="text-xs text-text-muted">Art. {esc(a["article"])}</span>
  </div>
  {title_html}
  <div class="zh-content text-sm whitespace-pre-wrap leading-relaxed mt-1">{esc(a.get("content_zh", ""))}</div>
  <div class="en-content text-sm whitespace-pre-wrap leading-relaxed text-text-muted mt-2 hidden">{esc(a.get("content_en", ""))}</div>
</div>\n'''

    html = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(t["treaty_zh"])} — Open Treaties</title>
<meta name="description" content="{esc(t['treaty_zh'])}（{esc(t['treaty_en'])}）全文 {t['total_articles']} 條，中英雙語對照。">
{FONTS}
{TAILWIND}
{TW_CONFIG}
{STYLE}
</head>
<body class="bg-surface text-text-body font-body antialiased">

<!-- Top bar -->
<header class="sticky top-0 z-40 bg-white/95 backdrop-blur border-b border-gray-200">
  <div class="max-w-7xl mx-auto flex items-center h-12 px-4">
    <a href="../" class="font-heading text-sm font-bold text-text-heading hover:text-primary cursor-pointer transition-colors duration-200 mr-4">Open Treaties</a>
    <svg class="w-3 h-3 text-gray-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>
    <span class="text-xs text-text-muted mr-2">{esc(cat_name)}</span>
    <svg class="w-3 h-3 text-gray-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>
    <span class="text-xs text-text-heading font-medium truncate">{esc(t["treaty_zh"])}</span>
    <div class="ml-auto flex border border-gray-200 rounded-lg overflow-hidden">
      <button onclick="setLang('zh')" class="lang-btn px-3 py-1 text-xs bg-primary text-white cursor-pointer transition-colors duration-200" data-l="zh">中文</button>
      <button onclick="setLang('en')" class="lang-btn px-3 py-1 text-xs bg-white text-text-muted hover:bg-gray-50 cursor-pointer transition-colors duration-200" data-l="en">EN</button>
      <button onclick="setLang('both')" class="lang-btn px-3 py-1 text-xs bg-white text-text-muted hover:bg-gray-50 cursor-pointer transition-colors duration-200" data-l="both">雙語</button>
    </div>
  </div>
</header>

<div class="max-w-7xl mx-auto flex">
  <!-- TOC sidebar -->
  <aside class="hidden lg:block w-56 shrink-0 sticky top-12 h-[calc(100vh-3rem)] border-r border-gray-200 bg-white overflow-y-auto sidebar-scroll py-3 px-2">
    <div class="text-xs font-bold text-text-muted uppercase tracking-wider px-2 mb-2">條文目錄</div>
    {toc_items}
  </aside>

  <!-- Main content -->
  <main class="flex-1 min-w-0 px-4 sm:px-8 py-6 max-w-3xl">
    <h1 class="font-heading text-2xl sm:text-3xl font-bold text-text-heading mb-1">{esc(t["treaty_zh"])}</h1>
    <p class="text-sm text-text-muted mb-1">{esc(t["treaty_en"])}</p>
    <p class="text-xs text-text-muted mb-6">{t["total_articles"]} 條條文 Articles</p>

    {preamble_html}

    <div>
      {articles_html}
    </div>

    {FOOTER}
  </main>
</div>

<script>
function setLang(l){{
  document.querySelectorAll('.lang-btn').forEach(b=>{{
    const a=b.dataset.l===l;
    b.classList.toggle('bg-primary',a);b.classList.toggle('text-white',a);
    b.classList.toggle('bg-white',!a);b.classList.toggle('text-text-muted',!a);
  }});
  document.querySelectorAll('.zh-content').forEach(e=>e.classList.toggle('hidden',l==='en'));
  document.querySelectorAll('.en-content').forEach(e=>{{
    e.classList.toggle('hidden',l==='zh');
    if(l==='both')e.classList.add('mt-2');else e.classList.remove('mt-2');
  }});
}}
</script>
</body>
</html>"""

    (TREATIES_DIR / f"{key}.html").write_text(html, encoding="utf-8")
    print(f"  treaties/{key}.html ({t['total_articles']} articles)")


# ── Main ──

if __name__ == "__main__":
    TREATIES_DIR.mkdir(parents=True, exist_ok=True)

    # Remove old single-page files
    for old in [DOCS / "treaties.json"]:
        if old.exists():
            old.unlink()

    gen_index()
    for cat in CATEGORIES:
        for key in cat["keys"]:
            if key in treaties:
                gen_treaty_page(key)

    print(f"\nDone. {len(treaties)} treaty pages generated.")
