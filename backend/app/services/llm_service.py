"""
LLM service for generating responses
"""
from typing import List, Dict, Optional, Iterator
from app.config import settings
from app.utils.logger import logger


class LLMService:
    """LLM integration service supporting multiple providers"""
    
    def __init__(self):
        self.provider = settings.llm_provider
        self.model = settings.llm_model
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize LLM client based on provider"""
        try:
            if self.provider == "openai":
                from openai import OpenAI
                self.client = OpenAI(api_key=settings.openai_api_key)
                logger.info("OpenAI client initialized")
                
            elif self.provider == "anthropic":
                from anthropic import Anthropic
                self.client = Anthropic(api_key=settings.anthropic_api_key)
                logger.info("Anthropic client initialized")
                
            elif self.provider == "google":
                import google.generativeai as genai
                genai.configure(api_key=settings.google_api_key)
                self.client = genai.GenerativeModel(self.model)
                logger.info("Google AI client initialized")
                
            elif self.provider == "groq":
                from groq import Groq
                self.client = Groq(api_key=settings.groq_api_key)
                logger.info("Groq client initialized")
                
            elif self.provider == "ollama":
                # Ollama uses local HTTP API
                logger.info("Using Ollama local API")
                
            else:
                raise ValueError(f"Unsupported LLM provider: {self.provider}")
                
        except Exception as e:
            logger.error(f"Error initializing LLM client: {str(e)}")
            raise

    def refine_query(self, query: str) -> str:
        """
        Generate search-optimized keywords from user query
        Example: "Where does he belong?" -> "Address Location Residence City Country"
        """
        prompt = f"""
        You are a search optimization expert.
        User Query: "{query}"
        
        Task: Generate 3-5 specific keywords or short phrases that would likely appear in a resume or technical document to answer this query.
        
        Rules:
        1. Return ONLY the keywords/phrases separated by spaces
        2. Do not include the original query if it's vague
        3. Do not add explanations or labels
        
        Example:
        Query: "How can I contact him?"
        Output: Email Phone Mobile Contact LinkedIn GitHub Address
        """
        
        try:
            # Use the existing generate methods but with a simple system prompt
            if self.provider == "google":
                response = self.client.generate_content(prompt)
                return response.text.strip()
            elif self.provider == "openai":
                return self._generate_openai("You are a keyword generator.", prompt, None, False)
            elif self.provider == "groq":
                return self._generate_groq("You are a keyword generator.", prompt, None, False)
            else:
                # Fallback for others
                return self.generate_response(prompt, "", None, False)
        except Exception as e:
            logger.error(f"Query refinement failed: {e}")
            return query # Fallback to original query

    def filter_contexts(self, query: str, contexts: List[str]) -> List[int]:
        """
        Filter contexts based on relevance to query using LLM.
        Returns indices of relevant contexts.
        """
        if not contexts:
            return []
            
        # Prepare the prompt with numbered contexts
        context_text = ""
        for i, ctx in enumerate(contexts):
            context_text += f"\n--- CHUNK {i} ---\n{ctx[:300]}...\n"
            
        prompt = f"""
        Task: Identify which of the following text chunks are relevant to answering the query: "{query}"
        
        Chunks:
        {context_text}
        
        Instructions:
        1. Analyze each chunk's relevance to the query.
        2. Return ONLY the numbers (indices) of the relevant chunks, separated by commas.
        3. If a chunk is garbage or irrelevant, ignore it.
        4. If unsure, err on the side of including it.
        5. Return "ALL" if all are good, or "NONE" if none are relevant.
        
        Example Output: 0, 2, 4
        """
        
        try:
            response_text = ""
            if self.provider == "google":
                response = self.client.generate_content(prompt)
                response_text = response.text.strip()
            elif self.provider == "openai":
                response_text = self._generate_openai("You are a relevance filter.", prompt, None, False)
            elif self.provider == "groq":
                response_text = self._generate_groq("You are a relevance filter.", prompt, None, False)
            else:
                return list(range(len(contexts))) # Fallback
                
            # Parse response
            if "NONE" in response_text.upper():
                return []
            if "ALL" in response_text.upper():
                return list(range(len(contexts)))
                
            # Extract numbers
            import re
            indices = [int(n) for n in re.findall(r'\d+', response_text)]
            
            # Validate indices
            valid_indices = [i for i in indices if 0 <= i < len(contexts)]
            return list(set(valid_indices)) # Unique sorted
            
        except Exception as e:
            logger.error(f"Context filtering failed: {e}")
            return list(range(len(contexts))) # Fallback to keeping all
    
    def generate_response(
        self,
        prompt: str,
        context: str,
        conversation_history: Optional[List[Dict]] = None,
        stream: bool = False
    ) -> str:
        """
        Generate response from LLM
        
        Args:
            prompt: User question
            context: Retrieved context
            conversation_history: Previous messages
            stream: Whether to stream response
            
        Returns:
            Generated response
        """
        # Construct the full prompt with grounding instructions
        system_message = """You are a helpful AI assistant. You must answer questions ONLY based on the provided context.

