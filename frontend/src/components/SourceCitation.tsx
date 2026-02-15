/**
 * Source citation display component
 */
import { Citation } from '@/types'
import { ExternalLink, FileText } from 'lucide-react'
import { useState } from 'react'

interface Props {
    citations: Citation[]
}

export default function SourceCitation({ citations }: Props) {
    const [expanded, setExpanded] = useState<number | null>(null)

    if (citations.length === 0) return null

    return (
        <div className="mt-4 space-y-2">
            <h4 className="text-sm font-semibold text-slate-400">Sources ({citations.length})</h4>
            <div className="space-y-2">
                {citations.map((citation, index) => (
                    <div
                        key={index}
                        className="glass rounded-lg p-3 hover:bg-slate-700/50 transition-all cursor-pointer"
                        onClick={() => setExpanded(expanded === index ? null : index)}
                    >
                        <div className="flex items-start justify-between">
                            <div className="flex items-center space-x-2 flex-1 min-w-0">
                                {citation.source_type === 'web' ? (
                                    <ExternalLink className="w-4 h-4 text-primary-400 flex-shrink-0" />
                                ) : (
                                    <FileText className="w-4 h-4 text-purple-400 flex-shrink-0" />
                                )}
                                <div className="flex-1 min-w-0">
                                    <p className="text-sm font-medium text-slate-200 break-all">
                                        {citation.source}
                                    </p>
                                    <p className="text-xs text-slate-400">
                                        Relevance: {(citation.relevance_score * 100).toFixed(0)}%
                                    </p>
                                </div>
                            </div>
                        </div>

                        {expanded === index && (
                            <div className="mt-3 pt-3 border-t border-slate-600">
                                <p className="text-sm text-slate-300 italic">
                                    "{citation.excerpt}..."
                                </p>
                            </div>
                        )}
                    </div>
                ))}
            </div>
        </div>
    )
}
