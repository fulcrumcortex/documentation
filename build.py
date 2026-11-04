#!/usr/bin/env python3
"""Render the Fulcrum documentation site.

Sources live in _src/pages/ as HTML fragments with a small front-matter block.
Running this script writes plain static HTML (one folder per page, each with
an index.html), plus sitemap.xml and robots.txt, into the repository root.
GitHub Pages then serves those files as they are.

The public address comes from `site_url` in _config.yml. To move the site to
a custom domain, change that one line and run this script again.

Standard library only: python3 build.py
"""

from __future__ import annotations

import html
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "_src" / "pages"
MANIFEST = ROOT / "_src" / "generated.txt"


def read_site_url() -> str:
    text = (ROOT / "_config.yml").read_text(encoding="utf-8")
    match = re.search(r"^site_url:\s*(\S+)\s*$", text, re.M)
    if not match:
        sys.exit("_config.yml must define site_url")
    return match.group(1).rstrip("/")


SITE_URL = read_site_url()
BASE_PATH = re.sub(r"^https?://[^/]+", "", SITE_URL)  # "/documentation" or ""
SITE_NAME = "Fulcrum Docs"
REPO_URL = "https://github.com/fulcrumcortex/documentation"

ORGANIZATION = {
    "@type": "Organization",
    "@id": "https://fulcrumcortex.com/#organization",
    "name": "Fulcrum Cortex",
    "url": "https://fulcrumcortex.com/",
    "logo": f"{SITE_URL}/assets/fulcrum-logo.png",
    "description": "Fulcrum Cortex is the AI execution layer for business, built in Australia.",
    "sameAs": [
        "https://fulcrumcrm.app/",
        "https://fulcrumcode.app/",
        "https://fulcrumail.app/",
        "https://lyre.au/",
        "https://docs.lyre.au/",
        "https://github.com/fulcrumcortex",
    ],
}

# Sidebar order. Each section starts with its hub page. Prev/next links follow this order.
NAV: list[tuple[str, list[str]]] = [
    ("Start here", ["/", "/sessions/"]),
    ("Fulcrum Code", ["/code/", "/code/install-and-sign-in/", "/code/plan-build-and-review/", "/code/tools-and-worktrees/", "/code/skills-and-agents/", "/code/sessions-and-memory/", "/code/connections-and-extensions/", "/code/voice-images-and-editor/"]),
    ("Fulcrum Mail", [
        "/fulcrum-mail/",
        "/fulcrum-mail/create-an-account/",
        "/fulcrum-mail/workspaces/",
        "/fulcrum-mail/invite-and-manage-members/",
        "/fulcrum-mail/switch-workspaces-and-accounts/",
        "/fulcrum-mail/mail-basics/",
        "/fulcrum-mail/settings/",
    ]),
    ("Calendar", [
        "/calendar/",
        "/calendar/import-and-connect-calendars/",
        "/calendar/booking-pages/",
        "/calendar/manage-bookings/",
        "/calendar/meetings/",
    ]),
    ("Files and documents", ["/drive/", "/docs/", "/pages/", "/wallet/"]),
    ("Lyre", [
        "/lyre/",
        "/lyre/voice-agents/",
        "/lyre/phone-numbers/",
        "/lyre/outbound-calls-and-campaigns/",
        "/lyre/book-meetings/",
        "/lyre/call-history/",
        "/lyre/credits-and-billing/",
        "/lyre/compliance/",
        "/lyre/sms-contacts-and-connections/",
    ]),
    ("Fulcrum CRM", [
        "/crm/",
        "/crm/contacts-and-companies/",
        "/crm/deals-and-pipelines/",
        "/crm/activities-and-tasks/",
        "/crm/lists/",
        "/crm/custom-fields/",
        "/crm/import-export-and-duplicates/",
        "/crm/lead-forms-and-routing/",
        "/crm/email/",
        "/crm/calls-and-ai/",
        "/crm/roles-and-permissions/",
        "/crm/reports-and-workflows/",
        "/crm/invoices-and-products/",
        "/crm/projects-and-issues/",
        "/crm/settings-and-integrations/",
    ]),
]


