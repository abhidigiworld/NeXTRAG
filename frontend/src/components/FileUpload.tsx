/**
 * File upload component with drag and drop
 */
import { useCallback, useState } from 'react'
import { Upload, X, FileText, Loader2 } from 'lucide-react'
import axios from 'axios'
import { UploadedFile } from '@/types'
import { API_BASE_URL } from '../config'

interface Props {
    sessionId: string
    onUploadComplete: () => void
}

export default function FileUpload({ sessionId, onUploadComplete }: Props) {
    const [isDragging, setIsDragging] = useState(false)
    const [uploading, setUploading] = useState(false)
    const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([])

    const handleDragOver = useCallback((e: React.DragEvent) => {
        e.preventDefault()
        setIsDragging(true)
    }, [])

    const handleDragLeave = useCallback((e: React.DragEvent) => {
        e.preventDefault()
        setIsDragging(false)
    }, [])

    const handleDrop = useCallback(async (e: React.DragEvent) => {
        e.preventDefault()
        setIsDragging(false)

        const files = Array.from(e.dataTransfer.files)
        await uploadFiles(files)
    }, [sessionId])

    const handleFileSelect = useCallback(async (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files) {
            const files = Array.from(e.target.files)
            await uploadFiles(files)
        }
    }, [sessionId])

    const uploadFiles = async (files: File[]) => {
        setUploading(true)

        for (const file of files) {
            try {
                const formData = new FormData()
                formData.append('file', file)

                const response = await axios.post<UploadedFile>(
                    `${API_BASE_URL}/upload?session_id=${sessionId}`,
                    formData,
                    {
                        headers: {
                            'Content-Type': 'multipart/form-data',
                        },
                    }
                )

                setUploadedFiles(prev => [...prev, response.data])
                onUploadComplete()
            } catch (error) {
                console.error('Upload error:', error)
                alert(`Failed to upload ${file.name}`)
            }
        }

        setUploading(false)
    }

    const removeFile = (fileId: string) => {
        setUploadedFiles(prev => prev.filter(f => f.file_id !== fileId))
    }

    return (
        <div className="space-y-4">
            {/* Drop zone */}
            <div
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                className={`
          glass rounded-2xl p-8 text-center transition-all duration-300
          ${isDragging
                        ? 'border-2 border-primary-500 bg-primary-500/10 scale-105'
                        : 'border-2 border-dashed border-slate-600 hover:border-slate-500'
                    }
        `}
            >
                <input
                    type="file"
                    id="file-upload"
                    className="hidden"
                    onChange={handleFileSelect}
                    multiple
                    accept=".pdf,.docx,.txt"
                />

                <label htmlFor="file-upload" className="cursor-pointer">
                    <div className="flex flex-col items-center space-y-3">
                        {uploading ? (
                            <Loader2 className="w-12 h-12 text-primary-400 animate-spin" />
                        ) : (
                            <Upload className="w-12 h-12 text-slate-400" />
                        )}

                        <div>
                            <p className="text-lg font-semibold text-slate-200">
                                {uploading ? 'Uploading...' : 'Drop files here or click to browse'}
                            </p>
                            <p className="text-sm text-slate-400 mt-1">
                                Supports PDF, DOCX, TXT (max 10MB)
                            </p>
                        </div>
                    </div>
                </label>
            </div>

            {/* Uploaded files list */}
            {uploadedFiles.length > 0 && (
                <div className="space-y-2">
                    <h4 className="text-sm font-semibold text-slate-400">
                        Uploaded Files ({uploadedFiles.length})
                    </h4>
                    {uploadedFiles.map((file) => (
                        <div
                            key={file.file_id}
                            className="glass rounded-lg p-3 flex items-center justify-between group hover:bg-slate-700/50 transition-all"
                        >
                            <div className="flex items-center space-x-3">
                                <FileText className="w-5 h-5 text-purple-400" />
                                <div>
                                    <p className="text-sm font-medium text-slate-200">
                                        {file.filename}
                                    </p>
                                    <p className="text-xs text-slate-400">
                                        {(file.size_bytes / 1024).toFixed(1)} KB • {file.message}
                                    </p>
                                </div>
                            </div>

                            <button
                                onClick={() => removeFile(file.file_id)}
                                className="opacity-0 group-hover:opacity-100 transition-opacity p-1 hover:bg-red-500/20 rounded"
                            >
                                <X className="w-4 h-4 text-red-400" />
                            </button>
                        </div>
                    ))}
                </div>
            )}
        </div>
    )
}
