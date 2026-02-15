/**
 * TypeScript type definitions
 */

export enum DataSourceMode {
    WEB = 'web',
    DOCUMENTS = 'documents',
    HYBRID = 'hybrid',
}

export interface Citation {
    source: string;
    excerpt: string;
    relevance_score: number;
    source_type: 'web' | 'document';
}

export interface Message {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    citations?: Citation[];
    confidence_score?: number;
    mode_used?: DataSourceMode;
    sources_count?: number;
    timestamp: Date;
}

export interface ChatRequest {
    message: string;
    mode: DataSourceMode;
    session_id: string;
    conversation_history?: Array<{ role: string; content: string }>;
}

export interface ChatResponse {
    answer: string;
    citations: Citation[];
    confidence_score: number;
    mode_used: DataSourceMode;
    sources_count: number;
}

export interface UploadedFile {
    file_id: string;
    filename: string;
    size_bytes: number;
    status: string;
    message: string;
}
