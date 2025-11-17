'use client'

import { useState, useRef, KeyboardEvent } from 'react'
import {
  Send,
  Paperclip,
  Mic,
  Image as ImageIcon,
  AtSign,
  Sparkles,
} from 'lucide-react'
import { AGENTS } from '@/lib/constants'
import { motion, AnimatePresence } from 'framer-motion'

interface ChatInputProps {
  onSend: (message: string, attachments?: File[], agent?: string) => void
  disabled?: boolean
}

export function ChatInput({ onSend, disabled }: ChatInputProps) {
  const [message, setMessage] = useState('')
  const [attachments, setAttachments] = useState<File[]>([])
  const [showAgentMenu, setShowAgentMenu] = useState(false)
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null)
  const [mentionSearch, setMentionSearch] = useState('')

  const inputRef = useRef<HTMLTextAreaElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit()
    }

    // Handle @ mention
    if (e.key === '@') {
      setShowAgentMenu(true)
      setMentionSearch('')
    }

    if (showAgentMenu && e.key === 'Escape') {
      setShowAgentMenu(false)
    }
  }

  const handleSubmit = () => {
    if (!message.trim() && attachments.length === 0) return
    if (disabled) return

    onSend(message, attachments, selectedAgent || undefined)
    setMessage('')
    setAttachments([])
    setSelectedAgent(null)
    setShowAgentMenu(false)

    // Reset textarea height
    if (inputRef.current) {
      inputRef.current.style.height = 'auto'
    }
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || [])
    setAttachments((prev) => [...prev, ...files])
  }

  const removeAttachment = (index: number) => {
    setAttachments((prev) => prev.filter((_, i) => i !== index))
  }

  const selectAgent = (agentId: string) => {
    setSelectedAgent(agentId)
    setShowAgentMenu(false)
    const agent = AGENTS.find((a) => a.id === agentId)
    if (agent) {
      // Add @ mention to message
      const newMessage = message + `@${agent.name} `
      setMessage(newMessage)
      inputRef.current?.focus()
    }
  }

  const filteredAgents = AGENTS.filter((agent) =>
    agent.name.toLowerCase().includes(mentionSearch.toLowerCase())
  )

  // Auto-resize textarea
  const handleInput = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const target = e.target
    target.style.height = 'auto'
    target.style.height = `${Math.min(target.scrollHeight, 200)}px`

    setMessage(target.value)

    // Check for @ mention
    const lastAtIndex = target.value.lastIndexOf('@')
    if (lastAtIndex !== -1) {
      const searchTerm = target.value.slice(lastAtIndex + 1)
      if (!searchTerm.includes(' ')) {
        setMentionSearch(searchTerm)
        setShowAgentMenu(true)
      }
    }
  }

  return (
    <div className="relative">
      {/* Agent Mention Menu */}
      <AnimatePresence>
        {showAgentMenu && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 10 }}
            className="absolute bottom-full mb-2 left-0 right-0 bg-dark-surface border border-dark-border rounded-ai-lg overflow-hidden shadow-2xl"
          >
            <div className="p-2 border-b border-dark-border">
              <p className="text-xs text-dark-text-tertiary font-medium">
                Select an agent
              </p>
            </div>
            <div className="max-h-64 overflow-y-auto p-2 space-y-1">
              {filteredAgents.map((agent) => (
                <button
                  key={agent.id}
                  onClick={() => selectAgent(agent.id)}
                  className="w-full flex items-center gap-3 px-3 py-2.5 rounded-ai hover:bg-dark-hover transition-all group"
                >
                  <div className="w-8 h-8 rounded-ai bg-dark-hover border border-dark-border flex items-center justify-center">
                    <agent.icon className="w-4 h-4 text-white" />
                  </div>
                  <div className="flex-1 text-left">
                    <p className="text-sm font-medium text-dark-text-primary">
                      {agent.name}
                    </p>
                    <p className="text-xs text-dark-text-tertiary">
                      {agent.description}
                    </p>
                  </div>
                </button>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Selected Agent Indicator */}
      {selectedAgent && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-2 flex items-center gap-2 px-3 py-2 bg-dark-surface rounded-ai border border-dark-border"
        >
          <Sparkles className="w-4 h-4 text-brand-primary" />
          <span className="text-sm text-dark-text-secondary">
            Sending to:{' '}
            <span className="font-medium text-dark-text-primary">
              {AGENTS.find((a) => a.id === selectedAgent)?.name}
            </span>
          </span>
          <button
            onClick={() => setSelectedAgent(null)}
            className="ml-auto text-xs text-dark-text-tertiary hover:text-dark-text-primary"
          >
            Clear
          </button>
        </motion.div>
      )}

      {/* Attachments Preview */}
      {attachments.length > 0 && (
        <div className="mb-2 flex flex-wrap gap-2">
          {attachments.map((file, index) => (
            <motion.div
              key={index}
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              className="flex items-center gap-2 px-3 py-2 bg-dark-surface rounded-ai border border-dark-border"
            >
              <ImageIcon className="w-4 h-4 text-dark-text-tertiary" />
              <span className="text-sm text-dark-text-secondary truncate max-w-[200px]">
                {file.name}
              </span>
              <button
                onClick={() => removeAttachment(index)}
                className="text-dark-text-tertiary hover:text-dark-text-primary"
              >
                ×
              </button>
            </motion.div>
          ))}
        </div>
      )}

      {/* Input Container */}
      <div className="relative flex items-end gap-2 bg-dark-surface rounded-ai-lg border border-dark-border p-2 focus-within:ring-2 focus-within:ring-white/20 focus-within:border-white transition-all">
        {/* Toolbar */}
        <div className="flex items-center gap-1 pb-2">
          <button
            onClick={() => fileInputRef.current?.click()}
            className="btn-icon text-white"
            disabled={disabled}
            title="Attach file"
          >
            <Paperclip className="w-5 h-5" />
          </button>
        </div>

        {/* Text Input */}
        <textarea
          ref={inputRef}
          value={message}
          onChange={handleInput}
          onKeyDown={handleKeyDown}
          placeholder="Ask AI Agent Team..."
          disabled={disabled}
          rows={1}
          className="flex-1 bg-transparent border-none outline-none resize-none text-dark-text-primary placeholder:text-dark-text-tertiary py-2 px-2 max-h-[200px]"
          style={{ minHeight: '40px' }}
        />

        {/* Send Button */}
        <button
          onClick={handleSubmit}
          disabled={disabled || (!message.trim() && attachments.length === 0)}
          className="btn-primary px-4 py-2 flex items-center gap-2 shrink-0"
        >
          <Send className="w-4 h-4 text-dark-bg" />
          <span className="hidden sm:inline text-dark-bg">Send</span>
        </button>

        {/* Hidden File Input */}
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept="image/*,.pdf,.doc,.docx,.txt"
          onChange={handleFileSelect}
          className="hidden"
        />
      </div>

      {/* Helper Text */}
      <div className="mt-2 px-2 flex items-center justify-end text-xs text-dark-text-tertiary">
        <span>
          <kbd className="px-1.5 py-0.5 bg-dark-hover rounded">Enter</kbd> to send
        </span>
      </div>
    </div>
  )
}
