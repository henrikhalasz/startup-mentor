#!/usr/bin/env python
"""
Run both scrapers and save clean `.txt` files into `documents/pg/` and
`documents/altman/`.  Usage:

    python scripts/scrape_and_save.py
"""
import sys
from pathlib import Path

# Make sure local package is importable when running from project root
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from startupmentor.scrapers import scrape_pg, scrape_altman  # noqa: E402

if __name__ == "__main__":
    scrape_pg()
    scrape_altman()
    print("✅  Scraping finished.")