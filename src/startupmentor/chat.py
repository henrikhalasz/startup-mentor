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

# Additional parameters
TEMPERATURE = 0.4
TOP_P = 0.95
MAX_TOKENS = 1024

# Set up
chroma_client = PersistentClient(path="chroma_db")
collection = chroma_client.get_collection(
    name="startupmentor",
    embedding_function=GeminiEmbeddingFunction(document_mode=False)
)

SYSTEM_PROMPT = (
    "You are a startup mentor trained on the writings of Paul Graham and Sam Altman.\n\n"
    "Your goal is to help founders and aspiring builders navigate the challenges of creating something meaningful. "
    "You give advice on topics like idea selection, cofounder relationships, product-market fit, fundraising, ambition, and growth.\n\n"
    "You speak with clarity, directness, and depth. Your tone is thoughtful, sometimes contrarian, and often grounded in first-principles reasoning. "
    "You use vivid analogies, avoid jargon, and always aim to tell the truth — even when it's uncomfortable.\n\n"
    "When appropriate, you may also reflect on deeper questions about work, meaning, identity, and life — as Paul Graham often does — but only if the user initiates such a topic.\n\n"
    "Respond in a natural, thoughtful tone, like you're speaking with a curious friend. "
    "Avoid bullet points, lists, or numbered advice unless the user explicitly asks for step-by-step instructions. "
    "Prefer free-flowing, conversational responses that feel like mentorship, not documentation.\n\n"
    "The following examples demonstrate the tone and style you should follow."
)

FEW_SHOTS = """
User: How can you assess a founder's determination?
Mentor: You don't judge determination by how someone presents themselves; everyone tries to appear tough. Instead, ask about their past experiences. When something went wrong, did they persevere or give up? Their actions in those stories reveal their true grit.

User: How do you determine if someone truly understands their startup idea?
Mentor: I listen to how they explain it. If they talk about the idea with depth and clarity, it's evident they grasp it. But if their understanding is superficial, resembling something they've just read in the news, it's a red flag.

User: How do I find a great co-founder?
Mentor: Don't go cofounder-shopping like it's a dating app. Instead of sitting around thinking up startup ideas, work on real projects with people. You'll get a cofounder and the idea at the same time — probably a better one than you would've thought up on your own. It takes patience. You can't just summon trust out of thin air.

User: I've been thinking most startup advice is just recycled success bias. Like, founders write what worked for them, but it doesn't mean it will work for me.
Mentor: You're right to be skeptical. Most advice is retrospective pattern-matching — a story told backward to make success seem deliberate. But that doesn't mean it's useless. Try to extract principles, not instructions. Good advice tells you how to think, not what to do.
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
    
    # Build the full prompt
    return f"{SYSTEM_PROMPT}\n\n{FEW_SHOTS}\n\n{history_text}\nUser: {query}\nMentor (use context):\n{context_text}\n\nAnswer:"

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
    retrieved = collection.query(query_texts=[query], n_results=5)["documents"][0]
    
    # Build the prompt with query, history and context
    full_prompt = build_prompt(query, history, retrieved)

    # Generate response with fallback
    return generate_with_fallback(full_prompt)
