"""Derive page descriptions, dates, and structured data from the published content/navigation."""

from html.parser import HTMLParser
import re

from markupsafe import escape


class Paragraphs(HTMLParser):
    """Read prose without markup, code, equations, or admonition labels."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.paragraphs = []
        self.parts = None
        self.ignored = False

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "p":
            self.parts = []
            self.ignored = "admonition-title" in attributes.get("class", "")
        if self.parts is not None and (
            tag in {"code", "script", "style"}
            or "arithmatex" in attributes.get("class", "")
        ):
            self.ignored = True

    def handle_data(self, data):
        if self.parts is not None:
            self.parts.append(data)

    def handle_endtag(self, tag):
        if tag == "p" and self.parts is not None:
            text = re.sub(r"\s+", " ", "".join(self.parts)).strip()
            if not self.ignored and len(text) >= 25:
                self.paragraphs.append(text)
            self.parts = None


def summarize(html, fallback):
    parser = Paragraphs()
    parser.feed(html)
    text = parser.paragraphs[0] if parser.paragraphs else fallback
    if len(text) <= 160:
        return text
    # Prefer a complete sentence; otherwise mark the shortened excerpt explicitly.
    excerpt = text[:159]
    boundary = max(excerpt.rfind(mark) for mark in "。！？")
    return excerpt[: boundary + 1] if boundary >= 60 else excerpt.rstrip() + "…"


def on_page_content(html, page, config, files):
    if not page.meta.get("description"):
        page.meta["description"] = summarize(
            html, f"{page.title}：{config.site_description}"
        )
    # Material renders this attribute without autoescaping. Markup also prevents
    # double escaping when the same description passes through our template's |e.
    page.meta["description"] = escape(page.meta["description"])
    # Sitemap <lastmod> defaults to the build date for every page; use the last
    # commit that touched the page so crawlers can tell which pages changed.
    modified = page.meta.get("git_revision_date_localized_raw_iso_date")
    if modified:
        page.update_date = modified
    return html


def on_page_context(context, page, config, nav):
    publisher = {"@type": "Organization", "name": config.site_author,
                 "url": config.site_url}
    if page.is_homepage:
        context["seo_schemas"] = [{
            "@context": "https://schema.org",
            "@type": "WebSite",
            "name": config.site_name,
            "alternateName": "Unitree G1 Handbook",
            "url": config.site_url,
            "description": page.meta["description"].unescape(),
            "inLanguage": "zh-CN",
            "publisher": publisher,
        }]
        return context
    trail = [(config.site_name, config.site_url)]
    ancestors = []
    parent = page.parent
    while parent is not None:
        ancestors.append(parent)
        parent = parent.parent
    for section in reversed(ancestors):
        # Chapter hubs and nested topic landing pages are first in each section.
        landing = section.children[0] if section.children else None
        if landing and landing.is_page and landing is not page:
            trail.append((landing.title, landing.canonical_url))
    trail.append((page.title, page.canonical_url))
    article = {
        "@context": "https://schema.org",
        "@type": "TechArticle",
        "headline": page.meta.get("title") or page.title,
        "description": page.meta["description"].unescape(),
        "url": page.canonical_url,
        "mainEntityOfPage": page.canonical_url,
        "image": config.site_url + "_static/social-card.png",
        "inLanguage": "zh-CN",
        "about": {"@type": "Product", "name": "Unitree G1",
                  "brand": {"@type": "Brand", "name": "Unitree Robotics"}},
        "author": publisher,
        "publisher": publisher,
        "isPartOf": {"@type": "WebSite", "name": config.site_name,
                     "url": config.site_url},
    }
    if page.update_date:
        article["dateModified"] = page.update_date
    context["seo_schemas"] = [article, {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": position, "name": name, "item": url}
            for position, (name, url) in enumerate(trail, 1)
        ],
    }]
    return context
