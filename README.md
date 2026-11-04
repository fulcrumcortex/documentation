# Fulcrum documentation

User guides for Fulcrum Cortex and the apps it runs: Fulcrum Code, Mail, Calendar, booking pages, Drive, Docs, Wallet, Sessions, Lyre and Fulcrum CRM.

Published with GitHub Pages at https://fulcrumcortex.github.io/documentation/.

## How the site works

The site is plain static HTML generated from sources in this repository. No JavaScript is needed to read a page, which keeps every guide fully crawlable.

| Path | What it is |
|------|------------|
| `_src/pages/**.html` | Page sources: a front-matter block followed by the article body in HTML |
| `build.py` | Generator (Python 3 standard library only). Writes the HTML pages, `sitemap.xml`, `robots.txt` and `404.html` |
| `scripts/check_site.py` | Checks headings, titles, descriptions, canonical URLs, JSON-LD and links |
| `scripts/make_og_image.py` | Redraws `assets/og-image.png` (needs Pillow) |
| `assets/` | Stylesheet, logo and social image |
| `_config.yml` | Holds `site_url` and stops GitHub Pages publishing the generator files |

Generated pages (`index.html`, `fulcrum-mail/`, `calendar/`, `pages/`, `lyre/`, `crm/`, `code/`, `drive/`, `docs/`, `wallet/`, `sessions/`, `sitemap.xml`, `robots.txt`, `404.html`) are committed, because GitHub Pages serves the repository as it is.

## Editing a guide

1. Edit or add a file in `_src/pages/`. A file at `_src/pages/crm/lists.html` becomes `/crm/lists/`.
2. If you add a page, list it in `NAV` in `build.py` so it appears in the sidebar, the sitemap and the previous/next links.
3. Run the build and the checks:

   ```bash
   python3 build.py
   python3 scripts/check_site.py            # offline checks
   python3 scripts/check_site.py --online   # also confirms every external link returns 200
   ```

4. Commit the source and the regenerated files together.

Front matter fields:

```text
title:        Page heading (H1) and Open Graph title
seo_title:    Optional <title>; defaults to "<title> | Fulcrum Docs"
description:  Meta description and lead paragraph (70-170 characters)
nav:          Sidebar and breadcrumb label
updated:      Last-updated date (YYYY-MM-DD), used in the sitemap and JSON-LD
about:        Product name for the TechArticle "about" property
howto:        Optional HowTo name. Steps come from the first <ol class="steps"> on the page
related:      "Related reading" links, one per line: "  - URL | Anchor text"
```

Root-relative links in page bodies (for example `href="/calendar/"`) are rewritten to include the site's base path at build time.

### Writing rules

- Describe only what the product does today, using the exact button and menu labels shown in the app.
- Link to relevant Fulcrum product pages and blog posts in the text, with descriptive anchor text, and add two to five related posts per page. Don't repeat the same anchor text across the site.
- Check every external link with `--online` before you commit. Link only to production sites.

## Publishing

GitHub Pages serves this repository from the `main` branch, root folder:
**Settings → Pages → Build and deployment → Source: Deploy from a branch → Branch: `main` / `(root)`**.

Note: while the site lives at `fulcrumcortex.github.io/documentation`, search engines read `robots.txt` only from the root of the host (`fulcrumcortex.github.io/robots.txt`), not from this folder. Submit `https://fulcrumcortex.github.io/documentation/sitemap.xml` directly in Google Search Console instead. With a custom domain, the generated `robots.txt` sits at the root and is used as written.

## Moving to a custom domain

To serve the docs from a custom domain such as `docs.fulcrumcortex.com`:

1. Change the one line in `_config.yml` to `site_url: https://docs.fulcrumcortex.com` and run `python3 build.py`. Canonical URLs, the sitemap, Open Graph tags and internal links all follow it.
2. Add a file named `CNAME` at the repository root containing `docs.fulcrumcortex.com`.
3. Create a DNS `CNAME` record for `docs` pointing to `fulcrumcortex.github.io`.
4. In **Settings → Pages**, enter the custom domain and tick **Enforce HTTPS** once the certificate is issued.
5. Resubmit the new `sitemap.xml` in Google Search Console.

## Screenshots and review

Screenshots use a local product build, a fresh browser context, blocked external network access and fixed fictional API data. Never reuse a signed-in personal browser profile. The Code screenshot uses its actual terminal renderer and a stub agent, without bootstrap, LSP or model requests. Captions distinguish demonstrations from live integration evidence.

- `node scripts/capture-screenshots.cjs /path/to/fulcrum-mail http://127.0.0.1:3187` captures the real local Mail, Calendar, booking, Drive and Docs interfaces. The source checkout needs installed Playwright and a running build.
- Run `scripts/capture-code.py` with the Code checkout’s Python environment to export the terminal screenshot.
- Visually inspect every output at full resolution, OCR raster screenshots where available, and check metadata and the SVG text before publishing.
- Recalculate `_src/screenshot-review.json` after approving a replacement.

The November 2026 review expands 33 guides to 50: eight Code guides, dedicated Drive/Docs/Wallet/Sessions guides, Lyre resources and additional CRM guides. Existing task guides gain worked examples, result verification and troubleshooting. `_src/review-notes.md` records the evidence scope and limits.

`landing/` is a noindex preview of the separately hosted GitHub profile homepage. The production homepage lives in `fulcrumcortex/fulcrumcortex.github.io`; edit that repository for future homepage changes.

## Cortex Chat reference

`_src/chat-guide-catalog.json` holds 100 individually authored task guides for chat.fulcrumcortex.com. Sources are rendered into `_src/pages/cortex-chat/`; the shared setting explanations distinguish identity, runtime, application access and saved tool policies. The Chat hub and screenshot tour index the content. Twenty-two actual UI captures use a local production build with fictional OIDC/API fixtures; ready voice states are simulations, not live call evidence. Provenance and hashes are in `_src/chat-screenshot-review.json`. The sidebar title filter is progressive enhancement; every guide remains available without JavaScript.
