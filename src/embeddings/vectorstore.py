"""
Vector store module for AI Newsletter Pipeline.
"""
from typing import List, Dict, Any
import numpy as np
from annoy import AnnoyIndex
import logging
import json
from pathlib import Path
from ..config.settings import VECTOR_DB_PATH

logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self):
        """Initialize the vector store."""
        try:
            self.vector_dimension = 384  # Default for all-MiniLM-L6-v2
            self.index = AnnoyIndex(self.vector_dimension, 'angular')
            self.metadata = {}
            self.current_id = 0
            self.index_path = Path(VECTOR_DB_PATH) / "articles.ann"
            self.metadata_path = Path(VECTOR_DB_PATH) / "metadata.json"
            
            # Create directory if it doesn't exist
            self.index_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Load existing index if available
            if self.index_path.exists() and self.metadata_path.exists():
                self.load()
            
            logger.info("Initialized vector store")
        
        except Exception as e:
            logger.error(f"Error initializing vector store: {str(e)}")
            raise

    def add_articles(self, articles: List[Dict[str, Any]]) -> None:
        """Add articles to the vector store."""
        try:
            for article in articles:
                if "embedding" not in article:
                    logger.warning(f"Article missing embedding, skipping: {article.get('title', 'Unknown')}")
                    continue
                
                # Add vector to index
                self.index.add_item(self.current_id, article["embedding"])
                
                # Store metadata
                self.metadata[self.current_id] = {
                    "title": article.get("title", ""),
                    "url": article.get("url", ""),
                    "content": article.get("content", ""),
                    "published_date": article.get("published_date", ""),
                    "source": article.get("source", "")
                }
                
                self.current_id += 1
            
            # Build index after adding all vectors
            self.index.build(10)  # 10 trees for better accuracy
            self.save()
            
            logger.info(f"Added {len(articles)} articles to vector store")
        
        except Exception as e:
            logger.error(f"Error adding articles to vector store: {str(e)}")

    def search(self, query_vector: np.ndarray, k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar articles."""
        try:
            # Get nearest neighbors
            indices, distances = self.index.get_nns_by_vector(
                query_vector, k, include_distances=True
            )
            
            # Get metadata for results
            results = []
            for idx, dist in zip(indices, distances):
                if idx in self.metadata:
                    result = self.metadata[idx].copy()
                    result["similarity"] = 1 - (dist / 2)  # Convert angular distance to similarity
                    results.append(result)
            
            return results
        
        except Exception as e:
            logger.error(f"Error searching vector store: {str(e)}")
            return []

    def save(self) -> None:
        """Save the index and metadata to disk."""
        try:
            # Save index
            self.index.save(str(self.index_path))
            
            # Save metadata
            with open(self.metadata_path, 'w') as f:
                json.dump(self.metadata, f)
            
            logger.info("Saved vector store to disk")
        
        except Exception as e:
            logger.error(f"Error saving vector store: {str(e)}")

    def load(self) -> None:
        """Load the index and metadata from disk."""
        try:
            # Load index
            self.index.load(str(self.index_path))
            
            # Load metadata
            with open(self.metadata_path, 'r') as f:
                self.metadata = json.load(f)
            
            # Update current_id
            if self.metadata:
                self.current_id = max(map(int, self.metadata.keys())) + 1
            
            logger.info("Loaded vector store from disk")
        
        except Exception as e:
            logger.error(f"Error loading vector store: {str(e)}")

    def clear(self) -> None:
        """Clear the vector store."""
        try:
            self.index = AnnoyIndex(self.vector_dimension, 'angular')
            self.metadata = {}
            self.current_id = 0
            
            # Remove files if they exist
            if self.index_path.exists():
                self.index_path.unlink()
            if self.metadata_path.exists():
                self.metadata_path.unlink()
            
            logger.info("Cleared vector store")
        
        except Exception as e:
            logger.error(f"Error clearing vector store: {str(e)}") 