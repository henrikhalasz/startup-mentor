from langchain.text_splitter import CharacterTextSplitter
from langchain.schema import Document
from typing import List

from .config import CHUNK_SIZE, CHUNK_OVERLAP


def chunk_documents(docs: List[Document]) -> List[Document]:
    splitter = CharacterTextSplitter(
        separator=" ",
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    return splitter.split_documents(docs)