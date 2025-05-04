from __future__ import annotations

import re
import time
from pathlib import Path
from typing import Iterable, List

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; StartupMentorScraper/1.0; "
        "+https://github.com/yourrepo)"
    )
}
SLEEP_BETWEEN_REQUESTS = 0.8  # seconds


def request_url(url: str) -> str:
    """GET the URL with a polite UA & simple retry."""
    for attempt in range(3):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=20)
            resp.raise_for_status()
            return resp.text
        except (requests.HTTPError, requests.ConnectionError):
            if attempt == 2:
                raise
            time.sleep(1.5)


def clean_html_to_text(html: str) -> str:
    """Strip scripts, styles, tags and squeeze multiple blank lines."""
    soup = BeautifulSoup(html, "lxml")

    for tag in soup(["script", "style", "header", "footer", "nav"]):
        tag.decompose()

    # Get text, collapse whitespace
    text = soup.get_text("\n")
    text = re.sub(r"\r|\t", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    return text


def save_if_new(text: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if not dest.exists():
        dest.write_text(text, encoding="utf-8")