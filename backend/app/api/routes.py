"""
API routes for SmartRAG AI
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import StreamingResponse
from typing import List
import os
import uuid
from datetime import datetime

from app.models.schemas import (
    ChatRequest, ChatResponse, FileUploadResponse,
    FileInfo, ErrorResponse, DataSourceMode
)
from app.services.rag_pipeline import rag_pipeline
from app.services.vector_store import vector_store
from app.utils.security import validate_upload, sanitize_input
from app.utils.logger import logger
from app.config import settings

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint
    
    Args:
        request: Chat request with message, mode, and session_id
        
    Returns:
        Chat response with answer and citations
    """
    try:
        # Sanitize input
        sanitized_message = sanitize_input(request.message)
        
        # Process query through RAG pipeline
        answer, citations, confidence = await rag_pipeline.process_query(
            query=sanitized_message,
            mode=request.mode,
            session_id=request.session_id,
            conversation_history=request.conversation_history
        )
        
        return ChatResponse(
            answer=answer,
            citations=citations,
            confidence_score=confidence,
            mode_used=request.mode,
            sources_count=len(citations)
        )
        
    except Exception as e:
        logger.error(f"Chat endpoint error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    session_id: str = Form(...)
):
    """
    Upload and process a document
    
    Args:
        file: Uploaded file
        session_id: User session ID
        
    Returns:
        Upload confirmation with file info
    """
    try:
        logger.info(f"Upload endpoint called with session_id: {session_id}")
        
        # Validate file
        is_valid, sanitized_filename = validate_upload(file)
        
        # Generate unique file ID
        file_id = str(uuid.uuid4())
        file_extension = sanitized_filename.split('.')[-1]
        unique_filename = f"{file_id}.{file_extension}"
        
        # Save file
        file_path = os.path.join(settings.upload_dir, unique_filename)
        
        with open(file_path, 'wb') as f:
            content = await file.read()
            f.write(content)
        
        file_size = len(content)
        
        # Process document
        result = await rag_pipeline.process_document_upload(file_path, session_id)
        
        logger.info(f"File uploaded and processed: {sanitized_filename}")
        
        return FileUploadResponse(
            filename=sanitized_filename,
            file_id=file_id,
            size_bytes=file_size,
            status="success",
            message=f"Processed {result['chunks_count']} chunks"
        )
        
    except Exception as e:
        logger.error(f"Upload endpoint error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/files/{session_id}")
async def list_files(session_id: str):
    """
    List uploaded files for a session
    
    Args:
        session_id: User session ID
        
    Returns:
        Session statistics
    """
    try:
        stats = vector_store.get_session_stats(session_id)
        return stats
        
    except Exception as e:
        logger.error(f"List files error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/files/{session_id}")
async def clear_session(session_id: str):
    """
    Clear all files for a session
    
    Args:
        session_id: User session ID
        
    Returns:
        Success message
    """
    try:
        if session_id in vector_store.sessions:
            del vector_store.sessions[session_id]
            logger.info(f"Cleared session: {session_id}")
        
        return {"status": "success", "message": "Session cleared"}
        
    except Exception as e:
        logger.error(f"Clear session error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "llm_provider": settings.llm_provider,
        "embedding_provider": settings.embedding_provider,
        "search_provider": settings.search_provider
    }
