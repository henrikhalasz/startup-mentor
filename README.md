# 🚀 Startup Mentor

An AI mentor for founders and builders, speaking in the style of Paul Graham and Sam Altman.

<img src="assets/mentor_avatar.png" alt="Startup Mentor" width="200"/>

## Overview

Startup Mentor is a conversational AI assistant that provides advice on startup-related topics, including idea validation, fundraising, product-market fit, team building, and growth strategies. The AI is trained on the writings and thinking patterns of Paul Graham and Sam Altman, delivering advice with a thoughtful, direct, and first-principles approach.

## Features

- 💬 Interactive chat interface with a familiar feel
- 🧠 Responses based on PG and Sam Altman's essays and thinking
- 📚 Contextual knowledge retrieval from a vector database
- ⚡ Streaming responses with typing effect
- 🖼️ Cool mentor avatar (PG and Altman's synthesis)
- 📝 Concise, focused responses (typically 70-150 words)

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/startup-mentor.git
   cd startup-mentor
   ```

2. Create a virtual environment:

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:

   Create a `.env` file with the following variables:
   ```
   GOOGLE_API_KEY=your_gemini_api_key
   ```

## Usage

Run the Streamlit UI:

```bash
streamlit run scripts/mentor_ui.py
```

## How It Works

The system consists of three main components:

1. **Vector Database**: Stores embeddings of Paul Graham and Sam Altman's essays.
2. **Retrieval System**: Finds relevant content based on user queries.
3. **Response Generation**: Generates mentor-like responses using Google's Gemini model with the clear, direct writing style of Paul Graham.

## Project Structure

```
startup-mentor/
├── assets/               # Images and static files
├── chroma_db/            # Vector database storage
├── documents/            # Raw essay documents
├── scripts/              # UI and utility scripts
│   ├── ask_mentor.py     # CLI interface
│   ├── demo_chat.py      # Demo script
│   ├── embed_documents.py# Embedding utility
│   ├── mentor_ui.py      # Streamlit web interface
│   └── scrape_and_save.py# Document collection
├── src/                  # Core functionality
│   └── startupmentor/    # Main package
│       ├── chat.py       # Chat and response generation
│       ├── embeddings.py # Vector embeddings
│       ├── config.py     # Configuration
│       └── ...           # Other modules
└── tests/                # Test cases
```

## Language Model

The system is designed to provide advice in a style reminiscent of Paul Graham's writing:
- Clear and direct language
- First-principles reasoning
- Concise delivery (typically 70-150 words)
- Focused on providing maximum insight with minimum padding
- Thoughtful advice based on startup fundamentals

## Future Improvements

- 🔊 Text-to-speech for spoken responses in a Paul Graham-inspired voice
- 📁 Document upload for business plan or pitch deck feedback
- 💾 Conversation history export
- 🌓 Light/dark mode toggle
- 📱 Mobile-responsive design

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Credits

- Vector search powered by [ChromaDB](https://github.com/chroma-core/chroma)
- LLM responses powered by [Google's Gemini](https://ai.google.dev/)
- Essays and knowledge from Paul Graham and Sam Altman's public writings

## License

[MIT](LICENSE)

---

Made with ❤️ for builders and founders everywhere




