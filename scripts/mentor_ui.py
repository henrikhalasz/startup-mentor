#!/usr/bin/env python
"""
Run with:

    streamlit run scripts/mentor_ui.py
"""

import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st

# Set page config first - must be the first Streamlit command
st.set_page_config(
    page_title="Startup Mentor",
    page_icon="🚀",
    layout="wide"
)

# Print debug information
print(f"Python path: {sys.path}")
print(f"Current directory: {os.getcwd()}")

# Add the src directory to the Python path
project_root = Path(__file__).resolve().parents[1]
src_path = str(project_root / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)
    print(f"Added {src_path} to sys.path")

load_dotenv()

# ── constants ────────────────────────────────────────────────────────────────
ROOT_DIR = Path(__file__).resolve().parents[1]
AVATAR_PATH = ROOT_DIR / "assets" / "mentor_avatar.png"

# ── local import path ────────────────────────────────────────────────────────
try:
    from startupmentor.chat import mentor_response
    print("Successfully imported mentor_response")
    
    # Try to import mentor_response_stream
    try:
        from startupmentor.chat import mentor_response_stream
        print("Successfully imported mentor_response_stream")
        USE_STREAMING = True
    except ImportError:
        print("mentor_response_stream not found in chat.py, creating a fallback implementation")
        # Fallback implementation if mentor_response_stream is not available
        def mentor_response_stream(query, history):
            """Fallback implementation that mimics streaming by yielding characters"""
            response = mentor_response(query, history)
            # Yield the response in small chunks to simulate streaming
            chunk_size = 3  # characters per chunk
            for i in range(0, len(response), chunk_size):
                yield response[i:i+chunk_size]
                # Slight delay to simulate typing
                time.sleep(0.02)
        USE_STREAMING = True
except ImportError as e:
    print(f"Error importing mentor_response: {e}")
    st.error("Failed to import mentor_response. Please check your Python path configuration.")
    USE_STREAMING = False

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

st.title("🚀 Ask Your Startup Mentor")
st.caption("Advice in the spirit of Paul Graham & Sam Altman")

if "history" not in st.session_state:
    st.session_state.history = []

# Display chat history
for user_msg, mentor_msg in st.session_state.history:
    # User message
    st.chat_message("user").markdown(user_msg)
    
    # Mentor message with avatar
    st.chat_message(
        "assistant", 
        avatar=str(AVATAR_PATH)
    ).markdown(mentor_msg)

# ── chat input ───────────────────────────────────────────────────────────────
if user_prompt := st.chat_input("Ask a startup question…"):
    # 1️⃣ display user message instantly
    st.chat_message("user").markdown(user_prompt)

    # 2️⃣ create mentor message container with avatar
    mentor_container = st.chat_message(
        "assistant",
        avatar=str(AVATAR_PATH)
    )
    mentor_placeholder = mentor_container.empty()

    if USE_STREAMING:
        try:
            # 3️⃣ call the streaming helper, updating the placeholder as we go
            partial_text = ""
            for delta in mentor_response_stream(user_prompt, st.session_state.history):
                partial_text += delta
                mentor_placeholder.markdown(partial_text)
                time.sleep(0.01)  # tiny delay to make the typing effect visible
        except Exception as e:
            # Fallback to non-streaming if there's an error
            print(f"Streaming failed, falling back to non-streaming: {str(e)}")
            response = mentor_response(user_prompt, st.session_state.history)
            mentor_placeholder.markdown(response)
            partial_text = response
    else:
        # Non-streaming fallback
        response = mentor_response(user_prompt, st.session_state.history)
        mentor_placeholder.markdown(response)
        partial_text = response

    # 4️⃣ record full turn in memory
    st.session_state.history.append((user_prompt, partial_text))
