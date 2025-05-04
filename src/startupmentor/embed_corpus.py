"""
Public helper so a user can just run:

    from startupmentor import embed_corpus
    embed_corpus()

or execute the CLI script in `scripts/embed_documents.py`.
"""
from pathlib import Path
from typing import List

from .config import DATA_FOLDERS
from .data_loader import load_documents
from .chunker import chunk_documents
from .vector_store import get_chroma_collection, add_documents_in_batches


def embed_corpus(folders: List[Path] | None = None) -> None:
    """
    Load, chunk, embed and store the entire corpus.
    """
    folders = folders or DATA_FOLDERS
    raw_docs = load_documents(folders)

    print(f"📄 Loaded {len(raw_docs)} full documents")

    chunks = chunk_documents(raw_docs)
    print(f"🔪 Chunked into {len(chunks)} chunks")

    # Flatten to plain strings for the DB
    texts = [chunk.page_content for chunk in chunks]

    collection = get_chroma_collection()
    add_documents_in_batches(texts, collection)

    print(f"✅ Added {len(texts)} embedded chunks to collection "
          f"'{collection.name}'.")