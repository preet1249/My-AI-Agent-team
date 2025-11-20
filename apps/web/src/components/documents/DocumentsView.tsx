'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { FileText, Upload, Search, Filter, Download, Trash2, Eye, RefreshCw } from 'lucide-react'
import { API_URL } from '@/lib/constants'

interface Document {
  id: string
  title: string
  content: string
  type: string
  metadata: {
    platforms?: string[]
  }
  created_at: string
}

export function DocumentsView() {
  const [searchQuery, setSearchQuery] = useState('')
  const [documents, setDocuments] = useState<Document[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [selectedDoc, setSelectedDoc] = useState<Document | null>(null)

  // Fetch documents from API
  useEffect(() => {
    fetchDocuments()
  }, [])

  const fetchDocuments = async () => {
    setIsLoading(true)
    try {
      const response = await fetch(`${API_URL}/api/documents/user-123?limit=50`)
      if (response.ok) {
        const data = await response.json()
        if (data.success && data.data) {
          setDocuments(data.data)
        }
      }
    } catch (error) {
      console.log('Could not fetch documents')
    } finally {
      setIsLoading(false)
    }
  }

  // Filter documents by search
  const filteredDocs = documents.filter(doc =>
    doc.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    doc.content.toLowerCase().includes(searchQuery.toLowerCase())
  )

  // Format file size (estimate based on content length)
  const formatSize = (content: string) => {
    const bytes = new Blob([content]).size
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  }

  return (
    <div className="h-full flex flex-col overflow-hidden">
      {/* Header */}
      <div className="border-b border-dark-border bg-dark-surface p-6">
        <div className="max-w-5xl mx-auto space-y-4">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold flex items-center gap-2 text-white">
              <FileText className="w-6 h-6 text-white" />
              Documents
            </h1>
            <div className="flex gap-2">
              <button
                onClick={fetchDocuments}
                className="btn-secondary flex items-center gap-2"
                disabled={isLoading}
              >
                <RefreshCw className={`w-4 h-4 text-white ${isLoading ? 'animate-spin' : ''}`} />
                <span className="text-white">Refresh</span>
              </button>
              <button className="btn-primary flex items-center gap-2">
                <Upload className="w-4 h-4 text-dark-bg" />
                <span className="text-dark-bg">Upload</span>
              </button>
            </div>
          </div>

          {/* Search */}
          <div className="flex gap-3">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-dark-text-tertiary" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search documents..."
                className="input-primary pl-11"
              />
            </div>
            <button className="btn-secondary flex items-center gap-2">
              <Filter className="w-4 h-4 text-white" />
              <span className="text-white">Filter</span>
            </button>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-6">
        <div className="max-w-5xl mx-auto">
          {isLoading ? (
            <div className="text-center py-12">
              <div className="w-8 h-8 border-2 border-white/20 border-t-white rounded-full animate-spin mx-auto mb-4" />
              <p className="text-dark-text-tertiary">Loading documents...</p>
            </div>
          ) : filteredDocs.length === 0 ? (
            <div className="text-center py-12">
              <FileText className="w-16 h-16 mx-auto mb-4 text-dark-text-tertiary opacity-50" />
              <h3 className="text-lg font-medium mb-2 text-white">No documents yet</h3>
              <p className="text-dark-text-tertiary mb-4">
                Create content with Ryan (Marketing) and save it here
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {filteredDocs.map((doc, index) => (
                <motion.div
                  key={doc.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className="card p-5 hover:border-white/30 transition-all group cursor-pointer"
                  onClick={() => setSelectedDoc(selectedDoc?.id === doc.id ? null : doc)}
                >
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-ai bg-dark-hover flex items-center justify-center">
                      <FileText className="w-6 h-6 text-white" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <h3 className="font-semibold text-white mb-1">{doc.title}</h3>
                      <p className="text-sm text-dark-text-secondary">
                        {formatSize(doc.content)} • {new Date(doc.created_at).toLocaleDateString()}
                        {doc.metadata?.platforms?.length > 0 && (
                          <span className="ml-2 text-dark-text-tertiary">
                            • {doc.metadata.platforms.join(', ')}
                          </span>
                        )}
                      </p>
                    </div>
                    <div className="flex items-center gap-2">
                      <button className="btn-icon" onClick={(e) => { e.stopPropagation(); setSelectedDoc(doc); }}>
                        <Eye className="w-4 h-4 text-white" />
                      </button>
                      <button className="btn-icon">
                        <Download className="w-4 h-4 text-white" />
                      </button>
                      <button className="btn-icon hover:text-red-500">
                        <Trash2 className="w-4 h-4 text-white" />
                      </button>
                    </div>
                  </div>
                  {/* Preview content when selected */}
                  {selectedDoc?.id === doc.id && (
                    <div className="mt-4 pt-4 border-t border-dark-border">
                      <pre className="text-sm text-dark-text-secondary whitespace-pre-wrap font-sans max-h-64 overflow-y-auto">
                        {doc.content}
                      </pre>
                    </div>
                  )}
                </motion.div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
