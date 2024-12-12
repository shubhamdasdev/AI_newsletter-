"""
Content filtering module for AI Newsletter Pipeline.
"""
from typing import List, Dict, Any
import logging
from datetime import datetime, timedelta
from ..config.settings import NEWSLETTER_SETTINGS

logger = logging.getLogger(__name__)

class ContentFilter:
    def __init__(self):
        self.relevance_threshold = NEWSLETTER_SETTINGS["relevance_threshold"]
        self.max_articles = NEWSLETTER_SETTINGS["max_articles"]

    def filter_articles(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter articles based on multiple criteria."""
        try:
            filtered_articles = articles
            
            # Apply filters in sequence
            filtered_articles = self.filter_by_date(filtered_articles)
            filtered_articles = self.filter_by_relevance(filtered_articles)
            filtered_articles = self.filter_duplicates(filtered_articles)
            filtered_articles = self.limit_articles(filtered_articles)
            
            logger.info(f"Filtered {len(articles)} articles down to {len(filtered_articles)}")
            return filtered_articles
        
        except Exception as e:
            logger.error(f"Error filtering articles: {str(e)}")
            return []

    def filter_by_date(self, articles: List[Dict[str, Any]], 
                      max_age_days: int = 7) -> List[Dict[str, Any]]:
        """Filter articles by publication date."""
        try:
            cutoff_date = datetime.now() - timedelta(days=max_age_days)
            recent_articles = []
            
            for article in articles:
                pub_date_str = article.get("published_date")
                if not pub_date_str:
                    continue
                
                try:
                    pub_date = datetime.fromisoformat(pub_date_str.replace('Z', '+00:00'))
                    if pub_date >= cutoff_date:
                        recent_articles.append(article)
                except ValueError:
                    logger.warning(f"Invalid date format: {pub_date_str}")
                    continue
            
            return recent_articles
        
        except Exception as e:
            logger.error(f"Error filtering by date: {str(e)}")
            return articles

    def filter_by_relevance(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter articles by relevance score."""
        try:
            relevant_articles = []
            
            for article in articles:
                # Check if article has embedding (indicates it was processed)
                if "embedding" not in article:
                    continue
                
                # Calculate basic relevance score
                score = self._calculate_relevance_score(article)
                
                if score >= self.relevance_threshold:
                    article["relevance_score"] = score
                    relevant_articles.append(article)
            
            # Sort by relevance score
            relevant_articles.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
            return relevant_articles
        
        except Exception as e:
            logger.error(f"Error filtering by relevance: {str(e)}")
            return articles

    def filter_duplicates(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate or very similar articles."""
        try:
            unique_articles = []
            seen_titles = set()
            
            for article in articles:
                title = article.get("title", "").lower()
                url = article.get("url", "")
                
                # Skip if we've seen this title or URL
                if title in seen_titles or not title:
                    continue
                
                # Check for very similar titles
                similar_exists = False
                for seen_title in seen_titles:
                    if self._calculate_similarity(title, seen_title) > 0.8:
                        similar_exists = True
                        break
                
                if not similar_exists:
                    seen_titles.add(title)
                    unique_articles.append(article)
            
            return unique_articles
        
        except Exception as e:
            logger.error(f"Error filtering duplicates: {str(e)}")
            return articles

    def limit_articles(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Limit the number of articles to the maximum allowed."""
        return articles[:self.max_articles]

    def _calculate_relevance_score(self, article: Dict[str, Any]) -> float:
        """Calculate a relevance score for an article."""
        try:
            score = 0.0
            
            # Keywords in title
            title = article.get("title", "").lower()
            keywords = ["ai", "machine learning", "deep learning", "product management",
                       "agile", "innovation", "technology"]
            
            for keyword in keywords:
                if keyword in title:
                    score += 0.2
            
            # Length of content (prefer medium-length articles)
            content = article.get("content", "")
            word_count = len(content.split())
            if 500 <= word_count <= 2000:
                score += 0.3
            
            # Has technical details
            if "technical" in content.lower() or "algorithm" in content.lower():
                score += 0.2
            
            # Recent publication date
            pub_date_str = article.get("published_date")
            if pub_date_str:
                try:
                    pub_date = datetime.fromisoformat(pub_date_str.replace('Z', '+00:00'))
                    days_old = (datetime.now() - pub_date).days
                    if days_old <= 2:
                        score += 0.3
                    elif days_old <= 5:
                        score += 0.2
                except ValueError:
                    pass
            
            return min(1.0, score)
        
        except Exception as e:
            logger.error(f"Error calculating relevance score: {str(e)}")
            return 0.0

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts using a simple approach."""
        try:
            # Convert to sets of words
            words1 = set(text1.lower().split())
            words2 = set(text2.lower().split())
            
            # Calculate Jaccard similarity
            intersection = len(words1.intersection(words2))
            union = len(words1.union(words2))
            
            return intersection / union if union > 0 else 0.0
        
        except Exception as e:
            logger.error(f"Error calculating text similarity: {str(e)}")
            return 0.0 