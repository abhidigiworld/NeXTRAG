
import { X, HelpCircle, BookOpen, Upload, Zap, Globe } from 'lucide-react'

interface HelpModalProps {
    isOpen: boolean
    onClose: () => void
}

export default function HelpModal({ isOpen, onClose }: HelpModalProps) {
    if (!isOpen) return null

    return (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
            <div
                className="absolute inset-0 bg-black/60 backdrop-blur-sm transition-opacity"
                onClick={onClose}
            />

            <div className="relative w-full max-w-2xl bg-slate-900 border border-white/10 rounded-2xl shadow-2xl overflow-hidden transform transition-all animate-in fade-in zoom-in-95 duration-200">
                {/* Header */}
                <div className="flex items-center justify-between p-6 border-b border-white/10 bg-slate-800/50">
                    <div className="flex items-center space-x-3">
                        <div className="p-2 bg-primary-500/20 rounded-lg">
                            <BookOpen className="w-6 h-6 text-primary-400" />
                        </div>
                        <div>
                            <h2 className="text-xl font-bold text-white">How to use SmartRAG AI</h2>
                            <p className="text-sm text-slate-400">Quick start guide & tips</p>
                        </div>
                    </div>
                    <button
                        onClick={onClose}
                        className="p-2 hover:bg-white/10 rounded-lg transition-colors"
                    >
                        <X className="w-5 h-5 text-slate-400" />
                    </button>
                </div>

                {/* Content */}
                <div className="p-6 max-h-[70vh] overflow-y-auto space-y-8">

                    {/* Modes Section */}
                    <div className="space-y-4">
                        <h3 className="text-lg font-semibold text-white flex items-center">
                            <Zap className="w-5 h-5 mr-2 text-yellow-500" />
                            Choose Your Mode
                        </h3>
                        <div className="grid md:grid-cols-2 gap-4">
                            <div className="p-4 rounded-xl bg-white/5 border border-white/5 hover:border-primary-500/30 transition-colors">
                                <div className="flex items-center mb-2 text-primary-400">
                                    <Globe className="w-4 h-4 mr-2" />
                                    <span className="font-medium">Web Search Mode</span>
                                </div>
                                <p className="text-sm text-slate-400">
                                    Best for general knowledge, current events, and broad topics. Searches the live internet.
                                </p>
                            </div>
                            <div className="p-4 rounded-xl bg-white/5 border border-white/5 hover:border-purple-500/30 transition-colors">
                                <div className="flex items-center mb-2 text-purple-400">
                                    <Upload className="w-4 h-4 mr-2" />
                                    <span className="font-medium">Hybrid Mode</span>
                                </div>
                                <p className="text-sm text-slate-400">
                                    Combines your **uploaded documents** with web search. Perfect for specific analysis.
                                </p>
                            </div>
                        </div>
                    </div>

                    {/* Upload Section */}
                    <div className="space-y-4">
                        <h3 className="text-lg font-semibold text-white flex items-center">
                            <Upload className="w-5 h-5 mr-2 text-blue-500" />
                            Uploading Documents
                        </h3>
                        <div className="pl-4 border-l-2 border-blue-500/30 space-y-2">
                            <p className="text-slate-300">
                                1. Open the **Sidebar** (click menu icon on mobile).
                            </p>
                            <p className="text-slate-300">
                                2. Drag & Drop files or click **Browse**.
                            </p>
                            <p className="text-slate-300">
                                3. Switch to **Hybrid Mode** to ask questions about your files.
                            </p>
                            <div className="mt-2 text-xs text-slate-500 bg-slate-950/50 p-2 rounded">
                                Supported: PDF, DOCX, TXT (Max 10MB)
                            </div>
                        </div>
                    </div>

                    {/* Pro Tips */}
                    <div className="bg-gradient-to-r from-primary-900/20 to-purple-900/20 p-4 rounded-xl border border-white/10">
                        <h4 className="font-medium text-white mb-2 flex items-center">
                            <HelpCircle className="w-4 h-4 mr-2 text-primary-400" />
                            Pro Tips
                        </h4>
                        <ul className="text-sm text-slate-300 space-y-2 list-disc list-inside">
                            <li>Be specific! "Summarize the introduction of the Q3 report" works better than "Summarize".</li>
                            <li>Check citations [1] to see where the info came from.</li>
                            <li>You can ask follow-up questions in the chat.</li>
                        </ul>
                    </div>

                </div>

                {/* Footer */}
                <div className="p-4 border-t border-white/10 bg-slate-800/30 flex justify-end">
                    <button
                        onClick={onClose}
                        className="px-4 py-2 bg-primary-600 hover:bg-primary-500 text-white rounded-lg font-medium transition-colors"
                    >
                        Got it!
                    </button>
                </div>
            </div>
        </div>
    )
}
