"""
Article summarization agent for AI Newsletter Pipeline.
"""
from typing import List, Dict, Any
import logging
from .chain_init import create_summarization_chain, get_token_usage
from ..config.settings import NEWSLETTER_SETTINGS

logger = logging.getLogger(__name__)

class SummarizerAgent:
    def __init__(self):
        try:
            self.chain = create_summarization_chain()
            logger.info("Initialized summarizer agent")
        except Exception as e:
            logger.error(f"Error initializing summarizer agent: {str(e)}")
            raise

    @get_token_usage
    def summarize_article(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """Summarize a single article."""
        try:
            # Extract article content
            title = article.get("title", "")
            content = article.get("content", "")
            
            if not title or not content:
                logger.warning("Article missing title or content")
                return article
            
            # Generate summary
            summary = self.chain.run(title=title, content=content)
            
            # Add summary to article
            article_with_summary = article.copy()
            article_with_summary["summary"] = summary
            
            return article_with_summary
        
        except Exception as e:
            logger.error(f"Error summarizing article: {str(e)}")
            return article

    def summarize_articles(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Summarize multiple articles."""
        summarized_articles = []
        
        for article in articles:
            try:
                summarized_article = self.summarize_article(article)
                if "summary" in summarized_article:
                    summarized_articles.append(summarized_article)
            except Exception as e:
                logger.error(f"Error in article summarization batch: {str(e)}")
                continue
        
        return summarized_articles

    def filter_and_rank_summaries(self, 
                                articles: List[Dict[str, Any]], 
                                max_articles: int = NEWSLETTER_SETTINGS["max_articles"]) -> List[Dict[str, Any]]:
        """Filter and rank summarized articles based on relevance and quality."""
        try:
            # Basic ranking based on summary length and keyword presence
            ranked_articles = []
            
            for article in articles:
                if "summary" not in article:
                    continue
                
                # Calculate basic score
                score = 0
                summary = article["summary"]
                
                # Length score (prefer medium-length summaries)
                length = len(summary.split())
                if 100 <= length <= 300:
                    score += 1
                
                # Keyword score
                keywords = ["AI", "machine learning", "deep learning", "product", 
                          "management", "innovation", "technology"]
                for keyword in keywords:
                    if keyword.lower() in summary.lower():
                        score += 0.5
                
                # Technical detail score
                if "Technical Details:" in summary:
                    score += 1
                
                ranked_articles.append((score, article))
            
            # Sort by score and get top articles
            ranked_articles.sort(reverse=True, key=lambda x: x[0])
            top_articles = [article for _, article in ranked_articles[:max_articles]]
            
            return top_articles
        
        except Exception as e:
            logger.error(f"Error filtering and ranking summaries: {str(e)}")
            return articles[:max_articles]

    def format_summaries_for_newsletter(self, articles: List[Dict[str, Any]]) -> str:
        """Format summarized articles for newsletter input."""
        try:
            formatted_summaries = []
            
            for i, article in enumerate(articles, 1):
                summary = f"""
                ## {i}. {article.get('title', 'Untitled')}
                
                {article.get('summary', 'No summary available')}
                
                Source: {article.get('url', 'No URL available')}
                """
                formatted_summaries.append(summary)
            
            return "\n\n".join(formatted_summaries)
        
        except Exception as e:
            logger.error(f"Error formatting summaries: {str(e)}")
            return "Error formatting summaries for newsletter" 