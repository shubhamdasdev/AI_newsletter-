"""
Newsletter drafting agent for AI Newsletter Pipeline.
"""
from typing import List, Dict, Any
import logging
from datetime import datetime
from .chain_init import create_newsletter_chain, create_refinement_chain, get_token_usage

logger = logging.getLogger(__name__)

class DraftAgent:
    def __init__(self):
        try:
            self.newsletter_chain = create_newsletter_chain()
            self.refinement_chain = create_refinement_chain()
            logger.info("Initialized draft agent")
        except Exception as e:
            logger.error(f"Error initializing draft agent: {str(e)}")
            raise

    @get_token_usage
    def create_initial_draft(self, formatted_summaries: str) -> str:
        """Create initial newsletter draft from formatted summaries."""
        try:
            draft = self.newsletter_chain.run(summaries=formatted_summaries)
            return draft
        except Exception as e:
            logger.error(f"Error creating initial draft: {str(e)}")
            return ""

    @get_token_usage
    def refine_draft(self, draft: str) -> str:
        """Refine the newsletter draft."""
        try:
            refined_draft = self.refinement_chain.run(content=draft)
            return refined_draft
        except Exception as e:
            logger.error(f"Error refining draft: {str(e)}")
            return draft

    def create_newsletter(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create complete newsletter from articles."""
        try:
            # Extract summaries and metadata
            article_titles = [article.get("title", "Untitled") for article in articles]
            article_urls = [article.get("url", "") for article in articles]
            
            # Create newsletter metadata
            metadata = {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "issue_number": self._generate_issue_number(),
                "article_count": len(articles),
                "sources": list(set(article_urls))
            }
            
            # Create newsletter header
            header = self._create_header(metadata)
            
            # Format summaries for the newsletter
            formatted_content = self._format_content(articles)
            
            # Create initial draft
            initial_draft = self.create_initial_draft(formatted_content)
            
            # Refine the draft
            refined_draft = self.refine_draft(initial_draft)
            
            # Create complete newsletter
            newsletter = {
                "metadata": metadata,
                "content": header + "\n\n" + refined_draft,
                "articles": articles
            }
            
            return newsletter
        
        except Exception as e:
            logger.error(f"Error creating newsletter: {str(e)}")
            return {}

    def _generate_issue_number(self) -> str:
        """Generate issue number (placeholder implementation)."""
        # In a real implementation, this would track actual issue numbers
        return f"Issue #{datetime.now().strftime('%Y%m')}"

    def _create_header(self, metadata: Dict[str, Any]) -> str:
        """Create newsletter header."""
        header = f"""# AI & Product Management Newsletter
{metadata['issue_number']} - {metadata['date']}

Welcome to this week's curated collection of insights from the worlds of AI and product management. 
We've gathered {metadata['article_count']} notable articles to keep you informed and inspired.

---
"""
        return header

    def _format_content(self, articles: List[Dict[str, Any]]) -> str:
        """Format articles into newsletter content."""
        sections = []
        
        # Group articles by category (simplified implementation)
        ai_articles = []
        product_articles = []
        other_articles = []
        
        for article in articles:
            title = article.get("title", "").lower()
            if "ai" in title or "machine learning" in title:
                ai_articles.append(article)
            elif "product" in title or "management" in title:
                product_articles.append(article)
            else:
                other_articles.append(article)
        
        # Format each section
        if ai_articles:
            sections.append("## 🤖 AI & Machine Learning\n")
            sections.extend(self._format_articles(ai_articles))
        
        if product_articles:
            sections.append("## 📊 Product Management\n")
            sections.extend(self._format_articles(product_articles))
        
        if other_articles:
            sections.append("## 🔍 Industry Insights\n")
            sections.extend(self._format_articles(other_articles))
        
        return "\n\n".join(sections)

    def _format_articles(self, articles: List[Dict[str, Any]]) -> List[str]:
        """Format a list of articles."""
        formatted = []
        for article in articles:
            formatted.append(f"""### {article.get('title', 'Untitled')}

{article.get('summary', 'No summary available')}

🔗 [Read more]({article.get('url', '#')})
""")
        return formatted 