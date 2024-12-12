"""
Tests for the AI Newsletter Pipeline.
"""
import pytest
from pathlib import Path
import os
from dotenv import load_dotenv
from src.main import NewsletterPipeline

# Load environment variables
load_dotenv()

@pytest.fixture
def pipeline():
    """Create a pipeline instance for testing."""
    return NewsletterPipeline()

def test_pipeline_initialization(pipeline):
    """Test that pipeline components are properly initialized."""
    assert pipeline.fetcher is not None
    assert pipeline.parser is not None
    assert pipeline.store is not None
    assert pipeline.encoder is not None
    assert pipeline.vectorstore is not None
    assert pipeline.summarizer is not None
    assert pipeline.drafter is not None
    assert pipeline.factchecker is not None
    assert pipeline.filter is not None
    assert pipeline.refiner is not None
    assert pipeline.grammar is not None
    assert pipeline.formatter is not None
    assert pipeline.exporter is not None

def test_content_fetching(pipeline):
    """Test content fetching functionality."""
    articles = pipeline.fetcher.fetch_all_sources()
    assert isinstance(articles, list)
    if articles:
        assert isinstance(articles[0], dict)
        assert "title" in articles[0]
        assert "content" in articles[0]
        assert "url" in articles[0]

def test_content_parsing(pipeline):
    """Test content parsing functionality."""
    sample_articles = [
        {
            "title": "Test Article",
            "content": "<p>This is a test article content.</p>",
            "url": "https://example.com/test"
        }
    ]
    parsed_articles = pipeline.parser.parse_articles(sample_articles)
    assert isinstance(parsed_articles, list)
    assert len(parsed_articles) == len(sample_articles)
    assert "This is a test article content." in parsed_articles[0]["content"]

def test_embedding_generation(pipeline):
    """Test embedding generation functionality."""
    sample_articles = [
        {
            "title": "Test Article",
            "content": "This is a test article content.",
            "url": "https://example.com/test"
        }
    ]
    encoded_articles = pipeline.encoder.encode_articles(sample_articles)
    assert isinstance(encoded_articles, list)
    assert "embedding" in encoded_articles[0]
    assert len(encoded_articles[0]["embedding"]) > 0

def test_newsletter_generation(pipeline):
    """Test complete newsletter generation."""
    sample_articles = [
        {
            "title": "AI Advancement",
            "content": "New developments in artificial intelligence.",
            "url": "https://example.com/ai",
            "published_date": "2023-01-01"
        },
        {
            "title": "Product Management Tips",
            "content": "Best practices for product management.",
            "url": "https://example.com/pm",
            "published_date": "2023-01-01"
        }
    ]
    
    # Process articles
    encoded_articles = pipeline.encoder.encode_articles(sample_articles)
    filtered_articles = pipeline.filter.filter_articles(encoded_articles)
    summarized_articles = pipeline.summarizer.summarize_articles(filtered_articles)
    newsletter = pipeline.drafter.create_newsletter(summarized_articles)
    
    assert isinstance(newsletter, dict)
    assert "content" in newsletter
    assert "metadata" in newsletter
    assert newsletter["metadata"]["article_count"] > 0

def test_export_functionality(pipeline, tmp_path):
    """Test newsletter export functionality."""
    # Create a simple newsletter
    newsletter = {
        "content": "# Test Newsletter\n\nThis is a test.",
        "metadata": {
            "issue_number": "TEST-001",
            "date": "2023-01-01",
            "article_count": 1
        }
    }
    
    # Export newsletter
    exported_files = pipeline.exporter.export_newsletter(
        newsletter,
        formats=["markdown", "html"]
    )
    
    assert isinstance(exported_files, dict)
    assert len(exported_files) > 0
    for filepath in exported_files.values():
        assert Path(filepath).exists()

def test_cleanup(pipeline):
    """Test cleanup functionality."""
    pipeline.clean_up()
    # Simply test that cleanup doesn't raise any exceptions
    assert True

if __name__ == "__main__":
    pytest.main([__file__]) 