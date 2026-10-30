#!/usr/bin/env python3
"""Validate the generated VitaGauge site, without network or third-party packages.

Run after build_pages.py. --output writes a reviewable JSON report; failures
exit with status 1. This is a static publishing check, not a crawler/indexing or
legal-compliance guarantee. Secret matches are reported without their contents.
"""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from html import unescape
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import unquote, urljoin, urlsplit
import xml.etree.ElementTree as ET


VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}
PUBLIC_TEXT = {".html", ".css", ".json", ".txt", ".xml", ".webmanifest", ".svg"}
SECRET_PATTERNS = {
    "private-key": re.compile(r"-----BEGIN (?:[A-Z0-9]+ )*PRIVATE KEY-----"),
    "provider-api-key": re.compile(r"\b(?:sk-[A-Za-z0-9_-]{20,}|gsk_[A-Za-z0-9]{20,}|xai-[A-Za-z0-9_-]{20,})\b"),
    "google-api-key": re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b"),
    "github-token": re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})\b"),
    "aws-access-key": re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"),
    "aliyun-access-key": re.compile(r"\bLTAI[A-Za-z0-9]{16,}\b"),
}
STALE_PATTERNS = {
    "old-version": re.compile(r"(?<![\d.])1\.1\.0(?![\d.])"),
    "unreleased-1.2.0-en": re.compile(r"(?:planned|upcoming|not (?:yet )?(?:live|released)|in preparation).{0,90}1\.2\.0|1\.2\.0.{0,90}(?:not (?:yet )?(?:live|released)|in preparation|planned)", re.I),
    "unreleased-1.2.0-zh": re.compile(r"(?:计划随|待发布|待审|尚未发布|准备中).{0,60}1\.2\.0|1\.2\.0.{0,60}(?:尚未发布|准备中|待审|待发布)"),
}


def normalized(value: str) -> str:
    return " ".join(unescape(value).split())


@dataclass
class Element:
    tag: str
    attrs: dict[str, str]
    children: list[Element | str] = field(default_factory=list)

    def text(self, visible: bool = False) -> str:
        if visible and (self.tag in {"script", "style", "head"} or "hidden" in self.attrs or self.attrs.get("aria-hidden") == "true"):
            return ""
        return " ".join(child.text(visible) if isinstance(child, Element) else child for child in self.children)


class Document(HTMLParser):
    def __init__(self, content: str):
        super().__init__(convert_charrefs=True)
        self.root = Element("document", {})
        self.stack = [self.root]
        self.elements: list[Element] = []
        self.feed(content)
        self.close()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        node = Element(tag, {key: value or "" for key, value in attrs})
        self.stack[-1].children.append(node)
        self.elements.append(node)
        if tag not in VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag: str) -> None:
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index].tag == tag:
                del self.stack[index:]
                break

    def handle_data(self, data: str) -> None:
        self.stack[-1].children.append(data)

    def nodes(self, tag: str) -> list[Element]:
        return [node for node in self.elements if node.tag == tag]

    def metas(self, key: str) -> list[str]:
        return [node.attrs.get("content", "") for node in self.nodes("meta") if node.attrs.get("name", node.attrs.get("property", "")).lower() == key]

    def links(self, relation: str) -> list[Element]:
        return [node for node in self.nodes("link") if relation in node.attrs.get("rel", "").split()]


