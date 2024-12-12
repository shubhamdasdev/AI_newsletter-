"""
Text embedding encoder module for AI Newsletter Pipeline.
"""
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Union, Dict, Any
import logging
from ..config.settings import EMBEDDING_MODEL

logger = logging.getLogger(__name__)

class TextEncoder:
    def __init__(self):
        try:
            self.model = SentenceTransformer(EMBEDDING_MODEL)
            logger.info(f"Loaded embedding model: {EMBEDDING_MODEL}")
        except Exception as e:
            logger.error(f"Error loading embedding model: {str(e)}")
            raise

    def encode_text(self, text: str) -> np.ndarray:
        """Encode a single text into an embedding vector."""
        try:
            return self.model.encode(text, convert_to_numpy=True)
        except Exception as e:
            logger.error(f"Error encoding text: {str(e)}")
            return np.zeros(self.model.get_sentence_embedding_dimension())

    def encode_batch(self, texts: List[str]) -> np.ndarray:
        """Encode a batch of texts into embedding vectors."""
        try:
            return self.model.encode(texts, convert_to_numpy=True)
        except Exception as e:
            logger.error(f"Error encoding batch: {str(e)}")
            return np.zeros((len(texts), self.model.get_sentence_embedding_dimension()))

    def encode_article(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """Encode an article's title and content."""
        try:
            encoded_article = article.copy()
            
            # Combine title and content for a single embedding
            combined_text = f"{article['title']} {article['content']}"
            encoded_article["embedding"] = self.encode_text(combined_text)
            
            return encoded_article
        except Exception as e:
            logger.error(f"Error encoding article: {str(e)}")
            return article

    def encode_articles(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Encode multiple articles."""
        encoded_articles = []
        for article in articles:
            encoded_article = self.encode_article(article)
            if "embedding" in encoded_article:
                encoded_articles.append(encoded_article)
        
        return encoded_articles

    def compute_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """Compute cosine similarity between two embeddings."""
        try:
            return float(np.dot(embedding1, embedding2) / 
                        (np.linalg.norm(embedding1) * np.linalg.norm(embedding2)))
        except Exception as e:
            logger.error(f"Error computing similarity: {str(e)}")
            return 0.0

    def find_similar_articles(self, 
                            query_embedding: np.ndarray, 
                            articles: List[Dict[str, Any]], 
                            top_k: int = 5) -> List[Dict[str, Any]]:
        """Find most similar articles to a query embedding."""
        try:
            similarities = []
            for article in articles:
                if "embedding" in article:
                    similarity = self.compute_similarity(query_embedding, article["embedding"])
                    similarities.append((similarity, article))
            
            # Sort by similarity and get top_k
            similarities.sort(reverse=True, key=lambda x: x[0])
            return [article for _, article in similarities[:top_k]]
        
        except Exception as e:
            logger.error(f"Error finding similar articles: {str(e)}")
            return []
 