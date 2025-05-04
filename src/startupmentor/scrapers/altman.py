"""
Scraper for Sam Altman’s blog (blog.samaltman.com) that follows every paginated
index page (/?page=N) to collect all posts. Uses the fast `lxml` parser.
"""
from __future__ import annotations

import re
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup, FeatureNotFound
from tqdm import tqdm

from .base import (
    clean_html_to_text,
    request_url,
    save_if_new,
    SLEEP_BETWEEN_REQUESTS,
)

BASE_URL = "https://blog.samaltman.com/"


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────
def _soup(html: str) -> BeautifulSoup:
    """Return a BeautifulSoup object with `lxml`, fall back to builtin parser."""
    try:
        return BeautifulSoup(html, "lxml")
    except FeatureNotFound:
        return BeautifulSoup(html, "html.parser")


def _extract_post_links_from_page(html: str) -> list[str]:
    """Given one index page’s HTML, return absolute URLs of blog posts."""
    soup = _soup(html)
    anchors = soup.select("a.post-link, h2 a, a.blog-item-link")
    links = [urljoin(BASE_URL, a["href"]) for a in anchors if a.get("href")]
    links = [u for u in links if urlparse(u).path.strip("/")]
    return links


def _collect_all_post_links(max_pages: int = 30) -> list[str]:
    """Iterate /?page=N until no new links appear (or max_pages reached)."""
    links: set[str] = set()
    for p in range(1, max_pages + 1):
        page_url = f"{BASE_URL}?page={p}"
        html = request_url(page_url)
        page_links = _extract_post_links_from_page(html)

        new_links = [u for u in page_links if u not in links]
        if not new_links:
            break

        links.update(new_links)
        time.sleep(SLEEP_BETWEEN_REQUESTS)

    return sorted(links)


# ──────────────────────────────────────────────────────────────────────────────
# Public entry point
# ──────────────────────────────────────────────────────────────────────────────
def scrape_altman(output_dir: Path | str = "documents/altman") -> None:
    """
    Download every Sam Altman blog post as plain text into `output_dir`.
    Existing files are skipped.
    """
    output_dir = Path(output_dir)
    print("🔗  Fetching Sam Altman blog index …")
    article_urls = _collect_all_post_links()
    print(f"📝  {len(article_urls)} posts found.")

    for url in tqdm(article_urls, desc="Downloading Altman posts"):
        slug = re.sub(r"[\\/*?\"<>|]", "", url.rstrip("/").split("/")[-1] or "index")
        dest = output_dir / f"{slug}.txt"
        if dest.exists():
            continue

        html = request_url(url)
        text = clean_html_to_text(html)

        title = text.split("\n", 1)[0]
        save_if_new(f"{title}\n\n{text}", dest)
