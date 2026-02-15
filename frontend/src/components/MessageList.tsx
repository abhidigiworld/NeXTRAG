/**
 * Message list component
 */
import { Message as MessageType } from '@/types'
import Message from './Message'
import LoadingAnimation from './LoadingAnimation'
import { useEffect, useRef } from 'react'

interface Props {
    messages: MessageType[]
    isLoading: boolean
}

export default function MessageList({ messages, isLoading }: Props) {
    const messagesEndRef = useRef<HTMLDivElement>(null)

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }

    useEffect(() => {
        scrollToBottom()
    }, [messages, isLoading])

    return (
        <div className="flex-1 overflow-y-auto custom-scrollbar px-4 py-6 space-y-6">
            {messages.length === 0 ? (
                <div className="h-full flex items-center justify-center">
                    <div className="text-center space-y-6 max-w-2xl">
                        {/* Simple Icon */}
                        <div className="relative mx-auto w-24 h-24">
                            <div className="w-24 h-24 rounded-2xl bg-slate-700 dark:bg-slate-600 flex items-center justify-center shadow-xl">
                                <svg
                                    className="w-12 h-12 text-white"
                                    fill="none"
                                    stroke="currentColor"
                                    viewBox="0 0 24 24"
                                >
                                    <path
                                        strokeLinecap="round"
                                        strokeLinejoin="round"
                                        strokeWidth={2}
                                        d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
                                    />
                                </svg>
                            </div>
                        </div>

                        {/* Simple Text */}
                        <div className="space-y-3">
                            <h2 className="text-3xl sm:text-4xl font-bold text-slate-800 dark:text-slate-200">
                                Welcome to SmartRAG AI
                            </h2>
                            <p className="text-base text-slate-600 dark:text-slate-400">
                                Choose your data source and start asking questions
                            </p>
                        </div>

                        {/* Simple Feature Pills */}
                        <div className="flex flex-wrap gap-3 justify-center mt-8">
                            <div className="glass px-4 py-2 rounded-full text-sm font-medium text-slate-700 dark:text-slate-300">
                                🌐 Web Search
                            </div>
                            <div className="glass px-4 py-2 rounded-full text-sm font-medium text-slate-700 dark:text-slate-300">
                                📄 Document Analysis
                            </div>
                            <div className="glass px-4 py-2 rounded-full text-sm font-medium text-slate-700 dark:text-slate-300">
                                🔄 Hybrid Mode
                            </div>
                        </div>
                    </div>
                </div>
            ) : (
                <>
                    {messages.map((message, index) => {
                        const isLast = index === messages.length - 1
                        // Animate only if it's the last message, from assistant, and not currently loading 
                        // (meaning msg just arrived fully)
                        // BUT: We need to ensure it doesn't re-animate on history load.
                        // For now, we assume simple session behavior: new messages arrive while user is watching.
                        const shouldAnimate = isLast && message.role === 'assistant' && !isLoading

                        return (
                            <Message
                                key={message.id}
                                message={message}
                                isTyping={shouldAnimate}
                                onTypingComplete={scrollToBottom}
                            />
                        )
                    })}

                    {isLoading && (
                        <div className="flex justify-start">
                            <div className="glass rounded-2xl p-4 flex items-center space-x-3">
                                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary-500 to-purple-600 flex items-center justify-center">
                                    <svg
                                        className="w-6 h-6 text-white"
                                        fill="none"
                                        stroke="currentColor"
                                        viewBox="0 0 24 24"
                                    >
                                        <path
                                            strokeLinecap="round"
                                            strokeLinejoin="round"
                                            strokeWidth={2}
                                            d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
                                        />
                                    </svg>
                                </div>
                                <LoadingAnimation />
                            </div>
                        </div>
                    )}
                </>
            )}

            <div ref={messagesEndRef} />
        </div>
    )
}
