"""
Embedding generation service
"""
from typing import List
import numpy as np
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
                from sentence_transformers import SentenceTransformer
                logger.info(f"Loading local embedding model: {self.model_name}")
                self.model = SentenceTransformer(self.model_name)
                logger.info("Local embedding model loaded successfully")
            elif self.provider == "openai":
                # OpenAI embeddings will be handled via API
                logger.info("Using OpenAI embeddings API")
            elif self.provider == "google":
                # Google embeddings will be handled via API
                logger.info("Using Google embeddings API")
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
            
            elif self.provider == "google":
                return self._generate_google_embeddings(texts)
            
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

    def _generate_google_embeddings(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings using Google GenAI SDK (V2)"""
        try:
            from google import genai
            from google.genai import types
            
            client = genai.Client(api_key=settings.google_api_key)
            
            embeddings = []
            for text in texts:
                result = client.models.embed_content(
                    model="gemini-embedding-001",
                    contents=text,
                    config=types.EmbedContentConfig(output_dimensionality=768)
                )
                # result.embeddings is a list of ContentEmbedding objects
                # taking the first one since we send one text at a time
                embeddings.append(result.embeddings[0].values)
            
            return np.array(embeddings, dtype=np.float32)
        except Exception as e:
            logger.error(f"Error with Google embeddings: {str(e)}")
            raise
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings"""
        if self.provider == "local":
            return self.model.get_sentence_embedding_dimension()
        elif self.provider == "openai":
            return 1536  # text-embedding-3-small dimension
        elif self.provider == "google":
            return 768  # gemini-embedding-001 dimension
        return 384  # Default


# Global instance
embedding_service = EmbeddingService()
