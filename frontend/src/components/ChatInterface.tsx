/**
 * Main chat interface component with centered card layout and responsive design
 */

import { useState, useEffect } from 'react'
import { createPortal } from 'react-dom'
import { v4 as uuidv4 } from 'uuid'
import { Send, Moon, Sun, Sparkles, Menu, X } from 'lucide-react'
import axios from 'axios'

import { DataSourceMode, Message, ChatResponse } from '@/types'
import ModeSelector from './ModeSelector'
import MessageList from './MessageList'
import { DocumentSidebar } from './DocumentSidebar'

import { API_BASE_URL } from '../config'

interface Document {
    id: string
    name: string
    size: number
    uploadedAt: string
}

export default function ChatInterface() {
    const [messages, setMessages] = useState<Message[]>([])
    const [input, setInput] = useState('')
    const [mode, setMode] = useState<DataSourceMode>(DataSourceMode.WEB)
    const [sessionId] = useState(() => uuidv4())
    const [isLoading, setIsLoading] = useState(false)
    const [darkMode, setDarkMode] = useState(true)
    const [documents, setDocuments] = useState<Document[]>([])
    const [sidebarOpen, setSidebarOpen] = useState(false)
    const [mounted, setMounted] = useState(false)

    // Initialize dark mode & mounted state
    useEffect(() => {
        document.documentElement.classList.add('dark')
        setMounted(true)
    }, [])

    useEffect(() => {
        if (darkMode) {
            document.documentElement.classList.add('dark')
        } else {
            document.documentElement.classList.remove('dark')
        }
    }, [darkMode])

    const handleDocumentUpload = async (file: File) => {
        const formData = new FormData()
        formData.append('file', file)
        formData.append('session_id', sessionId)

        try {
            const response = await axios.post(`${API_BASE_URL}/upload`, formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            })

            const newDoc: Document = {
                id: uuidv4(),
                name: file.name,
                size: file.size,
                uploadedAt: new Date().toISOString()
            }

            setDocuments(prev => [...prev, newDoc])
            // Close sidebar on mobile after upload
            if (window.innerWidth < 1024) {
                setSidebarOpen(false)
            }
        } catch (error) {
            console.error('Error uploading document:', error)
            alert('Failed to upload document')
        }
    }

    const handleDocumentDelete = async (id: string) => {
        setDocuments(prev => prev.filter(doc => doc.id !== id))
    }

    const sendMessage = async () => {
        if (!input.trim() || isLoading) return

        const userMessage: Message = {
            id: uuidv4(),
            role: 'user',
            content: input.trim(),
            timestamp: new Date()
        }

        setMessages(prev => [...prev, userMessage])
        setInput('')
        setIsLoading(true)

        try {
            const response = await axios.post<ChatResponse>(`${API_BASE_URL}/chat`, {
                message: userMessage.content,
                session_id: sessionId,
                mode: mode,
                conversation_history: []
            })

            const aiMessage: Message = {
                id: uuidv4(),
                role: 'assistant',
                content: response.data.answer,
                timestamp: new Date(),
                confidence_score: response.data.confidence_score,
                citations: response.data.citations
            }

            setMessages(prev => [...prev, aiMessage])
        } catch (error) {
            console.error('Error sending message:', error)
            const errorMessage: Message = {
                id: uuidv4(),
                role: 'assistant',
                content: 'Sorry, I encountered an error. Please try again.',
                timestamp: new Date()
            }
            setMessages(prev => [...prev, errorMessage])
        } finally {
            setIsLoading(false)
        }
    }

    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault()
            sendMessage()
        }
    }

    return (
        <div className="h-screen w-full flex items-center justify-center bg-slate-900 overflow-hidden">
            {/* Mobile Overlay - Handled by Portal below */}

            {/* Mobile Sidebar & Overlay - Rendered via Portal at Body Level to fix Z-Index */}
            {mounted && createPortal(
                <div className={`fixed inset-0 z-[100] lg:hidden ${sidebarOpen ? 'block' : 'hidden'}`}>
                    {/* Dark Overlay */}
                    <div
                        className="absolute inset-0 bg-black/90 backdrop-blur-none transition-opacity duration-300"
                        onClick={() => setSidebarOpen(false)}
                    />

                    {/* Sidebar Content */}
                    <div className={`
                        absolute inset-y-0 left-0 w-80 max-w-[85vw]
                        bg-slate-900 shadow-2xl border-r border-white/10
                        flex flex-col
                        transform transition-transform duration-300 ease-in-out
                        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
                    `}>
                        {/* Sidebar Header */}
                        <div className="p-4 border-b border-white/10">
                            <div className="flex items-center justify-between">
                                <div className="flex items-center space-x-3">
                                    <div className="w-10 h-10 rounded-xl bg-slate-700 dark:bg-slate-600 flex items-center justify-center">
                                        <Sparkles className="w-6 h-6 text-white" />
                                    </div>
                                    <div>
                                        <h1 className="text-lg font-bold text-white">SmartRAG AI</h1>
                                        <p className="text-xs text-slate-400">Intelligent Assistant</p>
                                    </div>
                                </div>
                                <button
                                    onClick={() => setSidebarOpen(false)}
                                    className="p-2 rounded-lg hover:bg-white/10 transition-smooth"
                                >
                                    <X className="w-5 h-5 text-white" />
                                </button>
                            </div>
                        </div>

                        <div className="flex-1 overflow-hidden">
                            <DocumentSidebar
                                isOpen={true}
                                onToggle={() => { }}
                                documents={documents}
                                onUpload={handleDocumentUpload}
                                onDelete={handleDocumentDelete}
                                isUploadDisabled={mode === DataSourceMode.WEB}
                            />
                        </div>
                    </div>
                </div>,
                document.body
            )}

            {/* Full Screen Container - Responsive */}
            <div className="w-full h-full glass-strong overflow-hidden flex relative rounded-none shadow-none">

                {/* Desktop Sidebar - Static inside card */}
                <div className="hidden lg:flex w-80 h-full border-r border-white/10 flex-col bg-transparent">
                    {/* Sidebar Header */}
                    <div className="p-4 sm:p-6 border-b border-white/10">
                        <div className="flex items-center justify-between">
                            <div className="flex items-center space-x-3">
                                <div className="w-10 h-10 rounded-xl bg-slate-700 dark:bg-slate-600 flex items-center justify-center">
                                    <Sparkles className="w-6 h-6 text-white" />
                                </div>
                                <div>
                                    <h1 className="text-lg sm:text-xl font-bold text-white">SmartRAG AI</h1>
                                    <p className="text-xs text-slate-400">Intelligent Assistant</p>
                                </div>
                            </div>
                            {/* Close button for mobile */}
                            <button
                                onClick={() => setSidebarOpen(false)}
                                className="lg:hidden p-2 rounded-lg hover:bg-white/10 transition-smooth"
                                aria-label="Close sidebar"
                            >
                                <X className="w-5 h-5 text-white" />
                            </button>
                        </div>
                    </div>

                    {/* Document Sidebar Content */}
                    <div className="flex-1 overflow-hidden">
                        <DocumentSidebar
                            isOpen={true}
                            onToggle={() => { }}
                            documents={documents}
                            onUpload={handleDocumentUpload}
                            onDelete={handleDocumentDelete}
                            isUploadDisabled={mode === DataSourceMode.WEB}
                        />
                    </div>
                </div>

                {/* Main Content Area */}
                <div className="flex-1 flex flex-col w-full lg:w-auto">
                    {/* Top Header */}
                    <div className="px-4 sm:px-6 py-3 sm:py-4 border-b border-white/10 flex items-center justify-between flex-shrink-0">
                        <div className="flex items-center space-x-3">
                            {/* Hamburger Menu - Mobile Only */}
                            <button
                                onClick={() => setSidebarOpen(!sidebarOpen)}
                                className="lg:hidden p-2 rounded-lg hover:bg-white/10 transition-smooth"
                                aria-label="Toggle sidebar"
                            >
                                <Menu className="w-5 h-5 text-white" />
                            </button>
                            <div className="flex items-center space-x-2">
                                <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
                                <span className="text-xs sm:text-sm text-slate-400">Online</span>
                            </div>
                        </div>

                        {/* Dark Mode Toggle */}
                        <button
                            onClick={() => setDarkMode(!darkMode)}
                            className="p-2 rounded-xl glass hover:glass-strong transition-smooth"
                            aria-label="Toggle dark mode"
                        >
                            {darkMode ? (
                                <Sun className="w-4 h-4 sm:w-5 sm:h-5 text-yellow-400" />
                            ) : (
                                <Moon className="w-4 h-4 sm:w-5 sm:h-5 text-slate-700" />
                            )}
                        </button>
                    </div>

                    {/* Messages Area */}
                    <div className="flex-1 flex flex-col min-h-0 overflow-hidden">
                        <MessageList messages={messages} isLoading={isLoading} />
                    </div>

                    {/* Input Area - Bottom */}
                    <div className="p-3 sm:p-4 lg:p-6 border-t border-white/10 flex-shrink-0">
                        {/* Mode Selector */}
                        <div className="mb-3 sm:mb-4">
                            <ModeSelector mode={mode} onChange={setMode} />
                        </div>

                        {/* Input Box */}
                        <div className="flex items-center space-x-2 sm:space-x-3">
                            <div className="flex-1 relative">
                                <textarea
                                    value={input}
                                    onChange={(e) => setInput(e.target.value)}
                                    onKeyDown={handleKeyPress}
                                    placeholder="Ask me anything..."
                                    className="w-full px-3 sm:px-4 py-2 sm:py-3 bg-white/90 dark:bg-slate-800/90 text-slate-900 dark:text-white rounded-xl sm:rounded-2xl border border-white/20 focus:outline-none focus:ring-2 focus:ring-slate-500 resize-none transition-smooth text-sm sm:text-base"
                                    rows={1}
                                    style={{ minHeight: '44px', maxHeight: '120px' }}
                                />
                            </div>

                            {/* Send Button */}
                            <button
                                onClick={sendMessage}
                                disabled={!input.trim() || isLoading}
                                className="p-2.5 sm:p-3 rounded-xl sm:rounded-2xl bg-slate-700 dark:bg-slate-600 hover:bg-slate-600 dark:hover:bg-slate-500 disabled:opacity-50 disabled:cursor-not-allowed transition-smooth shadow-lg flex-shrink-0"
                                aria-label="Send message"
                            >
                                <Send className="w-5 h-5 sm:w-6 sm:h-6 text-white" />
                            </button>
                        </div>

                        {/* Footer Info */}
                        <div className="mt-2 sm:mt-3 text-center">
                            <p className="text-xs text-slate-500">
                                Session: {sessionId.slice(0, 8)} • {documents.length} document{documents.length !== 1 ? 's' : ''}
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}