@dataclass
class Page:
    path: str  # site path such as "/crm/lists/"
    meta: dict
    body: str
    related: list[tuple[str, str]] = field(default_factory=list)
    section: str = ""

    @property
    def url(self) -> str:
        return SITE_URL + self.path

    @property
    def href(self) -> str:
        return BASE_PATH + self.path


def parse_source(path: Path) -> tuple[dict, list[tuple[str, str]], str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        sys.exit(f"{path}: missing front matter")
    head, body = text[4:].split("\n---\n", 1)
    meta: dict = {}
    related: list[tuple[str, str]] = []
    current = None
    for line in head.splitlines():
        if not line.strip():
            continue
        if line.startswith("  - ") and current == "related":
            url, _, title = line[4:].partition(" | ")
            related.append((url.strip(), title.strip()))
            continue
        key, _, value = line.partition(":")
        current = key.strip()
        meta[current] = value.strip()
    for required in ("title", "description", "nav"):
        if not meta.get(required):
            sys.exit(f"{path}: front matter needs {required}")
    return meta, related, body.strip() + "\n"


def source_to_path(src: Path) -> str:
    rel = src.relative_to(SRC).with_suffix("")
    parts = list(rel.parts)
    if parts[-1] == "index":
        parts = parts[:-1]
    return "/" + "".join(p + "/" for p in parts)


def slugify(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text).lower()
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text or "section"


def add_heading_ids(body: str) -> tuple[str, list[tuple[str, str]]]:
    toc: list[tuple[str, str]] = []
    seen: set[str] = set()

    def repl(match: re.Match) -> str:
        level, attrs, inner = match.group(1), match.group(2), match.group(3)
        id_match = re.search(r'id="([^"]+)"', attrs)
        ident = id_match.group(1) if id_match else slugify(inner)
        base, n = ident, 2
        while ident in seen:
            ident, n = f"{base}-{n}", n + 1
        seen.add(ident)
        if level == "2":
            toc.append((ident, re.sub(r"<[^>]+>", "", inner)))
        if id_match:
            return match.group(0)
        return f'<h{level} id="{ident}"{attrs}>{inner}</h{level}>'

    body = re.sub(r"<h([23])([^>]*)>(.*?)</h\1>", repl, body, flags=re.S)
    return body, toc


def rewrite_internal_links(fragment: str) -> str:
    return re.sub(r'(href|src)="/(?!/)', lambda m: f'{m.group(1)}="{BASE_PATH}/', fragment)


def strip_tags(fragment: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", fragment))).strip()


def howto_steps(body: str) -> list[str]:
    match = re.search(r'<ol class="steps">(.*?)</ol>', body, re.S)
    if not match:
        return []
    items = re.findall(r"<li>(.*?)</li>", match.group(1), re.S)
    return [strip_tags(item) for item in items]


def esc(text: str) -> str:
    return html.escape(text, quote=True)


def json_ld(page: Page, crumbs: list[tuple[str, str]]) -> str:
    graph: list[dict] = [ORGANIZATION]
    graph.append({
        "@type": "WebSite",
        "@id": f"{SITE_URL}/#website",
        "name": SITE_NAME,
        "url": f"{SITE_URL}/",
        "inLanguage": "en-AU",
        "publisher": {"@id": ORGANIZATION["@id"]},
    })
    graph.append({
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": name, "item": url}
            for i, (name, url) in enumerate(crumbs)
        ],
    })
    article = {
        "@type": "TechArticle",
        "headline": page.meta["title"],
        "description": page.meta["description"],
        "url": page.url,
        "mainEntityOfPage": page.url,
        "inLanguage": "en-AU",
        "isPartOf": {"@id": f"{SITE_URL}/#website"},
        "author": {"@id": ORGANIZATION["@id"]},
        "publisher": {"@id": ORGANIZATION["@id"]},
        "image": f"{SITE_URL}/assets/og-image.png",
        "dateModified": page.meta.get("updated", ""),
    }
    if page.meta.get("about"):
        article["about"] = {"@type": "SoftwareApplication", "name": page.meta["about"],
                            "applicationCategory": "BusinessApplication"}
    graph.append(article)
    steps = howto_steps(page.body) if page.meta.get("howto") else []
    if steps:
        graph.append({
            "@type": "HowTo",
            "name": page.meta["howto"],
            "description": page.meta["description"],
            "url": page.url,
            "step": [{"@type": "HowToStep", "position": i + 1, "text": s} for i, s in enumerate(steps)],
        })
    data = {"@context": "https://schema.org", "@graph": graph}
    return json.dumps(data, ensure_ascii=False, indent=1).replace("</", "<\\/")


def render_nav(pages: dict[str, Page], current: Page) -> str:
    out = ['<nav class="sidebar" id="docs-nav" aria-label="Documentation">']
    for section, paths in NAV:
        out.append(f'<p class="nav-section">{esc(section)}</p><ul>')
        for p in paths:
            page = pages[p]
            attrs = ' aria-current="page"' if page is current else ""
            out.append(f'<li><a href="{page.href}"{attrs}>{esc(page.meta["nav"])}</a></li>')
        out.append("</ul>")
    out.append("</nav>")
    return "\n".join(out)


def render(page: Page, pages: dict[str, Page], order: list[str]) -> str:
    body, toc = add_heading_ids(page.body)
    body = rewrite_internal_links(body)

    crumbs = [("Docs", f"{SITE_URL}/")]
    section_paths = next(paths for name, paths in NAV if page.path in paths)
    hub = pages[section_paths[0]]
    if page.path != "/":
        if hub is not page:
            crumbs.append((hub.meta["nav"], hub.url))
        crumbs.append((page.meta["nav"], page.url))
    crumb_html = []
    for i, (name, url) in enumerate(crumbs):
        href = BASE_PATH + url[len(SITE_URL):]
        if i == len(crumbs) - 1:
            crumb_html.append(f'<li><span aria-current="page">{esc(name)}</span></li>')
        else:
            crumb_html.append(f'<li><a href="{href}">{esc(name)}</a></li>')

    idx = order.index(page.path)
    prev_page = pages[order[idx - 1]] if idx > 0 else None
    next_page = pages[order[idx + 1]] if idx + 1 < len(order) else None
    pager = ['<nav class="pager" aria-label="Previous and next guides">']
    if prev_page:
        pager.append(f'<a class="prev" href="{prev_page.href}"><span>Previous</span>{esc(prev_page.meta["nav"])}</a>')
    if next_page:
        pager.append(f'<a class="next" href="{next_page.href}"><span>Next</span>{esc(next_page.meta["nav"])}</a>')
    pager.append("</nav>")

    related = ""
    if page.related:
        items = "\n".join(f'<li><a href="{esc(u)}">{esc(t)}</a></li>' for u, t in page.related)
        related = f'<section class="related" aria-labelledby="related-reading">\n<h2 id="related-reading">Related reading</h2>\n<ul>\n{items}\n</ul>\n</section>'
        toc.append(("related-reading", "Related reading"))

    toc_html = ""
    if len(toc) > 1:
        links = "\n".join(f'<li><a href="#{i}">{esc(t)}</a></li>' for i, t in toc)
        toc_html = f'<aside class="toc" aria-label="On this page"><p>On this page</p><ul>\n{links}\n</ul></aside>'

    title_tag = page.meta.get("seo_title") or f'{page.meta["title"]} | {SITE_NAME}'
    og_type = "website" if page.path == "/" else "article"
    updated = page.meta.get("updated", "")
    updated_html = f'<p class="updated">Last updated <time datetime="{updated}">{updated}</time></p>' if updated else ""

    return f"""<!doctype html>
<html lang="en-AU">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title_tag)}</title>
<meta name="description" content="{esc(page.meta["description"])}">
<link rel="canonical" href="{page.url}">
<meta name="robots" content="index, follow">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="{SITE_NAME}">
<meta property="og:locale" content="en_AU">
<meta property="og:title" content="{esc(page.meta["title"])}">
<meta property="og:description" content="{esc(page.meta["description"])}">
<meta property="og:url" content="{page.url}">
<meta property="og:image" content="{SITE_URL}/assets/og-image.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Fulcrum Docs">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(page.meta["title"])}">
<meta name="twitter:description" content="{esc(page.meta["description"])}">
<meta name="twitter:image" content="{SITE_URL}/assets/og-image.png">
<meta name="theme-color" content="#14100f">
<link rel="icon" href="{BASE_PATH}/assets/fulcrum-logo.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="{BASE_PATH}/assets/fulcrum-logo.png">
<link rel="stylesheet" href="{BASE_PATH}/assets/site.css">
<script type="application/ld+json">
{json_ld(page, crumbs)}
</script>
</head>
<body>
<a class="skip-link" href="#main">Skip to content</a>
<header class="topbar">
<a class="brand" href="{BASE_PATH}/"><img src="{BASE_PATH}/assets/fulcrum-logo.svg" alt="" width="28" height="28"><span>Fulcrum <b>Docs</b></span></a>
<a class="menu-link" href="#docs-nav">Guides</a>
</header>
<div class="layout">
<main id="main">
<nav class="breadcrumbs" aria-label="Breadcrumb"><ol>{"".join(crumb_html)}</ol></nav>
<article>
<h1>{esc(page.meta["title"])}</h1>
<p class="lead">{esc(page.meta["description"])}</p>
{body}
{related}
{updated_html}
</article>
{"".join(pager)}
</main>
{toc_html}
{render_nav(pages, page)}
</div>
<footer class="footer">
<p>Fulcrum Docs is written and maintained by the Fulcrum Cortex team in Australia.</p>
<p><a href="{REPO_URL}">Suggest a correction on GitHub</a></p>
</footer>
</body>
</html>
"""


def render_404() -> str:
    return f"""<!doctype html>
<html lang="en-AU">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Page not found | {SITE_NAME}</title>
<meta name="robots" content="noindex">
<link rel="icon" href="{BASE_PATH}/assets/fulcrum-logo.svg" type="image/svg+xml">
<link rel="stylesheet" href="{BASE_PATH}/assets/site.css">
</head>
<body>
<header class="topbar">
<a class="brand" href="{BASE_PATH}/"><img src="{BASE_PATH}/assets/fulcrum-logo.svg" alt="" width="28" height="28"><span>Fulcrum <b>Docs</b></span></a>
</header>
<main id="main" class="not-found">
<h1>That page isn't here</h1>
<p>The guide may have moved. Start again from the <a href="{BASE_PATH}/">Fulcrum Docs home page</a>.</p>
</main>
</body>
</html>
"""


def sitemap(pages: list[Page]) -> str:
    rows = []
    for page in pages:
        lastmod = f"<lastmod>{page.meta['updated']}</lastmod>" if page.meta.get("updated") else ""
        rows.append(f"<url><loc>{page.url}</loc>{lastmod}</url>")
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            + "\n".join(rows) + "\n</urlset>\n")


