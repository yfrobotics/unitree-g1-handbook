"""Validate SEO metadata in the built site: python scripts/check_seo.py."""

from collections import Counter
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import unquote
import xml.etree.ElementTree as ET


class Head(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.meta = {}
        self.canonicals = []
        self.schemas = []
        self.title = ""
        self.capture = None
        self.feed(html.split("</head>", 1)[0])

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "meta":
            key = attrs.get("name", attrs.get("property"))
            self.meta.setdefault(key, []).append(attrs.get("content", ""))
        elif tag == "link" and attrs.get("rel") == "canonical":
            self.canonicals.append(attrs["href"])
        elif tag == "title":
            self.capture = "title"
        elif tag == "script" and attrs.get("type") == "application/ld+json":
            self.capture = "schema"
            self.schemas.append("")

    def handle_data(self, data):
        if self.capture == "title":
            self.title += data
        elif self.capture == "schema":
            self.schemas[-1] += data

    def handle_endtag(self, tag):
        if tag in {"title", "script"}:
            self.capture = None


def main():
    site = Path(__file__).resolve().parents[1] / "site"
    urls = [node.text for node in ET.parse(site / "sitemap.xml").iterfind(
        ".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc"
    )]
    home = "https://yfrobotics.github.io/unitree-g1-handbook/"
    assert home in urls, "Homepage missing from sitemap"
    assert len(urls) == len(set(urls)), "Duplicate sitemap URLs"
    assert not any("/superpowers/" in url for url in urls), "Internal notes published"
    lastmods = [node.text for node in ET.parse(site / "sitemap.xml").iterfind(
        ".//{http://www.sitemaps.org/schemas/sitemap/0.9}lastmod"
    )]
    assert len(lastmods) == len(urls), "Every sitemap URL needs <lastmod>"
    assert all(re.fullmatch(r"\d{4}-\d{2}-\d{2}", value) for value in lastmods), lastmods
    image = home + "_static/social-card.png"
    assert (site / "_static/social-card.png").is_file(), "Missing social card"
    descriptions, titles = [], []
    for url in urls:
        assert url.startswith(home), url
        relative = unquote(url[len(home):])
        path = site / relative / "index.html"
        head = Head(path.read_text(encoding="utf-8"))
        assert head.canonicals == [url], f"Incorrect canonical: {url}"
        for key in ("description", "og:title", "og:description", "og:url",
                    "og:type", "og:locale", "og:site_name", "twitter:card",
                    "twitter:title", "twitter:description", "og:image",
                    "twitter:image"):
            values = head.meta.get(key, [])
            assert len(values) == 1 and values[0].strip(), f"Invalid {key}: {url}"
        assert head.meta["og:url"] == [url], url
        assert head.meta["og:title"] == head.meta["twitter:title"] == [head.title], url
        assert head.meta["description"] == head.meta["og:description"] == head.meta["twitter:description"], url
        assert head.meta["og:image"] == head.meta["twitter:image"] == [image], url
        assert head.meta["twitter:card"] == ["summary_large_image"], url
        assert not any("noindex" in value for value in head.meta.get("robots", [])), url
        descriptions.extend(head.meta["description"])
        titles.append(head.title)
        schemas = {schema["@type"]: schema for schema in map(json.loads, head.schemas)}
        if url == home:
            assert list(schemas) == ["WebSite"], f"Missing WebSite schema: {url}"
            assert schemas["WebSite"]["url"] == home
        else:
            assert list(schemas) == ["TechArticle", "BreadcrumbList"], f"Invalid schemas: {url}"
            article = schemas["TechArticle"]
            assert article["url"] == url and article["headline"], url
            assert article["description"] == head.meta["description"][0], url
            assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", article.get("dateModified", "")), url
            assert head.meta.get("article:modified_time") == [article["dateModified"]], url
            schema = schemas["BreadcrumbList"]
            crumbs = schema["itemListElement"]
            assert len(crumbs) >= 2 and crumbs[-1]["item"] == url, url
            assert crumbs[0]["item"] == home, url
            for position, crumb in enumerate(crumbs, 1):
                assert crumb["position"] == position and crumb["name"], url
                assert crumb["item"] in urls, f"Broken breadcrumb: {url}"
    for label, values in (("description", descriptions), ("title", titles)):
        duplicates = [value for value, count in Counter(values).items() if count > 1]
        assert not duplicates, f"Duplicate {label}: {duplicates}"
    error = Head((site / "404.html").read_text(encoding="utf-8"))
    assert error.meta.get("robots") == ["noindex"], "404 must be noindex"
    print(f"SEO checks passed for {len(urls)} pages and the 404 page.")


if __name__ == "__main__":
    main()
