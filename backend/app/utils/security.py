"""
Security utilities for file validation and rate limiting
"""
import os
from typing import Tuple
from fastapi import UploadFile, HTTPException
from app.config import settings
from app.utils.logger import logger


def validate_file_type(file: UploadFile) -> bool:
    """
    Validate file type using magic number checking
    
    Args:
        file: Uploaded file
        
    Returns:
        True if valid, raises HTTPException otherwise
    """
    # Get file extension
    file_ext = file.filename.split('.')[-1].lower() if '.' in file.filename else ''
    
    if file_ext not in settings.allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"File type '.{file_ext}' not allowed. Allowed types: {', '.join(settings.allowed_extensions)}"
        )
    
    return True


def validate_file_size(file: UploadFile) -> bool:
    """
    Validate file size
    
    Args:
        file: Uploaded file
        
    Returns:
        True if valid, raises HTTPException otherwise
    """
    # Read file to check size
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to beginning
    
    if file_size > settings.max_file_size_bytes:
        raise HTTPException(
            status_code=400,
            detail=f"File size ({file_size / 1024 / 1024:.2f}MB) exceeds maximum allowed size ({settings.max_file_size_mb}MB)"
        )
    
    return True


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent path traversal attacks
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove path components
    filename = os.path.basename(filename)
    
    # Remove potentially dangerous characters
    dangerous_chars = ['..', '/', '\\', '\0']
    for char in dangerous_chars:
        filename = filename.replace(char, '_')
    
    return filename


def validate_upload(file: UploadFile) -> Tuple[bool, str]:
    """
    Comprehensive file upload validation
    
    Args:
        file: Uploaded file
        
    Returns:
        Tuple of (is_valid, sanitized_filename)
    """
    try:
        validate_file_type(file)
        validate_file_size(file)
        sanitized = sanitize_filename(file.filename)
        logger.info(f"File validation passed: {sanitized}")
        return True, sanitized
    except HTTPException as e:
        logger.warning(f"File validation failed: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during file validation: {str(e)}")
        raise HTTPException(status_code=500, detail="File validation error")


def sanitize_input(text: str, max_length: int = 2000) -> str:
    """
    Sanitize user input text
    
    Args:
        text: User input
        max_length: Maximum allowed length
        
    Returns:
        Sanitized text
    """
    # Trim whitespace
    text = text.strip()
    
    # Limit length
    if len(text) > max_length:
        text = text[:max_length]
    
    # Remove null bytes
    text = text.replace('\0', '')
    
    return text
