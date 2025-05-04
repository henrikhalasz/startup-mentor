#!/usr/bin/env python
"""
Simple CLI wrapper around startupmentor.embed_corpus().
Activate your virtualenv, set GOOGLE_API_KEY, then run:

    python scripts/embed_documents.py
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Ensure local project is importable
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from startupmentor.embed_corpus import embed_corpus  # noqa: E402 (late import)

if __name__ == "__main__":
    if "GOOGLE_API_KEY" not in os.environ:
        sys.exit("❌  Set the environment variable GOOGLE_API_KEY before running. Add your own Google API key.")
    embed_corpus()