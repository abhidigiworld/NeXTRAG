"""
Document processing service for extracting text from PDF, DOCX, and TXT files
"""
import os
from typing import List, Dict, Tuple
import PyPDF2
import docx
from app.utils.logger import logger
from app.config import settings


class DocumentProcessor:
    """Process and extract text from various document formats"""
    
    def __init__(self):
        self.chunk_size = settings.chunk_size
        self.chunk_overlap = settings.chunk_overlap
    
    def extract_text_from_pdf(self, file_path: str) -> List[Dict[str, any]]:
        """
        Extract text from PDF file
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            List of dicts with text and metadata
        """
        try:
            chunks = []
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                total_pages = len(pdf_reader.pages)
                
                for page_num in range(total_pages):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    
                    if text.strip():
                        chunks.append({
                            'text': text,
                            'metadata': {
                                'page': page_num + 1,
                                'total_pages': total_pages,
                                'source': os.path.basename(file_path)
                            }
                        })
            
            logger.info(f"Extracted {len(chunks)} pages from PDF: {file_path}")
            return chunks
            
        except Exception as e:
            logger.error(f"Error extracting PDF text: {str(e)}")
            raise
    
    def extract_text_from_docx(self, file_path: str) -> List[Dict[str, any]]:
        """
        Extract text from DOCX file
        
        Args:
            file_path: Path to DOCX file
            
        Returns:
            List of dicts with text and metadata
        """
        try:
            doc = docx.Document(file_path)
            chunks = []
            
            full_text = []
            for para in doc.paragraphs:
                if para.text.strip():
                    full_text.append(para.text)
            
            combined_text = '\n'.join(full_text)
            
            chunks.append({
                'text': combined_text,
                'metadata': {
                    'paragraphs': len(full_text),
                    'source': os.path.basename(file_path)
                }
            })
            
            logger.info(f"Extracted text from DOCX: {file_path}")
            return chunks
            
        except Exception as e:
            logger.error(f"Error extracting DOCX text: {str(e)}")
            raise
    
    def extract_text_from_txt(self, file_path: str) -> List[Dict[str, any]]:
        """
        Extract text from TXT file
        
        Args:
            file_path: Path to TXT file
            
        Returns:
            List of dicts with text and metadata
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
            
            chunks = [{
                'text': text,
                'metadata': {
                    'source': os.path.basename(file_path)
                }
            }]
            
            logger.info(f"Extracted text from TXT: {file_path}")
            return chunks
            
        except Exception as e:
            logger.error(f"Error extracting TXT text: {str(e)}")
            raise
    
    def process_document(self, file_path: str) -> List[Dict[str, any]]:
        """
        Process document based on file extension
        
        Args:
            file_path: Path to document
            
        Returns:
            List of text chunks with metadata
        """
        file_ext = file_path.split('.')[-1].lower()
        
        if file_ext == 'pdf':
            raw_chunks = self.extract_text_from_pdf(file_path)
        elif file_ext == 'docx':
            raw_chunks = self.extract_text_from_docx(file_path)
        elif file_ext == 'txt':
            raw_chunks = self.extract_text_from_txt(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_ext}")
        
        # Further chunk the text for better retrieval
        final_chunks = []
        for chunk in raw_chunks:
            text_chunks = self.chunk_text(chunk['text'])
            for i, text_chunk in enumerate(text_chunks):
                final_chunks.append({
                    'text': text_chunk,
                    'metadata': {
                        **chunk['metadata'],
                        'chunk_index': i,
                        'total_chunks': len(text_chunks)
                    }
                })
        
        logger.info(f"Processed document into {len(final_chunks)} chunks")
        return final_chunks
    
    def chunk_text(self, text: str) -> List[str]:
        """
        Split text into overlapping chunks
        
        Args:
            text: Text to chunk
            
        Returns:
            List of text chunks
        """
        # Simple word-based chunking
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), self.chunk_size - self.chunk_overlap):
            chunk = ' '.join(words[i:i + self.chunk_size])
            if chunk.strip():
                chunks.append(chunk)
        
        return chunks if chunks else [text]


# Global instance
document_processor = DocumentProcessor()
