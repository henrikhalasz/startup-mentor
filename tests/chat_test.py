import sys
import os
from pathlib import Path
from dotenv import load_dotenv
import unittest
from unittest.mock import patch, MagicMock

# Add src directory to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

# Load environment variables
load_dotenv()

from startupmentor.chat import mentor_response, build_prompt


class TestChatFunctionality(unittest.TestCase):
    """Test cases for the chat functionality in the StartupMentor application."""

    @patch('startupmentor.chat.collection')
    @patch('startupmentor.chat.gemini_client')
    def test_mentor_response(self, mock_gemini_client, mock_collection):
        # Setup mock collection.query return value
        mock_collection.query.return_value = {
            "documents": [["Sample document 1", "Sample document 2"]]
        }
        
        # Setup mock gemini_client.generate_content return value
        mock_response = MagicMock()
        mock_response.text = "This is a test response"
        mock_gemini_client.generate_content.return_value = mock_response
        
        # Test the function with a sample query
        result = mentor_response("How do I find product-market fit?")
        
        # Assertions
        self.assertEqual(result, "This is a test response")
        mock_collection.query.assert_called_once()
        mock_gemini_client.generate_content.assert_called_once()
        
    def test_build_prompt(self):
        # Test with empty history
        query = "Test query"
        history = []
        context = ["Context document 1", "Context document 2"]
        
        prompt = build_prompt(query, history, context)
        
        # Make sure the query and context are included in the prompt
        self.assertIn(query, prompt)
        self.assertIn("Context document 1", prompt)
        self.assertIn("Context document 2", prompt)
        
        # Test with history
        history = [("Previous query", "Previous response")]
        prompt_with_history = build_prompt(query, history, context)
        
        # Make sure history is included
        self.assertIn("Previous query", prompt_with_history)
        self.assertIn("Previous response", prompt_with_history)


if __name__ == "__main__":
    unittest.main() 