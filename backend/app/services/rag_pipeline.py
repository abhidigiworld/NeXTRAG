"""
RAG Pipeline - Main orchestration for Retrieval-Augmented Generation
"""
from typing import List, Dict, Tuple
from app.models.schemas import DataSourceMode, Citation
from app.services.web_search import web_search_service
from app.services.document_processor import document_processor
from app.services.embeddings import embedding_service
from app.services.vector_store import vector_store
from app.services.llm_service import llm_service
from app.config import settings
from app.utils.logger import logger
import numpy as np


class RAGPipeline:
    """Main RAG orchestration pipeline"""
    
    def __init__(self):
        self.top_k = settings.top_k_results
        self.similarity_threshold = settings.similarity_threshold
    
    async def process_query(
        self,
        query: str,
        mode: DataSourceMode,
        session_id: str,
        conversation_history: List[Dict] = None
    ) -> Tuple[str, List[Citation], float]:
        """
        Process a user query through the RAG pipeline
        
        Args:
            query: User question
            mode: Data source mode
            session_id: User session ID
            conversation_history: Previous conversation messages
            
        Returns:
            Tuple of (answer, citations, confidence_score)
        """
        logger.info(f"Processing query in {mode} mode: {query[:50]}...")
        
        # Step 1: Retrieve context based on mode
        if mode == DataSourceMode.WEB:
            context, citations = await self._retrieve_from_web(query, session_id)
        elif mode == DataSourceMode.DOCUMENTS:
            logger.info(f"Document mode - using session_id: {session_id}")
            context, citations = await self._retrieve_from_documents(query, session_id)
        elif mode == DataSourceMode.HYBRID:
            context, citations = await self._retrieve_hybrid(query, session_id)
        else:
            raise ValueError(f"Unsupported mode: {mode}")
        
        # Step 2: Check if we have sufficient context
        if not context or len(context) < 50:
            logger.warning(f"Insufficient context: length={len(context) if context else 0}")
            return (
                "I cannot find reliable information in the selected data source to answer this question.",
                [],
                0.0
            )
        
        logger.info(f"Context built successfully: {len(context)} characters, {len(citations)} citations")
        
        # Step 3: Generate response using LLM
        try:
            logger.info("Calling LLM service to generate response...")
            answer = llm_service.generate_response(
                prompt=query,
                context=context,
                conversation_history=conversation_history,
                stream=False
            )
            logger.info(f"LLM response received: {len(answer)} characters")
        except Exception as e:
            logger.error(f"LLM generation failed: {str(e)}")
            return (
                "I apologize, but I encountered an error generating a response. Please try again.",
                citations,
                0.0
            )
        
        # Step 4: Calculate confidence score
        confidence = self._calculate_confidence(citations)
        
        logger.info(f"Generated answer with confidence {confidence:.2f}")
        return answer, citations, confidence
    
    async def _retrieve_from_web(
        self,
        query: str,
        session_id: str
    ) -> Tuple[str, List[Citation]]:
        """Retrieve context from web search"""
        # Rewrite query for better results
        enhanced_query = web_search_service.rewrite_query(query)
        
        # Search the web
        search_results = web_search_service.search(enhanced_query, self.top_k)
        
        if not search_results:
            return "", []
        
        # Extract content from URLs
        all_chunks = []
        citations = []
        
        for result in search_results:
            content = web_search_service.extract_content_from_url(result['url'])
            if content:
                # Chunk the content
                chunks = document_processor.chunk_text(content)
                
                for chunk in chunks[:3]:  # Top 3 chunks per source
                    all_chunks.append({
                        'text': chunk,
                        'metadata': {
                            'source': result['url'],
                            'title': result['title'],
                            'source_type': 'web'
                        }
                    })
        
        # Generate embeddings and search
        if all_chunks:
            texts = [chunk['text'] for chunk in all_chunks]
            embeddings = embedding_service.generate_embeddings(texts)
            
            # Create temporary session for web results
            web_session_id = f"{session_id}_web"
            vector_store.create_session(web_session_id, embeddings.shape[1])
            
            # Add text to metadata for later retrieval
            metadata_with_text = []
            for chunk in all_chunks:
                meta = chunk['metadata'].copy()
                meta['text'] = chunk['text']  # Store the actual text in metadata
                metadata_with_text.append(meta)
            
            vector_store.add_vectors(
                web_session_id,
                embeddings,
                metadata_with_text
            )
            
            # Search for relevant chunks
            query_embedding = embedding_service.generate_embeddings([query])
            results = vector_store.search(web_session_id, query_embedding[0], self.top_k)
            
            # Filter by similarity threshold
            filtered_results = [
                (metadata, score) for metadata, score in results
                if score >= self.similarity_threshold
            ]
            
            # Build context and citations
            context_parts = []
            for metadata, score in filtered_results:
                # Use the actual text from metadata, not texts[0]
                chunk_text = metadata.get('text', '')
                context_parts.append(f"Source: {metadata['title']}\n{chunk_text[:500]}")
                
                citations.append(Citation(
                    source=metadata['source'],
                    excerpt=chunk_text[:200],
                    relevance_score=score,
                    source_type='web'
                ))
            
            context = "\n\n".join(context_parts)
            return context, citations
        
        return "", []
    
    async def _retrieve_from_documents(
        self,
        query: str,
        session_id: str
    ) -> Tuple[str, List[Citation]]:
        """Retrieve context from uploaded documents"""
        # Check if session has documents
        stats = vector_store.get_session_stats(session_id)
        logger.info(f"Session stats for {session_id}: exists={stats['exists']}, vectors={stats.get('vector_count', 0)}")
        
        if not stats['exists'] or stats['vector_count'] == 0:
            logger.warning(f"No documents found for session {session_id}")
            return "", []
        
        # Search in document vectors
        # ENHANCEMENT: Refine query using LLM
        refined_terms = llm_service.refine_query(query)
        logger.info(f"Refining document query: '{query}' -> +'{refined_terms}'")
        
        # Combine original query with refined terms for broader search coverage
        expanded_query = f"{query} {refined_terms}"
        
        query_embedding = embedding_service.generate_embeddings([expanded_query])
        results = vector_store.search(session_id, query_embedding[0], self.top_k)
        
        # Filter by similarity threshold
        logger.info(f"Raw results scores: {[score for _, score in results]}, threshold: {self.similarity_threshold}")
        filtered_results = [
            (metadata, score) for metadata, score in results
            if score >= self.similarity_threshold
        ]
        logger.info(f"Filtered results count: {len(filtered_results)} (from {len(results)} total)")
        
        if not filtered_results:
            logger.warning(f"All results filtered out by similarity threshold {self.similarity_threshold}")
            logger.warning(f"Insufficient context: length=0")
            return "", []
            
        # ENHANCEMENT: Context Filtering (Reranking)
        # Extract texts for filtering
        chunk_texts = [m.get('text', '') for m, _ in filtered_results]
        
        # Ask LLM which chunks are relevant
        logger.info("Applying LLM-based context filtering...")
        kept_indices = llm_service.filter_contexts(query, chunk_texts)
        logger.info(f"LLM kept {len(kept_indices)}/{len(filtered_results)} chunks")
        
        # Keep only relevant results
        final_results = [filtered_results[i] for i in kept_indices]
        
        # Build Context and Citations
        context_parts = []
        citations = []
        
        for metadata, score in final_results:
            text = metadata.get('text', '')
            source = metadata.get('source', 'Unknown')
            page = metadata.get('page', 1)
            
            context_parts.append(f"Source: {source} (Page {page})\n{text}")
            
            citations.append(Citation(
                source=source,
                excerpt=text[:200] + "...",
                relevance_score=float(score),
                source_type='document'
            ))
            
        context = "\n\n".join(context_parts)
        return context, citations

    async def _retrieve_hybrid(self, query: str, session_id: str) -> Tuple[str, List[Citation]]:
        """
        Context-Aware Hybrid Search:
        1. Search documents first to find entities (GitHub, LinkedIn, projects)
        2. Refine web search query based on found entities
        3. Combine results
        """
        # Step 1: Search documents
        doc_results = []
        if session_id:
            logger.info("Hybrid search started - Refining query for document lookup...")
            refined_doc_terms = llm_service.refine_query(query)
            expanded_doc_query = f"{query} {refined_doc_terms}"
            
            query_embedding = embedding_service.generate_embeddings([expanded_doc_query])
            search_results = vector_store.search(session_id, query_embedding[0], self.top_k)
            
            # Filter and extract text
            filtered_doc_results = [
                (metadata, score) for metadata, score in search_results
                if score >= self.similarity_threshold
            ]
            
            # ENHANCEMENT: Filter Documents
            if filtered_doc_results:
                doc_texts = [m.get('text', '') for m, _ in filtered_doc_results]
                kept_doc_indices = llm_service.filter_contexts(query, doc_texts)
                logger.info(f"Hybrid: Kept {len(kept_doc_indices)}/{len(filtered_doc_results)} doc chunks")
                doc_results = [filtered_doc_results[i] for i in kept_doc_indices]
            
        # Step 2: Analyze document content for entities (URLs)
        refined_web_query = query
        found_entities = []
        
        import re
        # Regex for GitHub and LinkedIn URLs
        github_pattern = r'(https?://github\.com/[a-zA-Z0-9-]+(?:/[a-zA-Z0-9_.-]+)?)'
        linkedin_pattern = r'(https?://(?:www\.)?linkedin\.com/in/[a-zA-Z0-9-]+)'
        
        # Check texts for entities (using original results for entity extraction to be safe)
        all_text = " ".join([m.get('text', '') for m, _ in search_results[:3]]) # Check top 3 raw results
        
        github_matches = re.findall(github_pattern, all_text)
        linkedin_matches = re.findall(linkedin_pattern, all_text)
        
        unique_entities = list(set(github_matches + linkedin_matches))
        
        if unique_entities:
            found_entities = unique_entities
            logger.info(f"Found entities in documents: {found_entities}")
            # Append entities to query
            refined_web_query = f"{query} {' '.join(found_entities)}"
            logger.info(f"Refined web search query with entities: {refined_web_query}")
        else:
            logger.info("No entities found in documents, using original query")

        # Step 3: Web Search with Refined Query
        web_results = web_search_service.search(refined_web_query, self.top_k) # Use refined query
        
        # ENHANCEMENT: Filter Web Results
        # Web results are dicts with 'content' key
        if web_results:
            web_texts = [r.get('content', '') for r in web_results]
            kept_web_indices = llm_service.filter_contexts(query, web_texts)
            logger.info(f"Hybrid: Kept {len(kept_web_indices)}/{len(web_results)} web chunks")
            web_results = [web_results[i] for i in kept_web_indices]

        # Step 4: Build Contexts
        doc_context_parts = []
        doc_citations = []
        
        for metadata, score in doc_results:
            text = metadata.get('text', '')
            source = metadata.get('source', 'Unknown')
            page = metadata.get('page', 1)
            
            doc_context_parts.append(f"Source: {source} (Page {page})\n{text}")
            
            doc_citations.append(Citation(
                source=source,
                excerpt=text[:200] + "...",
                relevance_score=float(score),
                source_type='document'
            ))
            
        doc_context = "\n\n".join(doc_context_parts)
        
        web_context_parts = []
        web_citations = []
        
        for result in web_results:
            text = result.get('content', '')
            url = result.get('url', 'Unknown')
            
            web_context_parts.append(f"Source: {url}\n{text}")
            
            # Mock score for web results if not present
            score = result.get('score', 0.5)
            
            web_citations.append(Citation(
                source=url,
                excerpt=text[:200] + "...",
                relevance_score=float(score),
                source_type='web'
            ))
            
        web_context = "\n\n".join(web_context_parts)
        
        # Step 5: Combine Contexts
        full_context = f"""
        Information from Uploaded Documents:
        {doc_context}
        
        Information from Web Search:
        {web_context}
        """
        
        all_citations = doc_citations + web_citations
        
        # Sort and take top_k citations
        all_citations.sort(key=lambda x: x.relevance_score, reverse=True)
        top_citations = all_citations[:self.top_k]

        return full_context, top_citations
    

    
    def _calculate_confidence(self, citations: List[Citation]) -> float:
        """Calculate confidence score based on citations"""
        if not citations:
            return 0.0
        
        # Use MAXIMUM relevance score instead of average
        # If we found even ONE good chunk, we should be confident!
        max_score = max(c.relevance_score for c in citations)
        
        # Boost if we have multiple supporting chunks
        # e.g., if we have 3 results, boost by 0.1
        count_bonus = min(len(citations) * 0.05, 0.2)
        
        confidence = min(max_score * 2.5 + count_bonus, 1.0) # Scale up the embedding score (usually 0.2-0.5) to a loose 0-1 range
        return confidence
    
    async def process_document_upload(
        self,
        file_path: str,
        session_id: str
    ) -> Dict:
        """
        Process an uploaded document
        
        Args:
            file_path: Path to uploaded file
            session_id: User session ID
            
        Returns:
            Processing result with chunk count
        """
        logger.info(f"Processing document: {file_path}")
        
        # Extract and chunk text
        chunks = document_processor.process_document(file_path)
        
        if not chunks:
            raise ValueError("No text extracted from document")
        
        # Generate embeddings
        texts = [chunk['text'] for chunk in chunks]
        embeddings = embedding_service.generate_embeddings(texts)
        
        # Store in vector database
        dimension = embedding_service.get_embedding_dimension()
        vector_store.create_session(session_id, dimension)
        
        # Add text to metadata
        metadata = []
        for chunk, text in zip(chunks, texts):
            chunk['metadata']['text'] = text
            metadata.append(chunk['metadata'])
        
        vector_store.add_vectors(session_id, embeddings, metadata)
        
        logger.info(f"Processed {len(chunks)} chunks from document")
        
        return {
            'chunks_count': len(chunks),
            'status': 'success'
        }


# Global instance
rag_pipeline = RAGPipeline()
