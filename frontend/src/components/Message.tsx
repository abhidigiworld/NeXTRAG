/**
 * Individual message component
 */
import { Message as MessageType } from '@/types'
import { User, Bot, Copy, Check } from 'lucide-react'
import { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import SourceCitation from './SourceCitation'
import { useTypewriter } from '@/hooks/useTypewriter'

interface Props {
    message: MessageType
    isTyping?: boolean
    onTypingComplete?: () => void
}

export default function Message({ message, isTyping = false, onTypingComplete }: Props) {
    const [copied, setCopied] = useState(false)
    const isUser = message.role === 'user'

    // Typewriter effect for AI messages
    const { displayText, isComplete } = useTypewriter(
        message.content,
        10, // Speed (ms)
        isTyping && !isUser
    )

    // Notify parent when typing finishes
    if (isComplete && onTypingComplete) {
        onTypingComplete()
    }

    const copyToClipboard = () => {
        navigator.clipboard.writeText(message.content)
        setCopied(true)
        setTimeout(() => setCopied(false), 2000)
    }

    return (
        <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} animate-fade-in`}>
            <div className={`max-w-3xl ${isUser ? 'w-auto' : 'w-full'}`}>
                <div className="flex items-start space-x-3">
                    {!isUser && (
                        <div className="flex-shrink-0 w-10 h-10 rounded-full bg-slate-700 dark:bg-slate-600 flex items-center justify-center shadow-lg">
                            <Bot className="w-6 h-6 text-white" />
                        </div>
                    )}

                    <div className={`flex-1 ${isUser ? 'flex justify-end' : ''}`}>
                        <div
                            className={`
                rounded-2xl p-4 shadow-lg transition-smooth
                ${isUser
                                    ? 'bg-slate-700 dark:bg-slate-600 text-white'
                                    : 'glass text-slate-800 dark:text-slate-100'
                                }
              `}
                        >
                            {/* Message content */}
                            <div className={`markdown-content break-words overflow-x-auto ${isUser ? 'text-white' : ''}`}>
                                <ReactMarkdown>
                                    {isTyping && !isUser ? displayText : message.content}
                                </ReactMarkdown>
                                {isTyping && !isComplete && !isUser && (
                                    <span className="inline-block w-2 h-4 ml-1 align-middle bg-slate-400 animate-pulse" />
                                )}
                            </div>

                            {/* Confidence score for AI messages */}
                            {!isUser && message.confidence_score !== undefined && (
                                <div className="mt-3 pt-3 border-t border-slate-600">
                                    <div className="flex items-center justify-between text-xs">
                                        <span className="text-slate-400">Confidence Score</span>
                                        <div className="flex items-center space-x-2">
                                            <div className="w-24 h-2 bg-slate-700 rounded-full overflow-hidden">
                                                <div
                                                    className="h-full bg-gradient-to-r from-green-500 to-primary-500 transition-all duration-500"
                                                    style={{ width: `${message.confidence_score * 100}%` }}
                                                ></div>
                                            </div>
                                            <span className="text-slate-300 font-semibold">
                                                {(message.confidence_score * 100).toFixed(0)}%
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            )}

                            {/* Citations */}
                            {!isUser && message.citations && message.citations.length > 0 && (
                                <SourceCitation citations={message.citations} />
                            )}

                            {/* Copy button */}
                            <div className="mt-3 flex items-center justify-between">
                                <span className="text-xs text-slate-400">
                                    {message.timestamp.toLocaleTimeString()}
                                </span>
                                <button
                                    onClick={copyToClipboard}
                                    className={`
                    p-1.5 rounded-lg transition-all
                    ${isUser
                                            ? 'hover:bg-white/20 text-white'
                                            : 'hover:bg-slate-700 text-slate-400'
                                        }
                  `}
                                    title="Copy message"
                                >
                                    {copied ? (
                                        <Check className="w-4 h-4" />
                                    ) : (
                                        <Copy className="w-4 h-4" />
                                    )}
                                </button>
                            </div>
                        </div>
                    </div>

                    {isUser && (
                        <div className="flex-shrink-0 w-10 h-10 rounded-full bg-slate-700 flex items-center justify-center">
                            <User className="w-6 h-6 text-slate-300" />
                        </div>
                    )}
                </div>
            </div>
        </div>
    )
}
