# Fulcrum documentation

User guides for Fulcrum Cortex and the apps it runs: Fulcrum Mail, Calendar, booking pages, Lyre and Fulcrum CRM.

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

Generated pages (`index.html`, `fulcrum-mail/`, `calendar/`, `pages/`, `lyre/`, `crm/`, `sitemap.xml`, `robots.txt`, `404.html`) are committed, because GitHub Pages serves the repository as it is.

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
