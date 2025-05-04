import chromadb
from tqdm import tqdm
from typing import Sequence

from .embeddings import GeminiEmbeddingFunction
from .config import CHROMA_DB_NAME


def get_chroma_collection() -> chromadb.Collection:
    """
    Return (and create, if needed) the Chroma collection pre‑configured
    with the Gemini embedding function.
    """
    embed_fn = GeminiEmbeddingFunction(document_mode=True)
    client = chromadb.PersistentClient(path="chroma_db")
    return client.get_or_create_collection(
        name=CHROMA_DB_NAME,
        embedding_function=embed_fn,
    )


def add_documents_in_batches(
    docs: Sequence[str],
    collection: chromadb.Collection,
    batch_size: int = 100,
) -> None:
    from tqdm import tqdm

    for start in tqdm(
        range(0, len(docs), batch_size),
        desc="Embedding & adding chunks",
        unit="batch"
    ):
        batch = docs[start:start + batch_size]
        batch_ids = [str(i) for i in range(start, start + len(batch))]

        # Get already added IDs
        existing_ids = set(collection.get(ids=batch_ids, include=[]).get("ids", []))
        to_add = [(doc, doc_id) for doc, doc_id in zip(batch, batch_ids) if doc_id not in existing_ids]

        if not to_add:
            continue

        new_docs, new_ids = zip(*to_add)
        collection.add(documents=list(new_docs), ids=list(new_ids))