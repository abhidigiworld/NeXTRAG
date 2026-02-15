# SmartRAG AI

A production-ready full-stack Retrieval-Augmented Generation (RAG) AI assistant with dynamic data source selection.

## Features

- **Dynamic Data Source Selection**: Choose between Web Search, Uploaded Documents, or Hybrid mode
- **Multi-Format Document Support**: PDF, DOCX, and TXT files
- **Web Search Integration**: Real-time web search with content extraction
- **Vector-Based Retrieval**: FAISS vector database for efficient similarity search
- **Multiple LLM Providers**: Support for OpenAI, Anthropic, Google, and Ollama
- **Grounded Responses**: AI answers strictly based on retrieved context
- **Source Citations**: Every answer includes source references with relevance scores
- **Confidence Scoring**: Transparency in answer quality
- **Modern UI**: Beautiful dark mode interface with glassmorphism effects
- **File Upload**: Drag-and-drop support for documents
- **Conversation Memory**: Maintains context from recent messages

## Tech Stack

### Backend
- **FastAPI**: High-performance Python web framework
- **FAISS**: Vector similarity search
- **Sentence Transformers**: Local embedding generation
- **PyPDF2 & python-docx**: Document processing
- **DuckDuckGo/Tavily/SerpAPI**: Web search providers
- **OpenAI/Anthropic/Google/Ollama**: LLM providers

### Frontend
- **Next.js 14**: React framework with App Router
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first styling
- **Framer Motion**: Smooth animations
- **React Markdown**: Message rendering
- **Axios**: API communication

## Project Structure

```
SmartRAG-AI/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── config.py            # Configuration management
│   │   ├── models/schemas.py    # Pydantic models
│   │   ├── services/            # Core services
│   │   │   ├── document_processor.py
│   │   │   ├── web_search.py
│   │   │   ├── embeddings.py
│   │   │   ├── vector_store.py
│   │   │   ├── llm_service.py
│   │   │   └── rag_pipeline.py
│   │   ├── api/routes.py        # API endpoints
│   │   └── utils/               # Utilities
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── app/                 # Next.js app
│   │   ├── components/          # React components
│   │   ├── hooks/               # Custom hooks
│   │   └── types/               # TypeScript types
│   ├── package.json
│   └── tsconfig.json
└── README.md
```

## Setup Instructions

### Prerequisites

- Python 3.9+
- Node.js 18+
- npm or yarn

### Backend Setup

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Mac/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your API keys:
   ```env
   # Choose your LLM provider
   LLM_PROVIDER=openai
   OPENAI_API_KEY=your_key_here
   
   # Choose your search provider (duckduckgo is free)
   SEARCH_PROVIDER=duckduckgo
   
   # Embedding provider (local is free)
   EMBEDDING_PROVIDER=local
   ```

5. **Run the backend**:
   ```bash
   python -m app.main
   ```
   
   Backend will run on `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Run the development server**:
   ```bash
   npm run dev
   ```
   
   Frontend will run on `http://localhost:3000`

## Usage

1. **Open your browser** to `http://localhost:3000`

2. **Select a data source mode**:
   - **Web Search**: Ask questions about current events or general knowledge
   - **Documents**: Upload files and ask questions about their content
   - **Hybrid**: Combine both web and document sources

3. **Upload documents** (optional):
   - Click the upload icon in the header
   - Drag and drop or browse for PDF, DOCX, or TXT files
   - Wait for processing to complete

4. **Start chatting**:
   - Type your question in the input box
   - Press Enter or click Send
   - View the AI's response with source citations and confidence score

## API Endpoints

- `POST /api/chat` - Send a chat message
- `POST /api/upload` - Upload a document
- `GET /api/files/{session_id}` - List uploaded files
- `DELETE /api/files/{session_id}` - Clear session files
- `GET /api/health` - Health check

## Configuration Options

### LLM Providers

- **OpenAI**: `LLM_PROVIDER=openai`, `LLM_MODEL=gpt-4-turbo-preview`
- **Anthropic**: `LLM_PROVIDER=anthropic`, `LLM_MODEL=claude-3-sonnet-20240229`
- **Google**: `LLM_PROVIDER=google`, `LLM_MODEL=gemini-pro`
- **Ollama**: `LLM_PROVIDER=ollama`, `LLM_MODEL=llama2` (requires local Ollama installation)

### Search Providers

- **DuckDuckGo**: Free, no API key required
- **Tavily**: Best for RAG, requires API key
- **SerpAPI**: Google search results, requires API key

### Embedding Providers

- **Local**: Free Sentence Transformers (all-MiniLM-L6-v2)
- **OpenAI**: Higher quality, requires API key

## Security Features

- File type validation
- File size limits (10MB default)
- Input sanitization
- Rate limiting (10 requests/minute)
- Session-based isolation
- Automatic session cleanup

## Development

### Backend Testing
```bash
cd backend
pytest tests/
```

### Frontend Build
```bash
cd frontend
npm run build
```

## Troubleshooting

### Backend won't start
- Check Python version (3.9+)
- Verify all dependencies installed
- Check API keys in `.env`

### Frontend won't start
- Check Node.js version (18+)
- Delete `node_modules` and reinstall
- Clear Next.js cache: `rm -rf .next`

### Upload fails
- Check file size (max 10MB)
- Verify file type (PDF, DOCX, TXT only)
- Check backend logs

### No search results
- Verify search provider configuration
- Check API keys if using Tavily/SerpAPI
- Try DuckDuckGo (no API key needed)

## License

MIT

## Contributing

Contributions welcome! Please open an issue or submit a pull request.
