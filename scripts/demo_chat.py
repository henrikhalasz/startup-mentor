#!/usr/bin/env python3
"""
Simple demonstration of the StartupMentor chat functionality.
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

# Load environment variables
load_dotenv()

# Verify API key is available
if not os.environ.get("GOOGLE_API_KEY"):
    print("Error: GOOGLE_API_KEY not found in environment variables.")
    print("Make sure your .env file contains the API key.")
    sys.exit(1)

# Import the chat functionality
from startupmentor.chat import mentor_response

def main():
    """Run an interactive chat session with the startup mentor."""
    print("\n🚀 Welcome to Startup Mentor - powered by Paul Graham and Sam Altman's wisdom")
    print("📝 Type 'exit' or 'quit' to end the session\n")
    
    # Keep track of conversation history
    history = []
    
    while True:
        # Get user input
        try:
            query = input("\nYour question: ")
        except (EOFError, KeyboardInterrupt):
            print("\nThank you for using Startup Mentor! Goodbye.")
            break
        
        # Check for exit command
        if query.lower() in ["exit", "quit"]:
            print("\nThank you for using Startup Mentor! Goodbye.")
            break
            
        # Skip empty queries
        if not query.strip():
            continue
            
        try:
            print("\nThinking...")
            # Get response from the mentor
            response = mentor_response(query, history)
            
            # Save the conversation
            history.append((query, response))
            
            # Print the response
            print(f"\nMentor: {response}\n")
            
        except Exception as e:
            print(f"\nError: {e}")
            print("Something went wrong. Please try again.")

if __name__ == "__main__":
    main() 