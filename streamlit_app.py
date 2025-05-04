#!/usr/bin/env python
"""
Startup Mentor - PG & Sam Altman-style startup advice
This is a simplified deployment version for Streamlit Cloud.
"""

import os
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

# Configure page
st.set_page_config(
    page_title="Startup Mentor",
    page_icon="🚀",
    layout="wide"
)

# Setup constants
ROOT_DIR = Path(__file__).resolve().parent
AVATAR_PATH = ROOT_DIR / "assets" / "mentor_avatar.png"

# Configure Gemini
try:
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        st.error("No Google API key found. Please set the GOOGLE_API_KEY environment variable.")
        st.stop()
    
    genai.configure(api_key=api_key)
    MODEL = "gemini-1.5-flash"
    TEMPERATURE = 0.5
    MAX_TOKENS = 800
except Exception as e:
    st.error(f"Error configuring Gemini: {str(e)}")
    st.stop()

# System prompt
SYSTEM_PROMPT = (
    "You are a startup mentor who channels Paul Graham's clear, insightful writing style.\n\n"
    "IMPORTANT: Keep your responses moderately concise - aim for 100-150 words (roughly 4-8 sentences). "
    "Be concise while still delivering substantive insight and value.\n\n"
    "You speak with Paul Graham's clarity and directness. Focus on the core insight or principle, "
    "then add 1-2 supporting points or examples. Skip unnecessary pleasantries and obvious statements.\n\n"
    "Use simple language, vivid analogies when helpful, and deliver thoughtful insights efficiently. "
    "When answering, imagine Paul Graham writing a focused essay paragraph or email response."
)

# Session state
if "history" not in st.session_state:
    st.session_state.history = []

# Custom CSS for better styling
st.markdown("""
    <style>
    .chat-message {
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        align-items: flex-start;
    }
    .chat-message.user {
        background-color: #f0f2f6;
        margin-left: 20%;
    }
    .chat-message.mentor {
        background-color: #e6f3ff;
        margin-right: 20%;
    }
    .avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        margin-right: 1rem;
    }
    .message-content {
        flex: 1;
    }
    </style>
""", unsafe_allow_html=True)

# Page content
st.title("🚀 Ask Your Startup Mentor")
st.caption("Advice in the style of Paul Graham & Sam Altman")

# Display chat history
for user_msg, mentor_msg in st.session_state.history:
    # User message
    st.chat_message("user").markdown(user_msg)
    
    # Mentor message with avatar
    st.chat_message(
        "assistant", 
        avatar=str(AVATAR_PATH) if os.path.exists(AVATAR_PATH) else None
    ).markdown(mentor_msg)

# Simplified mentor response function
def mentor_response_stream(prompt, history=[]):
    history_text = "\n".join([f"User: {q}\nMentor: {a}" for q, a in history[-3:]]) if history else ""
    full_prompt = f"{SYSTEM_PROMPT}\n\n{history_text}\nUser: {prompt}\nMentor (KEEP YOUR RESPONSE TO ABOUT 100-150 WORDS):\n\nAnswer:"
    
    try:
        response = genai.GenerativeModel(MODEL).generate_content(
            full_prompt,
            stream=True,
            generation_config={
                "temperature": TEMPERATURE,
                "top_p": 0.95,
                "max_output_tokens": MAX_TOKENS,
            }
        )
        
        for chunk in response:
            # Break down the chunk into smaller pieces for better typing effect
            text = chunk.text
            if len(text) > 3:
                for i in range(0, len(text), 3):
                    yield text[i:i+3]
                    # Add a tiny delay between mini-chunks
                    import time
                    time.sleep(0.02)
            else:
                yield text
    except Exception as e:
        yield f"I'm sorry, I encountered an error: {str(e)}"

# Chat input and response
if user_prompt := st.chat_input("Ask a startup question…"):
    # Display user message
    st.chat_message("user").markdown(user_prompt)

    # Create mentor message container
    mentor_container = st.chat_message(
        "assistant",
        avatar=str(AVATAR_PATH) if os.path.exists(AVATAR_PATH) else None
    )
    mentor_placeholder = mentor_container.empty()

    # Generate response with streaming
    try:
        partial_text = ""
        for delta in mentor_response_stream(user_prompt, st.session_state.history):
            partial_text += delta
            mentor_placeholder.markdown(partial_text)
    except Exception as e:
        st.error(f"Error generating response: {str(e)}")
        partial_text = f"I apologize, but I'm having trouble generating a response right now."
        mentor_placeholder.markdown(partial_text)

    # Record conversation in history
    st.session_state.history.append((user_prompt, partial_text)) 