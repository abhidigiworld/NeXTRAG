/**
 * Document sidebar component - Integrated version for card layout
 */
import React, { useState } from 'react'
import { Upload, File, X, Trash2 } from 'lucide-react'

interface Document {
    id: string
    name: string
    size: number
    uploadedAt: string
}

interface DocumentSidebarProps {
    isOpen: boolean
    onToggle: () => void
    documents: Document[]
    onUpload: (file: File) => void
    onDelete: (id: string) => void
    isUploadDisabled?: boolean
}

export const DocumentSidebar: React.FC<DocumentSidebarProps> = ({
    documents,
    onUpload,
    onDelete,
    isUploadDisabled = false
}) => {
    const [isDragging, setIsDragging] = useState(false)

    const handleDragOver = (e: React.DragEvent) => {
        e.preventDefault()
        if (!isUploadDisabled) {
            setIsDragging(true)
        }
    }

    const handleDragLeave = () => {
        setIsDragging(false)
    }

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault()
        setIsDragging(false)

        if (isUploadDisabled) return

        const files = Array.from(e.dataTransfer.files)
        files.forEach(file => {
            onUpload(file)
        })
    }

    const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        const files = e.target.files
        if (files && files.length > 0) {
            // Upload all selected files
            Array.from(files).forEach(file => {
                onUpload(file)
            })
        }
    }

    const formatFileSize = (bytes: number): string => {
        if (bytes < 1024) return bytes + ' B'
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
        return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
    }

    return (
        <div className="h-full flex flex-col p-4">
            {/* Header */}
            <div className="mb-4">
                <h2 className="text-base font-semibold text-slate-800 dark:text-white">File Uploads</h2>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                    {isUploadDisabled
                        ? 'Uploads disabled in Web Search'
                        : 'Upload and manage your files'
                    }
                </p>
            </div>

            {/* Upload Area */}
            <div
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                className={`
                    border-2 border-dashed rounded-xl p-4 mb-4 transition-smooth text-center
                    ${isUploadDisabled
                        ? 'border-slate-200 dark:border-slate-700 bg-slate-100 dark:bg-slate-800/50 cursor-not-allowed opacity-60'
                        : isDragging
                            ? 'border-slate-400 bg-slate-400/10'
                            : 'border-slate-300 dark:border-white/20 hover:border-slate-400 dark:hover:border-white/30 bg-white/5'
                    }
                `}
            >
                <input
                    type="file"
                    id="file-upload"
                    className="hidden"
                    onChange={handleFileSelect}
                    accept=".pdf,.doc,.docx,.txt"
                    multiple
                    disabled={isUploadDisabled}
                />
                <label
                    htmlFor="file-upload"
                    className={`flex flex-col items-center space-y-2 ${isUploadDisabled ? 'cursor-not-allowed' : 'cursor-pointer'}`}
                >
                    <div className={`w-12 h-12 rounded-full flex items-center justify-center ${isUploadDisabled ? 'bg-slate-200 dark:bg-slate-700' : 'bg-slate-700/10 dark:bg-slate-700/30'
                        }`}>
                        <Upload className={`w-6 h-6 ${isUploadDisabled ? 'text-slate-400' : 'text-slate-500 dark:text-slate-300'}`} />
                    </div>
                    <div>
                        <p className={`text-sm font-medium ${isUploadDisabled ? 'text-slate-400' : 'text-slate-600 dark:text-slate-300'}`}>
                            {isUploadDisabled ? 'Upload Disabled' : (isDragging ? 'Drop file here' : 'Upload files')}
                        </p>
                        {!isUploadDisabled && (
                            <>
                                <p className="text-xs text-slate-500 mt-1">
                                    or drag and drop
                                </p>
                                <p className="text-xs text-slate-400 dark:text-slate-600 mt-1">
                                    PDF, DOCX, TXT
                                </p>
                            </>
                        )}
                    </div>
                </label>
            </div>

            {/* Document List */}
            <div className="flex-1 overflow-y-auto space-y-2 custom-scrollbar">
                {documents.length === 0 ? (
                    <div className="text-center py-8">
                        <File className="w-12 h-12 text-slate-600 mx-auto mb-2" />
                        <p className="text-sm text-slate-500">No documents uploaded</p>
                    </div>
                ) : (
                    documents.map((doc) => (
                        <div
                            key={doc.id}
                            className="group glass p-3 rounded-lg hover:glass-strong transition-smooth"
                        >
                            <div className="flex items-start space-x-3">
                                <div className="flex-shrink-0 w-8 h-8 rounded-lg bg-gradient-to-br from-purple-500/20 to-blue-500/20 flex items-center justify-center">
                                    <File className="w-4 h-4 text-purple-400" />
                                </div>

                                <div className="flex-1 min-w-0">
                                    <p className="text-sm font-medium text-white truncate">
                                        {doc.name}
                                    </p>
                                    <p className="text-xs text-slate-500 mt-0.5">
                                        {formatFileSize(doc.size)}
                                    </p>
                                </div>

                                <button
                                    onClick={() => onDelete(doc.id)}
                                    className="flex-shrink-0 p-1.5 rounded-lg opacity-0 group-hover:opacity-100 hover:bg-red-500/20 transition-smooth"
                                    aria-label="Delete document"
                                >
                                    <Trash2 className="w-4 h-4 text-red-400" />
                                </button>
                            </div>
                        </div>
                    ))
                )}
            </div>
        </div>
    )
}