def walk_json(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk_json(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_json(child)


class Validator:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.checks: list[dict] = []
        self.pages: dict[str, Document] = {}
        self.page_files: dict[str, str] = {}
        self.references = 0
        self.faq_pairs = 0
        self.facts = json.loads((self.root / "product-facts.json").read_text(encoding="utf-8"))
        self.base = self.facts["sites"]["base"].rstrip("/")
        self.base_parts = urlsplit(self.base)
        self.base_path = self.base_parts.path.rstrip("/")

    def check(self, name: str, passed: bool, file: str = "", detail: str = "") -> None:
        self.checks.append({"check": name, "passed": bool(passed), "file": file, "detail": detail})

    def read(self, relative: str) -> str:
        path = self.root / relative
        if not path.is_file():
            self.check("required-file", False, relative, "File is missing")
            return ""
        return path.read_text(encoding="utf-8")

    def local_target(self, link: str, source_url: str) -> tuple[Path | None, str]:
        absolute = urljoin(source_url, link)
        parts = urlsplit(absolute)
        if parts.scheme not in {"http", "https"} or parts.netloc != self.base_parts.netloc:
            return None, ""
        path = unquote(parts.path)
        if path != self.base_path and not path.startswith(self.base_path + "/"):
            return self.root / "__outside_project_base__", parts.fragment
        relative = path[len(self.base_path):].lstrip("/")
        target = self.root / relative
        if path.endswith("/") or not relative:
            target = target / "index.html"
        elif target.is_dir():
            target = target / "index.html"
        return target, unquote(parts.fragment)

    def verify_reference(self, link: str, source_url: str, file: str, anchors: bool = True) -> None:
        if not link or link.startswith(("data:", "mailto:", "tel:", "javascript:")):
            if link.startswith("javascript:"):
                self.check("no-javascript-url", False, file)
            return
        target, fragment = self.local_target(link, source_url)
        if target is None:
            return
        self.references += 1
        if not target.is_file():
            self.check("internal-reference", False, file, f"Missing internal target: {link}")
            return
        if anchors and fragment and target.suffix == ".html":
            relative = target.relative_to(self.root).as_posix()
            document = next((doc for url, doc in self.pages.items() if self.page_files[url] == relative), None)
            if document is None:
                document = Document(target.read_text(encoding="utf-8"))
            ids = {node.attrs["id"] for node in document.elements if "id" in node.attrs}
            ids.update(node.attrs["name"] for node in document.nodes("a") if "name" in node.attrs)
            if fragment not in ids:
                self.check("internal-anchor", False, file, f"Missing fragment: {link}")

    def page_metadata(self, url: str, document: Document, file: str, not_found: bool = False) -> None:
        titles = document.nodes("title")
        self.check("one-title", len(titles) == 1 and bool(normalized(titles[0].text())), file)
        description = document.metas("description")
        self.check("one-description", len(description) == 1 and bool(description[0].strip()), file)
        h1s = document.nodes("h1")
        self.check("one-h1", len(h1s) == 1 and bool(normalized(h1s[0].text())), file)
        canonical = document.links("canonical")
        self.check("canonical", len(canonical) == 1 and canonical[0].attrs.get("href") == url, file)
        self.check("modified-date-meta", document.metas("article:modified_time") == [self.facts["updated"]], file)
        ids = [node.attrs["id"] for node in document.elements if "id" in node.attrs]
        self.check("unique-ids", len(ids) == len(set(ids)), file)
        robots = document.metas("robots")
        googlebot = document.metas("googlebot")
        if not_found:
            self.check("404-one-noindex-robots", len(robots) == 1 and "noindex" in robots[0].lower().split(","), file)
            self.check("404-googlebot-no-index-conflict", len(googlebot) <= 1 and all("index" not in value.lower().split(",") or "noindex" in value.lower().split(",") for value in googlebot), file)
            return
        self.check("indexable-robots", len(robots) == 1 and "noindex" not in robots[0].lower(), file)
        alternates = [node for node in document.links("alternate") if "hreflang" in node.attrs]
        languages = [node.attrs["hreflang"] for node in alternates]
        self.check("hreflang-unique-languages", Counter(languages) == Counter(["zh-Hans", "en", "x-default"]), file)
        mapping = {node.attrs["hreflang"]: node.attrs.get("href", "") for node in alternates}
        own_language = "en" if file.startswith("en/") else "zh-Hans"
        self.check("html-language", len(document.nodes("html")) == 1 and document.nodes("html")[0].attrs.get("lang") == own_language, file)
        self.check("hreflang-self", mapping.get(own_language) == url, file)
        self.check("hreflang-default", mapping.get("x-default") == mapping.get("zh-Hans"), file)
        for language in ("zh-Hans", "en"):
            target = mapping.get(language, "")
            peer = self.pages.get(target)
            peer_mapping = {node.attrs["hreflang"]: node.attrs.get("href", "") for node in peer.links("alternate") if "hreflang" in node.attrs} if peer else {}
            self.check("hreflang-reciprocal", bool(peer) and peer_mapping == mapping, file, language)

    def page_schema(self, document: Document, file: str) -> None:
        payloads = []
        scripts = [node for node in document.nodes("script") if node.attrs.get("type") == "application/ld+json"]
        self.check("json-ld-present", bool(scripts), file)
        for script in scripts:
            try:
                payloads.append(json.loads(script.text()))
            except (json.JSONDecodeError, TypeError) as error:
                self.check("json-ld-valid", False, file, str(error))
        nodes = [node for payload in payloads for node in walk_json(payload)]
        apps = [node for node in nodes if node.get("@type") in ("SoftwareApplication", "MobileApplication")]
        # Terms and sources may describe a WebPage without repeating the app
        # entity; every SoftwareApplication that is present must be current.
        core_page = file not in {"terms/index.html", "en/terms/index.html", "sources/index.html", "en/sources/index.html"}
        self.check("schema-app-version", (bool(apps) or not core_page) and all(node.get("softwareVersion") == self.facts["product"]["version"] for node in apps), file)
        for node in apps:
            self.check("schema-app-release-date", node.get("dateModified") == self.facts["product"]["released"], file)
        visible_pairs = []
        for detail in document.nodes("details"):
            summaries = [node for node in detail.children if isinstance(node, Element) and node.tag == "summary"]
            if len(summaries) == 1:
                answer = " ".join(node.text(True) if isinstance(node, Element) else node for node in detail.children if node is not summaries[0])
                visible_pairs.append((normalized(summaries[0].text(True)), normalized(answer)))
        schema_pairs = []
        for node in nodes:
            if node.get("@type") == "FAQPage":
                for question in node.get("mainEntity", []):
                    answer = question.get("acceptedAnswer", {})
                    schema_pairs.append((normalized(question.get("name", "")), normalized(Document(answer.get("text", "")).root.text(True))))
        self.faq_pairs += len(schema_pairs)
        if schema_pairs or visible_pairs:
            self.check("faq-visible-schema-match", Counter(schema_pairs) == Counter(visible_pairs), file, f"schema={len(schema_pairs)}, visible={len(visible_pairs)}")

    def all_references(self) -> None:
        for url, document in self.pages.items():
            file = self.page_files[url]
            for node in document.elements:
                for attribute in ("href", "src", "poster"):
                    if attribute in node.attrs:
                        self.verify_reference(node.attrs[attribute], url, file)
                if "srcset" in node.attrs:
                    for item in node.attrs["srcset"].split(","):
                        if item.strip():
                            self.verify_reference(item.strip().split()[0], url, file)
                if node.tag == "meta" and node.attrs.get("property", node.attrs.get("name")) in {"og:image", "twitter:image"}:
                    self.verify_reference(node.attrs.get("content", ""), url, file)
                if node.tag == "script" and node.attrs.get("type") == "application/ld+json":
                    try:
                        payload = json.loads(node.text())
                    except json.JSONDecodeError:
                        continue
                    for obj in walk_json(payload):
                        for key in ("image", "logo", "screenshot", "contentUrl"):
                            links = obj.get(key, [])
                            links = [links] if isinstance(links, str) else links
                            if isinstance(links, list):
                                for link in links:
                                    if isinstance(link, str):
                                        self.verify_reference(link, url, file, anchors=False)
        for path in self.root.rglob("*.css"):
            file = path.relative_to(self.root).as_posix()
            content = path.read_text(encoding="utf-8")
            for match in re.finditer(r"url\(\s*['\"]?([^)'\"]+)['\"]?\s*\)", content):
                self.verify_reference(match.group(1).strip(), f"{self.base}/{file}", file)

    def sitemap(self, expected: set[str]) -> None:
        ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9", "x": "http://www.w3.org/1999/xhtml", "i": "http://www.google.com/schemas/sitemap-image/1.1"}
        try:
            tree = ET.fromstring(self.read("sitemap.xml"))
        except ET.ParseError as error:
            self.check("sitemap-valid-xml", False, "sitemap.xml", str(error))
            return
        entries = tree.findall("s:url", ns)
        urls = [entry.findtext("s:loc", default="", namespaces=ns) for entry in entries]
        self.check("sitemap-12-exact-urls", len(urls) == 12 and len(set(urls)) == 12 and set(urls) == expected, "sitemap.xml")
        for entry, url in zip(entries, urls):
            self.check("sitemap-lastmod", entry.findtext("s:lastmod", namespaces=ns) == self.facts["updated"], "sitemap.xml", url)
            alternates = entry.findall("x:link", ns)
            actual = {link.attrib.get("hreflang"): link.attrib.get("href") for link in alternates}
            document = self.pages.get(url)
            wanted = {node.attrs["hreflang"]: node.attrs.get("href", "") for node in document.links("alternate") if "hreflang" in node.attrs} if document else {}
            self.check("sitemap-hreflang", len(alternates) == 3 and actual == wanted, "sitemap.xml", url)
            for image in entry.findall("i:image/i:loc", ns):
                self.verify_reference(image.text or "", self.base + "/sitemap.xml", "sitemap.xml")

    def machine_files(self) -> None:
        facts = self.facts
        product = facts["product"]
        dates = {"updated": facts["updated"], "reviewed": facts.get("reviewed"), "privacyReviewedDate": facts["legal"].get("privacyReviewedDate"), "effective": facts["legal"]["privacyEffectiveDate"], "released": product["released"], "firstReleased": product["firstReleased"]}
        valid_dates = True
        for key, value in dates.items():
            try:
                date.fromisoformat(value)
            except (TypeError, ValueError):
                valid_dates = False
                self.check("date-iso", False, "product-facts.json", key)
        if valid_dates:
            self.check("review-dates-consistent", dates["updated"] == dates["reviewed"] == dates["privacyReviewedDate"], "product-facts.json")
            self.check("date-order", dates["firstReleased"] <= dates["released"] <= dates["updated"] and dates["effective"] <= dates["reviewed"], "product-facts.json")
        self.check("facts-released-status", facts.get("status") in {"live", "released"} and "pendingRelease" not in facts, "product-facts.json")
        release = facts.get("currentRelease", {})
        self.check("facts-current-release", release.get("version") == product["version"] and "not_released" not in str(release.get("status", "")), "product-facts.json")
        for filename in ("llms.txt", "llms-full.txt"):
            text = self.read(filename)
            self.check("machine-version-date", product["version"] in text and facts["reviewed"] in text, filename)
            self.check("machine-store-identity", str(facts["stores"]["appleId"]) in text and facts["legal"]["email"] in text, filename)
        for filename in ("llms.txt", "ai.txt"):
            original = self.read(filename)
            mirror = self.read(".well-known/" + filename)
            self.check("well-known-mirror", bool(original) and original == mirror, filename)
        robots = self.read("robots.txt")
        self.check("robots-sitemap", f"Sitemap: {self.base}/sitemap.xml" in robots, "robots.txt")
        self.check("robots-public-crawl", bool(re.search(r"User-agent:\s*\*\s*\nAllow:\s*/", robots, re.I)) and not re.search(r"Disallow:\s*/\s*(?:\n|$)", robots, re.I), "robots.txt")
        humans = self.read("humans.txt")
        self.check("humans-review-date", facts["reviewed"] in humans, "humans.txt")
        security = self.read(".well-known/security.txt")
        expiry = re.search(r"^Expires:\s*(\S+)", security, re.M)
        try:
            self.check("security-not-expired", bool(expiry) and datetime.fromisoformat(expiry.group(1).replace("Z", "+00:00")) > datetime.combine(date.fromisoformat(facts["updated"]), datetime.min.time(), tzinfo=timezone.utc), ".well-known/security.txt")
        except ValueError:
            self.check("security-not-expired", False, ".well-known/security.txt")
        manifest_text = self.read("site.webmanifest")
        try:
            manifest = json.loads(manifest_text)
            self.check("manifest-scope", manifest.get("scope") == self.base + "/", "site.webmanifest")
            self.verify_reference(manifest.get("start_url", ""), self.base + "/", "site.webmanifest")
            for icon in manifest.get("icons", []):
                self.verify_reference(icon.get("src", ""), self.base + "/", "site.webmanifest")
        except json.JSONDecodeError as error:
            self.check("manifest-valid-json", False, "site.webmanifest", str(error))
        self.check("nojekyll-present", (self.root / ".nojekyll").is_file(), ".nojekyll")

    def public_content(self) -> None:
        for path in sorted(self.root.rglob("*")):
            if not path.is_file() or ".git" in path.relative_to(self.root).parts:
                continue
            file = path.relative_to(self.root).as_posix()
            if path.name in {".env", ".env.local", ".env.production"} or path.suffix in {".p8", ".p12", ".pem", ".key", ".mobileprovision"}:
                self.check("no-credential-file", False, file)
            if path.suffix not in PUBLIC_TEXT:
                continue
            text = path.read_text(encoding="utf-8")
            if path.suffix == ".json":
                try:
                    json.loads(text)
                except json.JSONDecodeError as error:
                    self.check("public-json-valid", False, file, str(error))
            for label, pattern in STALE_PATTERNS.items():
                if pattern.search(text):
                    self.check("no-stale-release-assertion", False, file, label)
            for label, pattern in SECRET_PATTERNS.items():
                match = pattern.search(text)
                if match:
                    line = text.count("\n", 0, match.start()) + 1
                    self.check("no-secret-material", False, file, f"{label} at line {line}; value withheld")

    def run(self) -> dict:
        routes = list(self.facts["sites"]["paths"].values())
        expected: set[str] = set()
        for route in routes:
            url = self.base + "/" + route.strip("/") + "/" if route.strip("/") else self.base + "/"
            relative = route.strip("/") + "/index.html" if route.strip("/") else "index.html"
            expected.add(url)
            self.pages[url] = Document(self.read(relative))
            self.page_files[url] = relative
        self.check("12-public-routes", len(routes) == len(expected) == 12, "product-facts.json")
        not_found_url = self.base + "/404.html"
        self.pages[not_found_url] = Document(self.read("404.html"))
        self.page_files[not_found_url] = "404.html"
        html_files = {path.relative_to(self.root).as_posix() for path in self.root.rglob("*.html") if ".git" not in path.relative_to(self.root).parts}
        self.check("13-generated-html-files", html_files == set(self.page_files.values()), detail=f"found={len(html_files)}")
        for url, document in self.pages.items():
            file = self.page_files[url]
            self.page_metadata(url, document, file, not_found=(file == "404.html"))
            if file != "404.html":
                self.page_schema(document, file)
        for label, values in (("unique-titles", [normalized(document.nodes("title")[0].text()) for document in self.pages.values() if document.nodes("title")]), ("unique-descriptions", [document.metas("description")[0] for document in self.pages.values() if document.metas("description")])):
            self.check(label, len(values) == len(self.pages) == len(set(values)))
        self.all_references()
        self.sitemap(expected)
        self.machine_files()
        self.public_content()
        errors = [check for check in self.checks if not check["passed"]]
        self.check("internal-references-complete", not any(check["check"] in {"internal-reference", "internal-anchor"} for check in errors), detail=f"checked={self.references}")
        return {"passed": not errors, "site": self.base, "version": self.facts["product"]["version"], "reviewed": self.facts["reviewed"], "summary": {"htmlPages": len(self.pages), "sitemapUrls": len(expected), "internalReferences": self.references, "faqPairs": self.faq_pairs, "checks": len(self.checks), "failures": len(errors)}, "errors": errors, "checks": self.checks}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent, help="Generated site directory (default: script directory)")
    parser.add_argument("--output", type=Path, help="Optional path for the complete JSON verification report")
    args = parser.parse_args()
    try:
        report = Validator(args.root).run()
    except (OSError, KeyError, TypeError, ValueError) as error:
        report = {"passed": False, "errors": [{"check": "validator-input", "passed": False, "detail": str(error)}]}
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in report.items() if key != "checks"}, ensure_ascii=False, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
