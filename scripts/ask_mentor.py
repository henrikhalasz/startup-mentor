#!/usr/bin/env python
"""
CLI chat with a Paul‑Graham‑+‑Sam‑Altman‑style mentor (RAG‑powered).

   $ python scripts/ask_mentor.py
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()                                   # pulls GOOGLE_API_KEY from .env

# -- make local src/ importable ------------------------------------------------
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import google.generativeai as genai
from startupmentor.client import client as gemini_client
from chromadb import PersistentClient
from startupmentor.embeddings import GeminiEmbeddingFunction

# ────────────────────────────────────────────
# Basic config
# ────────────────────────────────────────────
DB_PATH          = "chroma_db"
COLLECTION_NAME  = "startupmentor"
K_RETRIEVE       = 5           # chunks sent as context each turn
HISTORY_TURNS    = 4           # how many past Q&A pairs to keep
MODEL_NAME       = "gemini-1.5-flash"    # primary model
FALLBACK_MODEL   = "gemini-pro"          # fallback model
TEMPERATURE      = 0.65
TOP_P            = 0.9
MAX_TOKENS       = 1024

SYSTEM_PROMPT = (
    "You are a startup mentor trained on the writings of Paul Graham and "
    "Sam Altman.\n\n"
    "Your goal is to help founders and aspiring builders navigate the challenges "
    "of creating something meaningful. You give advice on topics like idea "
    "selection, co‑founder relationships, product‑market fit, fundraising, "
    "ambition, and growth.\n\n"
    "You speak with clarity, directness, and depth. Your tone is thoughtful, "
    "sometimes contrarian, and often grounded in first‑principles reasoning. "
    "You use vivid analogies, avoid jargon, and always aim to tell the truth — "
    "even when it's uncomfortable.\n\n"
    "When appropriate, you may also reflect on deeper questions about work, "
    "meaning, identity, and life — as Paul Graham often does — but only if the "
    "user initiates such a topic.\n\n"
    "Respond in a natural, thoughtful tone, like you're speaking with a curious "
    "friend. Avoid bullet points unless the user explicitly asks for step‑by‑step "
    "instructions. Prefer free‑flowing, conversational responses that feel like "
    "mentorship, not documentation."
)

FEW_SHOT_EXAMPLES = """
User: How can you assess a founder's determination?
Mentor: You don't judge determination by how someone presents themselves; everyone tries to appear tough. Instead, ask about their past experiences. When something went wrong, did they persevere or give up? Their actions in those stories reveal their true grit.

User: I've been thinking most startup advice is just recycled success bias.
Mentor: You're right to be skeptical. Most advice is retrospective pattern‑matching — a story told backward to make success seem deliberate. But that doesn't mean it's useless. Try to extract principles, not instructions. Good advice tells you how to think, not what to do.
"""

# ────────────────────────────────────────────
# Set up Chroma collection and embedding fn
# ────────────────────────────────────────────
chroma_client = PersistentClient(path=DB_PATH)
collection = chroma_client.get_collection(
    name=COLLECTION_NAME,
    embedding_function=GeminiEmbeddingFunction(document_mode=False)
)

# Memory of past turns
conversation: list[tuple[str, str]] = []   # (user, mentor)

# ────────────────────────────────────────────
# Helper: build the full prompt
# ────────────────────────────────────────────
def build_prompt(user_query: str, retrieved_chunks: list[str]) -> str:
    # 1) last few turns
    history_text = ""
    for u, m in conversation[-HISTORY_TURNS:]:
        history_text += f"User: {u}\nMentor: {m}\n"

    # 2) context from Chroma
    context = "\n---\n".join(retrieved_chunks)

    return (
        f"{SYSTEM_PROMPT}\n\n"
        f"{FEW_SHOT_EXAMPLES}\n\n"
        f"{history_text}"
        f"User: {user_query}\n"
        f"Mentor (use the following documents as supporting context):\n"
        f"{context}\n\n"
        f"Answer:"
    )

# ────────────────────────────────────────────
# Helper: Generate response with fallback
# ────────────────────────────────────────────
def generate_with_fallback(prompt, primary_model=MODEL_NAME, fallback_model=FALLBACK_MODEL):
    try:
        # Create a primary model instance
        model = genai.GenerativeModel(model_name=primary_model)
        
        # Generate the response
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=TEMPERATURE,
                top_p=TOP_P,
                max_output_tokens=MAX_TOKENS,
            )
        )
        return response.text.strip()
    except Exception as e:
        print(f"\nFalling back to {fallback_model} due to: {str(e)[:100]}...")
        # Create a fallback model instance
        fallback = genai.GenerativeModel(model_name=fallback_model)
        
        # Generate with fallback model
        response = fallback.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=TEMPERATURE,
                top_p=TOP_P,
                max_output_tokens=MAX_TOKENS,
            )
        )
        return response.text.strip()

# ────────────────────────────────────────────
# Chat loop
# ────────────────────────────────────────────
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
print(
    "Mentor: Hi, I'm the love child of Paul Graham and Sam Altman.\n"
    "Ask me anything about startups. Type 'exit' to quit.\n"
)

while True:
    try:
        user_input = input("You: ")
    except (EOFError, KeyboardInterrupt):
        break

    if user_input.strip().lower() in {"exit", "quit"}:
        break

    # 1) retrieve relevant chunks
    res = collection.query(query_texts=[user_input], n_results=K_RETRIEVE)
    retrieved_docs = res["documents"][0]

    # 2) build prompt
    full_prompt = build_prompt(user_input, retrieved_docs)

    # 3) call Gemini with fallback
    mentor_reply = generate_with_fallback(full_prompt)

    # 4) store in memory
    conversation.append((user_input, mentor_reply))

    # 5) show reply
    print("\nMentor:\n" + mentor_reply + "\n")
