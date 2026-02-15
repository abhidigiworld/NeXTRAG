"""
Pydantic models for request/response validation
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from enum import Enum


class DataSourceMode(str, Enum):
    """Data source modes for RAG"""
    WEB = "web"
    DOCUMENTS = "documents"
    HYBRID = "hybrid"


class Citation(BaseModel):
    """Source citation"""
    source: str = Field(..., description="Source name (URL or filename)")
    excerpt: str = Field(..., description="Relevant excerpt from source")
    relevance_score: float = Field(..., ge=0, le=1, description="Relevance score")
    source_type: Literal["web", "document"] = Field(..., description="Type of source")


class ChatRequest(BaseModel):
    """Chat request from user"""
    message: str = Field(..., min_length=1, max_length=2000, description="User question")
    mode: DataSourceMode = Field(..., description="Data source mode")
    session_id: str = Field(..., description="User session ID")
    conversation_history: Optional[List[dict]] = Field(default=[], description="Previous messages")


class ChatResponse(BaseModel):
    """Chat response to user"""
    answer: str = Field(..., description="AI-generated answer")
    citations: List[Citation] = Field(default=[], description="Source citations")
    confidence_score: float = Field(..., ge=0, le=1, description="Answer confidence")
    mode_used: DataSourceMode = Field(..., description="Mode that was used")
    sources_count: int = Field(..., description="Number of sources retrieved")


class FileUploadResponse(BaseModel):
    """File upload response"""
    filename: str = Field(..., description="Uploaded filename")
    file_id: str = Field(..., description="Unique file identifier")
    size_bytes: int = Field(..., description="File size in bytes")
    status: str = Field(..., description="Upload status")
    message: str = Field(..., description="Status message")


class FileInfo(BaseModel):
    """File information"""
    file_id: str
    filename: str
    size_bytes: int
    upload_time: str
    chunks_count: int


class ErrorResponse(BaseModel):
    """Error response"""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    code: str = Field(..., description="Error code")


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    llm_provider: str
    embedding_provider: str
    search_provider: str
