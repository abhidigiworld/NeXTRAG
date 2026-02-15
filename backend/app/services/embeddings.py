"""
Embedding generation service
"""
from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer
from app.config import settings
from app.utils.logger import logger


class EmbeddingService:
    """Generate embeddings for text chunks"""
    
    def __init__(self):
        self.provider = settings.embedding_provider
        self.model_name = settings.embedding_model
        self.model = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize embedding model based on provider"""
        try:
            if self.provider == "local":
                logger.info(f"Loading local embedding model: {self.model_name}")
                self.model = SentenceTransformer(self.model_name)
                logger.info("Local embedding model loaded successfully")
            elif self.provider == "openai":
                # OpenAI embeddings will be handled via API
                logger.info("Using OpenAI embeddings API")
            else:
                raise ValueError(f"Unsupported embedding provider: {self.provider}")
        except Exception as e:
            logger.error(f"Error initializing embedding model: {str(e)}")
            raise
    
    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for a list of texts
        
        Args:
            texts: List of text strings
            
        Returns:
            Numpy array of embeddings
        """
        try:
            if self.provider == "local":
                embeddings = self.model.encode(
                    texts,
                    normalize_embeddings=True,
                    show_progress_bar=False
                )
                logger.info(f"Generated {len(embeddings)} embeddings")
                return embeddings
            
            elif self.provider == "openai":
                return self._generate_openai_embeddings(texts)
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            raise
    
    def _generate_openai_embeddings(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings using OpenAI API"""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=settings.openai_api_key)
            
            embeddings = []
            for text in texts:
                response = client.embeddings.create(
                    input=text,
                    model="text-embedding-3-small"
                )
                embeddings.append(response.data[0].embedding)
            
            return np.array(embeddings)
        except Exception as e:
            logger.error(f"Error with OpenAI embeddings: {str(e)}")
            raise
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings"""
        if self.provider == "local":
            return self.model.get_sentence_embedding_dimension()
        elif self.provider == "openai":
            return 1536  # text-embedding-3-small dimension
        return 384  # Default


# Global instance
embedding_service = EmbeddingService()
