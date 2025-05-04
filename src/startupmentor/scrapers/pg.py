"""
Scraper for Paul Graham essays (paulgraham.com).
"""
from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import urljoin

from tqdm import tqdm

from .base import clean_html_to_text, request_url, save_if_new, SLEEP_BETWEEN_REQUESTS


BASE_URL = "http://paulgraham.com/"
INDEX_URL = urljoin(BASE_URL, "articles.html")  # master list


def _extract_article_links(index_html: str) -> list[str]:
    # PG's index page uses <a href="essay.html"> inside <font> tags
    hrefs = re.findall(r'href="([a-zA-Z0-9_\-]+\.html)"', index_html)
    return [urljoin(BASE_URL, h) for h in hrefs]


def scrape_pg(output_dir: Path | str = "documents/pg") -> None:
    output_dir = Path(output_dir)
    print("🔗  Fetching Paul Graham essay index …")
    index_html = request_url(INDEX_URL)
    article_urls = _extract_article_links(index_html)
    print(f"📝  {len(article_urls)} essays found.")

    for url in tqdm(article_urls, desc="Downloading PG essays"):
        fname = url.split("/")[-1].replace(".html", ".txt")
        dest = output_dir / fname

        if dest.exists():
            continue

        html = request_url(url)
        text = clean_html_to_text(html)

        # First line as title, then blank line then body:
        title = text.split("\n", 1)[0]
        save_if_new(f"{title}\n\n{text}", dest)