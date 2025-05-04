from pathlib import Path

# Folders containing .txt files scraped from Paul Graham & Sam Altman
DATA_FOLDERS = [Path("documents/pg"), Path("documents/altman")]

# Chunking
CHUNK_SIZE = 400
CHUNK_OVERLAP = 50

# Vector store
CHROMA_DB_NAME = "startupmentor"

# Gemini models
GEMINI_MODEL_NAME = "gemini-1.5-flash"  # Model for generating responses
EMBEDDING_MODEL_NAME = "text-embedding-004"  # Model for creating embeddings