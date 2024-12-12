# AI-Driven Newsletter Pipeline

An intelligent newsletter generation system that automatically curates, summarizes, and formats content from various AI and product management sources. The pipeline uses Google's Gemini AI for content generation and modern NLP techniques for content processing.

## Features

- **Multi-Source Content Aggregation**: Automatically fetches content from:
  - AI Articles (TowardsDataScience, ArXiv, MIT Technology Review)
  - Product Management Resources (ProductPlan, Mind the Product, The Product Manager)
  - General Technology News (Wired AI, VentureBeat, TechCrunch)

- **Intelligent Processing Pipeline**:
  - Content fetching and parsing with BeautifulSoup4
  - Text embeddings using Sentence Transformers
  - Vector similarity search with Annoy
  - Content summarization and drafting using Google's Gemini AI
  - Grammar checking with Language Tool
  - Automated formatting and export

## Technical Stack

- **Core Dependencies**:
  - `langchain` & `langchain-google-genai` for LLM operations
  - `google-generativeai` for Gemini AI integration
  - `sentence-transformers` for text embeddings
  - `annoy` for efficient vector similarity search
  - `beautifulsoup4` for web scraping
  - `language-tool-python` for grammar checking

## Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and add your API keys:
   ```
   GEMINI_API_KEY=your_gemini_api_key_here
   NEWS_API_KEY=your_news_api_key_here
   ```

## Project Structure

```
project_root/
├─ src/
│  ├─ config/          # Configuration settings
│  ├─ data/            # Data fetching and storage
│  ├─ embeddings/      # Text embedding and vector storage
│  ├─ agents/          # LangChain agents for content generation
│  ├─ processing/      # Content filtering and refinement
│  ├─ editing/         # Grammar and style checking
│  ├─ output/          # Newsletter formatting and export
│  └─ main.py         # Pipeline orchestration
├─ tests/             # Test suite
├─ requirements.txt   # Project dependencies
└─ .env.example      # Environment variables template
```

## Usage

Run the pipeline:
```bash
python -m src.main
```

The generated newsletter will be exported in both Markdown and HTML formats in the `output` directory.

## Configuration

Key settings can be adjusted in `src/config/settings.py`:
- Content sources and categories
- Model parameters (temperature, token limits)
- Newsletter formatting preferences
- Vector store settings

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License - feel free to use this project for your own newsletter automation needs.

