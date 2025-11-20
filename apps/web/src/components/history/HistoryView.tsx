'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import {
  Clock,
  MessageSquare,
  FileText,
  Image as ImageIcon,
  Search,
  Filter,
  Calendar,
} from 'lucide-react'
import { format } from 'date-fns'
import { Conversation } from '@/types'
import Link from 'next/link'

// Conversations will be fetched from API
// GET /api/conversations/{user_id}
const initialConversations: Conversation[] = []

export function HistoryView() {
  const [searchQuery, setSearchQuery] = useState('')
  const [filterType, setFilterType] = useState<'all' | 'conversations' | 'documents'>('all')
  const [conversations] = useState<Conversation[]>(initialConversations)

  const filteredConversations = conversations.filter((conv) =>
    conv.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    conv.preview.toLowerCase().includes(searchQuery.toLowerCase())
  )

  return (
    <div className="h-full flex flex-col overflow-hidden">
      {/* Header */}
      <div className="border-b border-dark-border bg-dark-surface p-6">
        <div className="max-w-5xl mx-auto space-y-4">
          <h1 className="text-2xl font-bold flex items-center gap-2 text-white">
            <Clock className="w-6 h-6 text-white" />
            History
          </h1>

          {/* Search and Filters */}
          <div className="flex flex-col sm:flex-row gap-3">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-dark-text-tertiary" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search conversations..."
                className="input-primary pl-11"
              />
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => setFilterType('all')}
                className={`px-4 py-2 rounded-ai text-sm font-medium transition-all ${
                  filterType === 'all'
                    ? 'bg-white text-dark-bg'
                    : 'bg-dark-surface text-dark-text-secondary hover:text-dark-text-primary'
                }`}
              >
                All
              </button>
              <button
                onClick={() => setFilterType('conversations')}
                className={`px-4 py-2 rounded-ai text-sm font-medium transition-all ${
                  filterType === 'conversations'
                    ? 'bg-white text-dark-bg'
                    : 'bg-dark-surface text-dark-text-secondary hover:text-dark-text-primary'
                }`}
              >
                Conversations
              </button>
              <button
                onClick={() => setFilterType('documents')}
                className={`px-4 py-2 rounded-ai text-sm font-medium transition-all ${
                  filterType === 'documents'
                    ? 'bg-white text-dark-bg'
                    : 'bg-dark-surface text-dark-text-secondary hover:text-dark-text-primary'
                }`}
              >
                Documents
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-6">
        <div className="max-w-5xl mx-auto">
          {filteredConversations.length === 0 ? (
            <div className="text-center py-12">
              <Clock className="w-16 h-16 mx-auto mb-4 text-dark-text-tertiary opacity-50" />
              <h3 className="text-lg font-medium mb-2">No conversations found</h3>
              <p className="text-dark-text-tertiary">
                {searchQuery
                  ? 'Try adjusting your search query'
                  : 'Start a new conversation to see it here'}
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {filteredConversations.map((conversation, index) => (
                <motion.div
                  key={conversation.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                >
                  <Link
                    href={`/chat/${conversation.id}`}
                    className="card p-5 hover:border-white/30 transition-all group block"
                  >
                    <div className="flex items-start gap-4">
                      <div className="p-3 rounded-ai bg-dark-hover group-hover:bg-white/10 transition-colors">
                        <MessageSquare className="w-5 h-5 text-white" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <h3 className="font-semibold text-dark-text-primary mb-1 group-hover:text-white transition-colors">
                          {conversation.title}
                        </h3>
                        <p className="text-sm text-dark-text-secondary line-clamp-2 mb-2">
                          {conversation.preview}
                        </p>
                        <div className="flex items-center gap-4 text-xs text-dark-text-tertiary">
                          <span className="flex items-center gap-1">
                            <Calendar className="w-3 h-3" />
                            {format(conversation.lastMessage, 'MMM d, yyyy')}
                          </span>
                          <span className="flex items-center gap-1">
                            <Clock className="w-3 h-3" />
                            {format(conversation.lastMessage, 'h:mm a')}
                          </span>
                          {conversation.agentType && (
                            <span className="px-2 py-0.5 bg-dark-hover rounded-ai-sm capitalize">
                              {conversation.agentType.replace('_', ' ')}
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  </Link>
                </motion.div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
