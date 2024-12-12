"""
Main module for AI Newsletter Pipeline.
"""
import logging
from typing import List, Dict, Any
from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import pipeline components
from .data.fetch import ContentFetcher
from .data.parse import ContentParser
from .data.store import DataStore
from .embeddings.encoder import TextEncoder
from .embeddings.vectorstore import VectorStore
from .agents.summarizer_agent import SummarizerAgent
from .agents.draft_agent import DraftAgent
from .agents.factcheck_agent import FactCheckAgent
from .processing.filter import ContentFilter
from .processing.refinement import ContentRefiner
from .editing.grammar_check import GrammarChecker
from .output.formatting import NewsletterFormatter
from .output.export import NewsletterExporter

class NewsletterPipeline:
    def __init__(self):
        """Initialize the newsletter pipeline components."""
        try:
            # Initialize all components
            self.fetcher = ContentFetcher()
            self.parser = ContentParser()
            self.store = DataStore()
            self.encoder = TextEncoder()
            self.vectorstore = VectorStore()
            self.summarizer = SummarizerAgent()
            self.drafter = DraftAgent()
            self.factchecker = FactCheckAgent()
            self.filter = ContentFilter()
            self.refiner = ContentRefiner()
            self.grammar = GrammarChecker()
            self.formatter = NewsletterFormatter()
            self.exporter = NewsletterExporter()
            
            logger.info("Newsletter pipeline initialized")
        
        except Exception as e:
            logger.error(f"Error initializing pipeline: {str(e)}")
            raise

    def run(self, export_formats: List[str] = None) -> Dict[str, str]:
        """Run the complete newsletter pipeline."""
        try:
            # 1. Fetch content
            logger.info("Fetching content...")
            articles = self.fetcher.fetch_all_sources()
            self.store.save_articles(articles, "raw")
            
            # 2. Parse and clean content
            logger.info("Parsing content...")
            parsed_articles = self.parser.parse_articles(articles)
            self.store.save_articles(parsed_articles, "parsed")
            
            # 3. Generate embeddings
            logger.info("Generating embeddings...")
            encoded_articles = self.encoder.encode_articles(parsed_articles)
            self.vectorstore.add_articles(encoded_articles)
            
            # 4. Filter and rank content
            logger.info("Filtering content...")
            filtered_articles = self.filter.filter_articles(encoded_articles)
            self.store.save_articles(filtered_articles, "filtered")
            
            # 5. Summarize articles
            logger.info("Summarizing articles...")
            summarized_articles = self.summarizer.summarize_articles(filtered_articles)
            ranked_articles = self.summarizer.filter_and_rank_summaries(summarized_articles)
            
            # 6. Generate newsletter draft
            logger.info("Generating newsletter draft...")
            newsletter = self.drafter.create_newsletter(ranked_articles)
            
            # 7. Fact check content
            logger.info("Fact checking...")
            passes_validation, issues = self.factchecker.validate_newsletter(newsletter)
            if not passes_validation:
                logger.warning("Newsletter failed validation:", issues)
            
            # 8. Refine content
            logger.info("Refining content...")
            refined_newsletter = self.refiner.refine_newsletter(newsletter)
            
            # 9. Grammar check
            logger.info("Checking grammar...")
            content = refined_newsletter.get("content", "")
            corrected_content, fixes = self.grammar.fix_text(content)
            refined_newsletter["content"] = corrected_content
            
            # 10. Export newsletter
            logger.info("Exporting newsletter...")
            if export_formats is None:
                export_formats = ["markdown", "html"]
            
            exported_files = self.exporter.export_newsletter(
                refined_newsletter, 
                formats=export_formats
            )
            
            logger.info("Newsletter pipeline completed successfully")
            return exported_files
        
        except Exception as e:
            logger.error(f"Error in pipeline execution: {str(e)}")
            return {}

    def clean_up(self):
        """Clean up temporary files and old exports."""
        try:
            # Clean old exports
            self.exporter.clean_old_exports()
            
            # Clear vector store
            self.vectorstore.clear()
            
            logger.info("Clean up completed")
        
        except Exception as e:
            logger.error(f"Error during clean up: {str(e)}")

def main():
    """Main entry point for the newsletter pipeline."""
    try:
        # Check for required environment variables
        required_vars = ["GEMINI_API_KEY"]
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {missing_vars}")
        
        # Initialize and run pipeline
        pipeline = NewsletterPipeline()
        exported_files = pipeline.run()
        
        # Print results
        if exported_files:
            print("\nNewsletter generated successfully!")
            print("\nExported files:")
            for format_name, filepath in exported_files.items():
                print(f"- {format_name}: {filepath}")
        else:
            print("\nNewsletter generation failed. Check the logs for details.")
        
        # Clean up
        pipeline.clean_up()
    
    except Exception as e:
        logger.error(f"Pipeline execution failed: {str(e)}")
        raise

if __name__ == "__main__":
    main() 