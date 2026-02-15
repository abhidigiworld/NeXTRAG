"""
Vector store service using FAISS for similarity search
"""
import faiss
import numpy as np
import pickle
import os
from typing import List, Dict, Tuple
from datetime import datetime, timedelta
from app.config import settings
from app.utils.logger import logger


class VectorStore:
    """FAISS-based vector store with session management"""
    
    def __init__(self):
        self.sessions = {}  # session_id -> (index, metadata, last_access)
        self.dimension = None
        self.session_timeout = timedelta(minutes=settings.session_timeout_minutes)
        self.storage_dir = "vector_store"
        os.makedirs(self.storage_dir, exist_ok=True)
    
    def create_session(self, session_id: str, dimension: int):
        """
        Create a new session with a FAISS index
        
        Args:
            session_id: Unique session identifier
            dimension: Embedding dimension
        """
        if session_id not in self.sessions:
            index = faiss.IndexFlatIP(dimension)  # Inner product (cosine similarity with normalized vectors)
            self.sessions[session_id] = {
                'index': index,
                'metadata': [],
                'last_access': datetime.now()
            }
            self.dimension = dimension
            logger.info(f"Created new session: {session_id}")
    
    def add_vectors(
        self,
        session_id: str,
        vectors: np.ndarray,
        metadata: List[Dict]
    ):
        """
        Add vectors to a session's index
        
        Args:
            session_id: Session identifier
            vectors: Numpy array of vectors
            metadata: List of metadata dicts for each vector
        """
        if session_id not in self.sessions:
            self.create_session(session_id, vectors.shape[1])
        
        session = self.sessions[session_id]
        
        # Normalize vectors for cosine similarity
        faiss.normalize_L2(vectors)
        
        # Add to index
        session['index'].add(vectors)
        session['metadata'].extend(metadata)
        session['last_access'] = datetime.now()
        
        logger.info(f"Added {len(vectors)} vectors to session {session_id}")
    
    def search(
        self,
        session_id: str,
        query_vector: np.ndarray,
        top_k: int = 5
    ) -> List[Tuple[Dict, float]]:
        """
        Search for similar vectors
        
        Args:
            session_id: Session identifier
            query_vector: Query vector
            top_k: Number of results to return
            
        Returns:
            List of (metadata, score) tuples
        """
        if session_id not in self.sessions:
            logger.warning(f"Session not found: {session_id}")
            return []
        
        session = self.sessions[session_id]
        session['last_access'] = datetime.now()
        
        # Normalize query vector
        query_vector = query_vector.reshape(1, -1)
        faiss.normalize_L2(query_vector)
        
        # Search
        scores, indices = session['index'].search(query_vector, min(top_k, session['index'].ntotal))
        
        # Prepare results
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx != -1:  # Valid index
                results.append((session['metadata'][idx], float(score)))
        
        logger.info(f"Search in session {session_id} returned {len(results)} results")
        return results
    
    def get_session_stats(self, session_id: str) -> Dict:
        """Get statistics for a session"""
        if session_id not in self.sessions:
            return {'exists': False}
        
        session = self.sessions[session_id]
        return {
            'exists': True,
            'vector_count': session['index'].ntotal,
            'last_access': session['last_access'].isoformat()
        }
    
    def cleanup_expired_sessions(self):
        """Remove expired sessions"""
        now = datetime.now()
        expired = []
        
        for session_id, session in self.sessions.items():
            if now - session['last_access'] > self.session_timeout:
                expired.append(session_id)
        
        for session_id in expired:
            del self.sessions[session_id]
            logger.info(f"Cleaned up expired session: {session_id}")
        
        return len(expired)
    
    def save_session(self, session_id: str):
        """Save session to disk"""
        if session_id not in self.sessions:
            return
        
        session = self.sessions[session_id]
        session_path = os.path.join(self.storage_dir, f"{session_id}.pkl")
        
        with open(session_path, 'wb') as f:
            pickle.dump({
                'metadata': session['metadata'],
                'last_access': session['last_access']
            }, f)
        
        # Save FAISS index
        index_path = os.path.join(self.storage_dir, f"{session_id}.index")
        faiss.write_index(session['index'], index_path)
        
        logger.info(f"Saved session {session_id} to disk")
    
    def load_session(self, session_id: str) -> bool:
        """Load session from disk"""
        session_path = os.path.join(self.storage_dir, f"{session_id}.pkl")
        index_path = os.path.join(self.storage_dir, f"{session_id}.index")
        
        if not os.path.exists(session_path) or not os.path.exists(index_path):
            return False
        
        try:
            with open(session_path, 'rb') as f:
                data = pickle.load(f)
            
            index = faiss.read_index(index_path)
            
            self.sessions[session_id] = {
                'index': index,
                'metadata': data['metadata'],
                'last_access': datetime.now()
            }
            
            logger.info(f"Loaded session {session_id} from disk")
            return True
            
        except Exception as e:
            logger.error(f"Error loading session {session_id}: {str(e)}")
            return False


# Global instance
vector_store = VectorStore()
