from chromadb import PersistentClient
from startupmentor.embeddings import GeminiEmbeddingFunction
import google.generativeai as genai
from startupmentor.client import client as gemini_client
import os
from typing import List, Tuple

# Load .env
from dotenv import load_dotenv
load_dotenv()

# Configure model parameters
from startupmentor.config import GEMINI_MODEL_NAME as MODEL_NAME
FALLBACK_MODEL = "gemini-pro"  # Fallback model if primary isn't available

# Additional parameters - adjusted for moderately concise responses
TEMPERATURE = 0.5  # Slightly higher for more creative responses
TOP_P = 0.95
MAX_TOKENS = 800  # Increased from 350 to allow for more moderate length

# Set up
chroma_client = PersistentClient(path="chroma_db")
collection = chroma_client.get_collection(
    name="startupmentor",
    embedding_function=GeminiEmbeddingFunction(document_mode=False)
)

SYSTEM_PROMPT = (
    "You are a startup mentor who channels Paul Graham's clear, insightful writing style.\n\n"
    "IMPORTANT: Keep your responses moderately concise - aim for 100-150 words (roughly 4-8 sentences). "
    "Be concise while still delivering substantive insight and value.\n\n"
    "You speak with Paul Graham's clarity and directness. Focus on the core insight or principle, "
    "then add 1-2 supporting points or examples. Skip unnecessary pleasantries and obvious statements.\n\n"
    "Use simple language, vivid analogies when helpful, and deliver thoughtful insights efficiently. "
    "When answering, imagine Paul Graham writing a focused essay paragraph or email response.\n\n"
    "The following examples demonstrate the PG-like style and moderate conciseness you should follow."
)

FEW_SHOTS = """
User: How can you assess a founder's determination?
Mentor: Look at what they've done, not what they say. The best founders have a history of pushing through obstacles that would stop most people. Ask about specific challenges they've faced in previous projects. How did they respond when things went wrong? Did they persevere or move on? Their past behavior reveals more than any interview answer. Pay special attention to unprompted stories about overcoming resistance or solving seemingly impossible problems - these are the clearest signals of genuine determination.

User: How do you determine if someone truly understands their startup idea?
Mentor: They can explain it simply, without jargon. They know precise details - not just what they're building but exactly how it works and why users want it. When you ask unexpected questions, they respond thoughtfully rather than defensively. They can name specific people who need their product and why alternatives fall short. Most tellingly, they can articulate why they're excited enough to spend years of their life on this problem. Shallow understanding shows itself immediately through vague explanations and borrowed talking points.

User: How do I find a great co-founder?
Mentor: Don't go looking for co-founders directly - that's backward. Instead, work on interesting projects with smart people you respect. The best partnerships form naturally through collaboration on real work. You want a co-founder whose skills complement yours but whose fundamental values and work ethic align closely. Someone who makes you better and vice versa. Great co-founders often start as collaborators before the startup idea even exists. Finding the right person takes time and can't be forced - the trust necessary for co-founding is earned through shared experiences.

User: I've been thinking most startup advice is just recycled success bias.
Mentor: Much of it is. Success stories often get rewritten after the fact to seem inevitable and formulaic. But that doesn't make all advice worthless. The key is distinguishing between tactical tips (which are usually context-dependent) and principles (which transfer across situations). Good advice helps you think better, not just follow instructions. The best advisors share their reasoning process and acknowledge uncertainty, not just conclusions. Extract the underlying mental models and adapt them to your specific situation rather than copying surface-level behaviors.
"""

def build_prompt(query: str, history: List[Tuple[str, str]], context: List[str]) -> str:
    """
    Build the prompt for the LLM with the user query, conversation history, and retrieved context.
    
    Args:
        query: The current user query
        history: List of previous (question, answer) pairs
        context: Retrieved relevant documents
        
    Returns:
        Full prompt with system instructions, history, and context
    """
    # Format history if it exists, otherwise use empty string
    history_text = "\n".join([f"User: {q}\nMentor: {a}" for q, a in history[-3:]]) if history else ""
    
    # Format context documents
    context_text = "\n---\n".join(context) if context else ""
    
    # Build the full prompt with emphasis on moderate conciseness
    return f"{SYSTEM_PROMPT}\n\n{FEW_SHOTS}\n\n{history_text}\nUser: {query}\nMentor (KEEP YOUR RESPONSE TO ABOUT 100-150 WORDS, use context when relevant):\n{context_text}\n\nAnswer:"

def generate_with_fallback(prompt: str, primary_model: str = MODEL_NAME, fallback_model: str = FALLBACK_MODEL) -> str:
    """
    Generate response with fallback to a different model if the primary one fails.
    
    Args:
        prompt: The prompt to send to the model
        primary_model: The preferred model to use
        fallback_model: The fallback model to use if the primary fails
        
    Returns:
        The generated text response
    """
    try:
        # Create a GenerativeModel instance for the primary model
        model = genai.GenerativeModel(model_name=primary_model)
        
        # Generate content with the model
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
        print(f"Falling back to {fallback_model} due to error with {primary_model}: {str(e)[:100]}...")
        # Create a GenerativeModel instance for the fallback model
        fallback = genai.GenerativeModel(model_name=fallback_model)
        
        # Generate content with the fallback model
        response = fallback.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=TEMPERATURE,
                top_p=TOP_P,
                max_output_tokens=MAX_TOKENS,
            )
        )
        return response.text.strip()

def mentor_response(query: str, history: List[Tuple[str, str]] = None) -> str:
    """
    Generate a response to the user's query using retrieved context.
    
    Args:
        query: The user's question
        history: List of previous (question, answer) pairs
        
    Returns:
        The generated response text
    """
    if history is None:
        history = []
        
    # Retrieve relevant documents
    retrieved = collection.query(query_texts=[query], n_results=4)["documents"][0]  # adjusted from 3 to 4
    
    # Build the prompt with query, history and context
    full_prompt = build_prompt(query, history, retrieved)

    # Generate response with fallback
    return generate_with_fallback(full_prompt)

def mentor_response_stream(query: str, history: list[tuple[str, str]]):
    """
    Yield the mentor's reply token-by-token (or chunk-by-chunk) so the UI can
    stream it.  Falls back to non‑streaming if the account/model doesn't allow.
    """
    retrieved = collection.query(query_texts=[query], n_results=4)["documents"][0]  # adjusted from 3 to 4
    prompt     = build_prompt(query, history, retrieved)

    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

    # Try the streaming API first
    try:
        response = genai.generate_content(
            model="models/gemini-1.5-flash",
            contents=prompt,
            stream=True,                       # ← key difference
            generation_config={
                "temperature": TEMPERATURE,
                "top_p": TOP_P,
                "max_output_tokens": MAX_TOKENS,
            },
        )
        # The generator yields "chunks" with .text
        for chunk in response:
            yield chunk.text
    except Exception:
        # Fallback: one‑shot (non‑stream) then yield once
        full = mentor_response(query, history)
        yield full