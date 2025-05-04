import sys
import os
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

# Load .env
load_dotenv()
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

from chromadb import PersistentClient
from startupmentor.embeddings import GeminiEmbeddingFunction

client = PersistentClient(path="chroma_db")  # Make sure this folder exists!
print("✅ Available collections:", client.list_collections())

collection = client.get_collection(
    name="startupmentor",
    embedding_function=GeminiEmbeddingFunction()
)

print("✅ Chunk count:", collection.count())
print("✅ API KEY:", os.environ.get("GOOGLE_API_KEY"))