#!/usr/bin/env python
"""
Package the ChromaDB database for Streamlit Cloud deployment.

This script extracts the essential data from the ChromaDB database 
and converts it into a format that can be easily loaded in 
Streamlit Cloud without depending on ChromaDB's persistent storage.

Run this before deploying to create the packaged data file.
"""

import os
import sys
import json
import pickle
import shutil
from pathlib import Path

# Add the src directory to the Python path
project_root = Path(__file__).resolve().parents[1]
src_path = str(project_root / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)
    print(f"Added {src_path} to sys.path")

from chromadb import PersistentClient
from startupmentor.embeddings import GeminiEmbeddingFunction

# Path to the ChromaDB database
DB_PATH = project_root / "chroma_db"
# Path to save the packaged data
OUTPUT_PATH = project_root / "streamlit_data"
# Output file
OUTPUT_FILE = OUTPUT_PATH / "packaged_documents.json"

def package_documents():
    """
    Extract and package documents from the ChromaDB database.
    """
    print(f"Connecting to ChromaDB at {DB_PATH}")
    
    try:
        # Initialize ChromaDB client
        client = PersistentClient(path=str(DB_PATH))
        # Get the collection
        collection = client.get_collection(
            name="startupmentor",
            embedding_function=GeminiEmbeddingFunction(document_mode=False)
        )
        
        # Get all documents (limit to 1000 for safety)
        result = collection.get(limit=1000)
        
        # Create output directory if it doesn't exist
        os.makedirs(OUTPUT_PATH, exist_ok=True)
        
        # Extract documents, ids, and metadata
        packaged_data = {
            "documents": result["documents"],
            "ids": result["ids"],
            "metadatas": result["metadatas"]
        }
        
        # Save to JSON file
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(packaged_data, f, ensure_ascii=False, indent=2)
        
        print(f"Successfully packaged {len(result['documents'])} documents")
        print(f"Saved to {OUTPUT_FILE}")
        
        # Create a small sample file with just a few documents for testing
        sample_size = min(10, len(result["documents"]))
        sample_data = {
            "documents": result["documents"][:sample_size],
            "ids": result["ids"][:sample_size],
            "metadatas": result["metadatas"][:sample_size]
        }
        
        sample_file = OUTPUT_PATH / "sample_documents.json"
        with open(sample_file, 'w', encoding='utf-8') as f:
            json.dump(sample_data, f, ensure_ascii=False, indent=2)
        
        print(f"Also created sample file with {sample_size} documents at {sample_file}")
        
    except Exception as e:
        print(f"Error packaging documents: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    package_documents()
    print("Done!") 