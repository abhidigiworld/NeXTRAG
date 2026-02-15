/**
 * Mode selector component - Horizontal layout for card design
 */
import { Globe, FileText, Layers } from 'lucide-react'
import { DataSourceMode } from '@/types'

interface ModeSelectorProps {
    mode: DataSourceMode
    onChange: (mode: DataSourceMode) => void
}

const modes = [
    {
        value: DataSourceMode.WEB,
        label: 'Web Search',
        icon: Globe,
        gradient: 'from-blue-500 to-cyan-500'
    },
    {
        value: DataSourceMode.DOCUMENTS,
        label: 'Document Analysis',
        icon: FileText,
        gradient: 'from-purple-500 to-pink-500'
    },
    {
        value: DataSourceMode.HYBRID,
        label: 'Hybrid Mode',
        icon: Layers,
        gradient: 'from-pink-500 to-orange-500'
    }
]

export default function ModeSelector({ mode, onChange }: ModeSelectorProps) {
    return (
        <div className="flex items-center justify-center space-x-3">
            {modes.map((modeOption) => {
                const Icon = modeOption.icon
                const isActive = mode === modeOption.value

                return (
                    <button
                        key={modeOption.value}
                        onClick={() => onChange(modeOption.value)}
                        className={`
                            relative flex items-center justify-center space-x-2
                            px-4 py-2.5 rounded-xl transition-smooth text-sm font-medium
                            ${isActive
                                ? 'bg-slate-700 dark:bg-slate-600 text-white shadow-lg'
                                : 'bg-white/5 text-slate-400 hover:bg-white/10 border border-white/10'
                            }
                        `}
                    >
                        <Icon className="w-4 h-4" />
                        <span>{modeOption.label}</span>
                    </button>
                )
            })}
        </div>
    )
}