CRITICAL RULES:
1. Answer ONLY using information from the provided context
2. If the context doesn't contain enough information to answer the question, say: "I cannot find reliable information in the selected data source to answer this question."
3. Always cite your sources by mentioning which source the information came from
4. Be concise and accurate
5. Do not make up information or use knowledge outside the provided context"""

        user_message = f"""Context:
{context}

Question: {prompt}

Please provide a well-structured answer based ONLY on the context above. Include citations to your sources."""

        try:
            if self.provider == "openai":
                return self._generate_openai(system_message, user_message, conversation_history, stream)
            elif self.provider == "anthropic":
                return self._generate_anthropic(system_message, user_message, conversation_history, stream)
            elif self.provider == "google":
                return self._generate_google(system_message, user_message, conversation_history, stream)
            elif self.provider == "groq":
                return self._generate_groq(system_message, user_message, conversation_history, stream)
            elif self.provider == "ollama":
                return self._generate_ollama(system_message, user_message, conversation_history, stream)
                
        except Exception as e:
            logger.error(f"Error generating LLM response: {str(e)}")
            raise
    
    def _generate_openai(
        self,
        system_message: str,
        user_message: str,
        conversation_history: Optional[List[Dict]],
        stream: bool
    ) -> str:
        """Generate response using OpenAI"""
        messages = [{"role": "system", "content": system_message}]
        
        if conversation_history:
            messages.extend(conversation_history[-5:])  # Last 5 messages
        
        messages.append({"role": "user", "content": user_message})
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.1,
            max_tokens=1000,
            stream=stream
        )
        
        if stream:
            return response  # Return generator for streaming
        else:
            return response.choices[0].message.content
    
    def _generate_anthropic(
        self,
        system_message: str,
        user_message: str,
        conversation_history: Optional[List[Dict]],
        stream: bool
    ) -> str:
        """Generate response using Anthropic"""
        messages = []
        
        if conversation_history:
            messages.extend(conversation_history[-5:])
        
        messages.append({"role": "user", "content": user_message})
        
        response = self.client.messages.create(
            model=self.model,
            system=system_message,
            messages=messages,
            temperature=0.1,
            max_tokens=1000
        )
        
        return response.content[0].text
    
    def _generate_google(
        self,
        system_message: str,
        user_message: str,
        conversation_history: Optional[List[Dict]],
        stream: bool
    ) -> str:
        """Generate response using Google AI"""
        try:
            full_prompt = f"{system_message}\n\n{user_message}"
            response = self.client.generate_content(full_prompt)
            
            # Handle the response based on the new API format
            if hasattr(response, 'text'):
                return response.text
            elif hasattr(response, 'parts'):
                return response.parts[0].text
            elif hasattr(response, 'candidates'):
                return response.candidates[0].content.parts[0].text
            else:
                logger.error(f"Unexpected Gemini response format: {response}")
                return "I apologize, but I encountered an error generating a response."
        except Exception as e:
            logger.error(f"Gemini API error: {str(e)}")
            raise
    
    def _generate_ollama(
        self,
        system_message: str,
        user_message: str,
        conversation_history: Optional[List[Dict]],
        stream: bool
    ) -> str:
        """Generate response using Ollama"""
        import requests
        
        messages = [{"role": "system", "content": system_message}]
        
        if conversation_history:
            messages.extend(conversation_history[-5:])
        
        messages.append({"role": "user", "content": user_message})
        
        response = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": self.model,
                "messages": messages,
                "stream": False
            }
        )
        
        return response.json()["message"]["content"]

    def _generate_groq(
        self,
        system_message: str,
        user_message: str,
        conversation_history: Optional[List[Dict]],
        stream: bool
    ) -> str:
        """Generate response using Groq"""
        messages = [{"role": "system", "content": system_message}]
        
        if conversation_history:
            messages.extend(conversation_history[-5:])
        
        messages.append({"role": "user", "content": user_message})
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.1,
            max_tokens=1000,
            stream=stream
        )
        
        if stream:
            return response
        else:
            return response.choices[0].message.content


# Global instance
llm_service = LLMService()
