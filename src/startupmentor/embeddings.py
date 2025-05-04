import google.generativeai as genai
from chromadb import Documents, EmbeddingFunction, Embeddings
import os

from .config import EMBEDDING_MODEL_NAME


class GeminiEmbeddingFunction(EmbeddingFunction):
    """
    Make Gemini's text‑embedding‑004 work with ChromaDB.

    Notes
    -----
    * The current google‑generativeai client (≥ 0.4) returns a *dict*:
        {'embedding': [...], 'token_count': …, …}
      Earlier versions returned an object with `.embeddings`.
    * We embed each document individually; Chroma batches at a higher level.
    """

    def __init__(self, *, document_mode: bool = True):
        super().__init__()
        self.document_mode = document_mode

    # --------------------------------------------------------------------- #
    # Required signature for Chroma's EmbeddingFunction
    # --------------------------------------------------------------------- #
    def __call__(self, input: Documents) -> Embeddings:  # type: ignore[override]
        genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
        task = "retrieval_document" if self.document_mode else "retrieval_query"
        vectors: list[list[float]] = []

        for doc in input:
            resp = genai.embed_content(
                model=EMBEDDING_MODEL_NAME,
                content=doc,
                task_type=task,
            )

            # Newer client: single vector under "embedding"
            if "embedding" in resp:
                vectors.append(resp["embedding"])
            # Future‑proof: maybe a list of embeddings
            elif "embeddings" in resp:
                vectors.extend(
                    e["values"] if isinstance(e, dict) and "values" in e else e
                    for e in resp["embeddings"]
                )
            else:
                raise RuntimeError("Unexpected Gemini embedding response shape")

        return vectors
