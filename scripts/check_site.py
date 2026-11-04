#!/usr/bin/env python3
"""Check the built site before publishing. Standard library only.

    python3 scripts/check_site.py            # structure, SEO tags, internal links
    python3 scripts/check_site.py --online   # also fetch every external link

Checks: one <h1> per page, unique <title> and meta description, canonical URL,
Open Graph tags, valid JSON-LD with BreadcrumbList, balanced tags, unique ids,
internal links and #anchors that resolve, no rel=nofollow/ugc, external links
only to the allowed production domains, and (with --online) HTTP 200 for each
external link and external image.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import build  # noqa: E402

ALLOWED_HOSTS = {
    "fulcrumcortex.com", "fulcrumcrm.app", "fulcrumcode.app", "lyre.au",
    "docs.lyre.au", "fulcrumail.app", "github.com", "fulcrumcortex.github.io",
    "www.f6s.com",  # F6S follow badge on the home page (link and badge image)
}
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[str] = []
        self.errors: list[str] = []
        self.h1 = 0
        self.title = ""
        self._in_title = False
        self.meta: dict[str, str] = {}
        self.canonical = ""
        self.ids: list[str] = []
        self.links: list[tuple[str, str, str]] = []  # (href, rel, text)
        self.images: list[dict[str, str]] = []
        self._link: list | None = None
        self.jsonld: list[str] = []
        self._in_jsonld = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag not in VOID:
            self.stack.append(tag)
        if "id" in a:
            self.ids.append(a["id"])
        if tag == "img":
            self.images.append(a)
        if tag == "h1":
            self.h1 += 1
        if tag == "title":
            self._in_title = True
        if tag == "meta":
            key = a.get("name") or a.get("property")
            if key:
                self.meta[key] = a.get("content", "")
        if tag == "link" and a.get("rel") == "canonical":
            self.canonical = a.get("href", "")
        if tag == "a":
            self._link = [a.get("href", ""), a.get("rel", ""), ""]
        if tag == "script" and a.get("type") == "application/ld+json":
            self._in_jsonld = True
            self.jsonld.append("")

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if not self.stack or self.stack[-1] != tag:
            self.errors.append(f"unexpected </{tag}> (open: {self.stack[-3:]})")
            if tag in self.stack:
                while self.stack and self.stack.pop() != tag:
                    pass
            return
        self.stack.pop()
        if tag == "title":
            self._in_title = False
        if tag == "a" and self._link is not None:
            self.links.append((self._link[0], self._link[1], re.sub(r"\s+", " ", self._link[2]).strip()))
            self._link = None
        if tag == "script":
            self._in_jsonld = False

    def handle_data(self, data):
        if self._in_title:
            self.title += data
        if self._link is not None:
            self._link[2] += data
        if self._in_jsonld:
            self.jsonld[-1] += data


def built_pages() -> dict[str, Path]:
    order = [p for _, paths in build.NAV for p in paths]
    return {p: ROOT / (p.strip("/") + "/index.html").lstrip("/") for p in order}


def main() -> int:
    online = "--online" in sys.argv
    problems: list[str] = []
    pages = built_pages()
    parsed: dict[str, PageParser] = {}
    external_images: dict[str, list[str]] = defaultdict(list)
    for path, file in pages.items():
        if not file.exists():
            problems.append(f"{path}: not built")
            continue
        p = PageParser()
        p.feed(file.read_text(encoding="utf-8"))
        parsed[path] = p
        if p.stack:
            problems.append(f"{path}: unclosed tags {p.stack}")
        problems += [f"{path}: {e}" for e in p.errors]
        if p.h1 != 1:
            problems.append(f"{path}: {p.h1} <h1> elements")
        if p.canonical != build.SITE_URL + path:
            problems.append(f"{path}: canonical {p.canonical}")
        desc = p.meta.get("description", "")
        if not 70 <= len(desc) <= 170:
            problems.append(f"{path}: description length {len(desc)}")
        if len(p.title) > 90:
            problems.append(f"{path}: title length {len(p.title)}")
        for key in ("og:title", "og:description", "og:url", "og:image", "twitter:card"):
            if not p.meta.get(key):
                problems.append(f"{path}: missing {key}")
        for img in p.images:
            src = img.get("src", "")
            if not img.get("alt", "").strip() and "/screenshots/" in src:
                problems.append(f"{path}: screenshot needs descriptive alt text")
            if src.startswith(build.BASE_PATH + "/"):
                target = ROOT / src[len(build.BASE_PATH):].lstrip("/")
                if not target.is_file():
                    problems.append(f"{path}: missing image {src}")
            elif src.startswith("http"):
                host = re.sub(r"^https?://([^/]+).*", r"\1", src)
                if host not in ALLOWED_HOSTS:
                    problems.append(f"{path}: external image host not allowed: {src}")
                external_images[src].append(path)
        dup_ids = [i for i, n in Counter(p.ids).items() if n > 1]
        if dup_ids:
            problems.append(f"{path}: duplicate ids {dup_ids}")
        for block in p.jsonld:
            try:
                data = json.loads(block)
                types = {node["@type"] for node in data["@graph"]}
                for needed in ("Organization", "BreadcrumbList", "TechArticle"):
                    if needed not in types:
                        problems.append(f"{path}: JSON-LD lacks {needed}")
            except (ValueError, KeyError) as exc:
                problems.append(f"{path}: JSON-LD error {exc}")

    for kind in ("title", "description"):
        seen = defaultdict(list)
        for path, p in parsed.items():
            seen[p.title if kind == "title" else p.meta.get("description")].append(path)
        for value, paths in seen.items():
            if len(paths) > 1:
                problems.append(f"duplicate {kind} on {paths}")

    external: dict[str, list[str]] = defaultdict(list)
    anchors: dict[str, set[str]] = defaultdict(set)
    for path, p in parsed.items():
        for href, rel, text in p.links:
            if "nofollow" in rel or "ugc" in rel:
                problems.append(f"{path}: rel={rel} on {href}")
            if href.startswith("#"):
                if href[1:] not in p.ids:
                    problems.append(f"{path}: missing anchor {href}")
            elif href.startswith("http"):
                host = re.sub(r"^https?://([^/]+).*", r"\1", href)
                if host not in ALLOWED_HOSTS:
                    problems.append(f"{path}: external host not allowed: {href}")
                external[href].append(path)
                anchors[href].add(text)
            else:
                target, _, frag = href.partition("#")
                if not target.startswith(build.BASE_PATH + "/"):
                    problems.append(f"{path}: odd link {href}")
                    continue
                site_path = target[len(build.BASE_PATH):]
                file = ROOT / site_path.lstrip("/")
                if site_path.endswith("/"):
                    file = file / "index.html"
                if not file.exists():
                    problems.append(f"{path}: broken internal link {href}")
                elif frag and site_path in parsed and frag not in parsed[site_path].ids:
                    problems.append(f"{path}: missing anchor {href}")

    print(f"{len(parsed)} pages checked, {len(external)} distinct external URLs, "
          f"{len(external_images)} external images")
    if online:
        for url in sorted(set(external) | set(external_images)):
            out = subprocess.run(
                ["curl", "-s", "-o", "/dev/null", "-L", "--max-time", "30", "-A",
                 "Mozilla/5.0 (compatible; FulcrumDocsLinkCheck/1.0)", "-w", "%{http_code} %{url_effective}", url],
                capture_output=True, text=True)
            code, _, final = out.stdout.partition(" ")
            norm = lambda u: u.rstrip("/")
            status = "ok" if code == "200" and norm(final) == norm(url) else "FAIL"
            print(f"{status} {code} {url}" + ("" if norm(final) == norm(url) else f" -> {final}"))
            if status != "ok":
                problems.append(f"external link {url}: {code} {final}")

    if problems:
        print("\n".join(problems))
        print(f"{len(problems)} problem(s)")
        return 1
    print("All checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
