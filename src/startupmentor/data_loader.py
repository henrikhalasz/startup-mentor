from langchain_community.document_loaders import TextLoader
from pathlib import Path
from typing import Iterable, List
from langchain.schema import Document


def load_documents(paths: Iterable[Path]) -> List[Document]:
    """Load every `.txt` file in the provided folders."""
    docs: List[Document] = []
    for folder in paths:
        for filepath in folder.glob("*.txt"):
            loader = TextLoader(str(filepath), encoding="utf-8")
            docs.extend(loader.load())
    return docs