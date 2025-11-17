'use client'

import { Message } from '@/types'
import { motion } from 'framer-motion'
import { User, Sparkles, Image as ImageIcon, FileText } from 'lucide-react'
import { AGENTS } from '@/lib/constants'
import Image from 'next/image'

interface ChatMessageProps {
  message: Message
  index: number
}

export function ChatMessage({ message, index }: ChatMessageProps) {
  const isUser = message.role === 'user'
  const agent = message.agentType
    ? AGENTS.find((a) => a.id === message.agentType)
    : null

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05 }}
      className={`flex gap-4 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}
    >
      {/* Avatar */}
      <div className="flex-shrink-0">
        {isUser ? (
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-brand-primary to-brand-accent flex items-center justify-center">
            <User className="w-4 h-4 text-white" />
          </div>
        ) : (
          <div
            className="w-8 h-8 rounded-full flex items-center justify-center text-lg"
            style={{
              background: agent
                ? `linear-gradient(135deg, ${agent.color}, ${agent.color}dd)`
                : 'linear-gradient(135deg, #4F9EFF, #7B61FF)',
            }}
          >
            {agent ? (
              <span className="text-sm">{agent.icon}</span>
            ) : (
              <Sparkles className="w-4 h-4 text-white" />
            )}
          </div>
        )}
      </div>

      {/* Message Content */}
      <div className={`flex-1 max-w-3xl ${isUser ? 'items-end' : 'items-start'} flex flex-col`}>
        {/* Agent Name (for assistant messages) */}
        {!isUser && agent && (
          <p className="text-xs font-medium text-dark-text-tertiary mb-1">
            {agent.name}
          </p>
        )}

        {/* Attachments */}
        {message.attachments && message.attachments.length > 0 && (
          <div className="mb-2 flex flex-wrap gap-2">
            {message.attachments.map((attachment) => (
              <div
                key={attachment.id}
                className="relative group overflow-hidden rounded-ai border border-dark-border"
              >
                {attachment.type === 'image' ? (
                  <div className="relative w-48 h-48">
                    <Image
                      src={attachment.url}
                      alt={attachment.name}
                      fill
                      className="object-cover"
                    />
                    <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                      <ImageIcon className="w-6 h-6 text-white" />
                    </div>
                  </div>
                ) : (
                  <div className="flex items-center gap-2 px-3 py-2 bg-dark-surface">
                    <FileText className="w-4 h-4 text-dark-text-tertiary" />
                    <span className="text-sm text-dark-text-secondary">
                      {attachment.name}
                    </span>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        {/* Message Bubble */}
        <div
          className={`px-4 py-3 rounded-ai-lg ${
            isUser
              ? 'bg-brand-primary text-white'
              : 'bg-dark-surface border border-dark-border text-dark-text-primary'
          }`}
        >
          <p className="text-sm leading-relaxed whitespace-pre-wrap">
            {message.content}
          </p>
        </div>

        {/* Timestamp */}
        <p className="text-xs text-dark-text-tertiary mt-1 px-1">
          {message.timestamp.toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit',
          })}
        </p>
      </div>
    </motion.div>
  )
}
