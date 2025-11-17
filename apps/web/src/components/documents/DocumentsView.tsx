'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { FileText, Upload, Search, Filter, Download, Trash2, Eye } from 'lucide-react'

export function DocumentsView() {
  const [searchQuery, setSearchQuery] = useState('')

  const mockDocuments = [
    {
      id: '1',
      name: 'Q4 Marketing Strategy.pdf',
      size: '2.4 MB',
      uploadedAt: new Date(2025, 10, 15),
      type: 'pdf',
    },
    {
      id: '2',
      name: 'Product Roadmap 2025.docx',
      size: '1.8 MB',
      uploadedAt: new Date(2025, 10, 14),
      type: 'docx',
    },
  ]

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
            <button className="btn-primary flex items-center gap-2">
              <Upload className="w-4 h-4 text-dark-bg" />
              <span className="text-dark-bg">Upload</span>
            </button>
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
          {mockDocuments.length === 0 ? (
            <div className="text-center py-12">
              <FileText className="w-16 h-16 mx-auto mb-4 text-dark-text-tertiary opacity-50" />
              <h3 className="text-lg font-medium mb-2 text-white">No documents yet</h3>
              <p className="text-dark-text-tertiary mb-4">
                Upload your first document to get started
              </p>
              <button className="btn-primary">
                <Upload className="w-4 h-4 text-dark-bg inline mr-2" />
                <span className="text-dark-bg">Upload Document</span>
              </button>
            </div>
          ) : (
            <div className="space-y-3">
              {mockDocuments.map((doc, index) => (
                <motion.div
                  key={doc.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className="card p-5 hover:border-white/30 transition-all group"
                >
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-ai bg-dark-hover flex items-center justify-center">
                      <FileText className="w-6 h-6 text-white" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <h3 className="font-semibold text-white mb-1">{doc.name}</h3>
                      <p className="text-sm text-dark-text-secondary">
                        {doc.size} • {doc.uploadedAt.toLocaleDateString()}
                      </p>
                    </div>
                    <div className="flex items-center gap-2">
                      <button className="btn-icon">
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
                </motion.div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
