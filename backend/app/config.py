"""
Configuration management for SmartRAG AI
"""
from pydantic_settings import BaseSettings
from typing import Literal
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # API Keys
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    google_api_key: str = ""
    groq_api_key: str = ""
    tavily_api_key: str = ""
    serpapi_key: str = ""
    
    # LLM Configuration
    llm_provider: Literal["openai", "anthropic", "google", "ollama", "groq"] = "groq"
    llm_model: str = "llama-3.3-70b-versatile"
    
    # Embedding Configuration
    embedding_provider: Literal["openai", "local"] = "local"
    embedding_model: str = "all-MiniLM-L6-v2"
    
    # Search Configuration
    search_provider: Literal["tavily", "serpapi", "duckduckgo"] = "duckduckgo"
    
    # File Upload Settings
    max_file_size_mb: int = 10
    allowed_file_types: str = "pdf,docx,txt"
    upload_dir: str = "uploads"
    
    # RAG Settings
    chunk_size: int = 500
    chunk_overlap: int = 50
    top_k_results: int = 5
    similarity_threshold: float = 0.7
    session_timeout_minutes: int = 30
    
    # Rate Limiting
    rate_limit_per_minute: int = 10
    
    # CORS
    frontend_url: str = "http://localhost:3000"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    @property
    def allowed_extensions(self) -> set:
        """Get allowed file extensions as a set"""
        return set(self.allowed_file_types.split(","))
    
    @property
    def max_file_size_bytes(self) -> int:
        """Get max file size in bytes"""
        return self.max_file_size_mb * 1024 * 1024
    
    def validate_api_keys(self):
        """Validate that required API keys are set based on provider choices"""
        if self.llm_provider == "openai" and not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required when using OpenAI as LLM provider")
        if self.llm_provider == "anthropic" and not self.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY is required when using Anthropic as LLM provider")
        if self.llm_provider == "google" and not self.google_api_key:
            raise ValueError("GOOGLE_API_KEY is required when using Google as LLM provider")
        if self.embedding_provider == "openai" and not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required when using OpenAI embeddings")
        if self.search_provider == "tavily" and not self.tavily_api_key:
            raise ValueError("TAVILY_API_KEY is required when using Tavily search")
        if self.search_provider == "serpapi" and not self.serpapi_key:
            raise ValueError("SERPAPI_KEY is required when using SerpAPI search")
        if self.llm_provider == "groq" and not self.groq_api_key:
            raise ValueError("GROQ_API_KEY is required when using Groq as LLM provider")


# Global settings instance
settings = Settings()

# Create upload directory if it doesn't exist
os.makedirs(settings.upload_dir, exist_ok=True)