def robots() -> str:
    return f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n"


def main() -> None:
    pages: dict[str, Page] = {}
    for src in sorted(SRC.rglob("*.html")):
        meta, related, body = parse_source(src)
        path = source_to_path(src)
        pages[path] = Page(path=path, meta=meta, body=body, related=related)

    order = [p for _, paths in NAV for p in paths]
    missing = [p for p in order if p not in pages]
    unlisted = [p for p in pages if p not in order]
    if missing or unlisted:
        sys.exit(f"NAV and sources disagree. Missing sources: {missing}. Not in NAV: {unlisted}")

    # Remove what the previous build wrote, so renamed pages don't linger.
    if MANIFEST.exists():
        for line in MANIFEST.read_text(encoding="utf-8").splitlines():
            target = ROOT / line
            if target.is_file():
                target.unlink()
        for line in sorted(MANIFEST.read_text(encoding="utf-8").splitlines(), reverse=True):
            parent = (ROOT / line).parent
            while parent != ROOT and parent.is_dir() and not any(parent.iterdir()):
                parent.rmdir()
                parent = parent.parent

    written: list[str] = []

    def write(rel: str, content: str) -> None:
        target = ROOT / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        written.append(rel)

    for path in order:
        rel = (path.strip("/") + "/index.html").lstrip("/")
        write(rel, render(pages[path], pages, order))
    write("404.html", render_404())
    write("sitemap.xml", sitemap([pages[p] for p in order]))
    write("robots.txt", robots())
    MANIFEST.write_text("\n".join(written) + "\n", encoding="utf-8")
    print(f"Built {len(order)} pages for {SITE_URL}")


if __name__ == "__main__":
    main()
