'use client'

import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { ChatInput } from './ChatInput'
import { ChatMessage } from './ChatMessage'
import { WelcomeScreen } from './WelcomeScreen'
import { Message } from '@/types'
import { nanoid } from 'nanoid'

interface ChatInterfaceProps {
  conversationId?: string
}

export function ChatInterface({ conversationId }: ChatInterfaceProps = {}) {
  const [messages, setMessages] = useState<Message[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Load messages from localStorage
  useEffect(() => {
    const storageKey = conversationId ? `conversation_${conversationId}` : 'main_conversation'
    const savedMessages = localStorage.getItem(storageKey)
    if (savedMessages) {
      const parsed = JSON.parse(savedMessages)
      setMessages(parsed.map((msg: any) => ({
        ...msg,
        timestamp: new Date(msg.timestamp)
      })))
    }
  }, [conversationId])

  // Save messages to localStorage whenever they change
  useEffect(() => {
    if (messages.length > 0) {
      const storageKey = conversationId ? `conversation_${conversationId}` : 'main_conversation'
      localStorage.setItem(storageKey, JSON.stringify(messages))
    }
  }, [messages, conversationId])

  const handleSendMessage = async (
    content: string,
    attachments?: File[],
    mentionedAgent?: string
  ) => {
    if (!content.trim() && !attachments?.length) return

    const userMessage: Message = {
      id: nanoid(),
      role: 'user',
      content,
      timestamp: new Date(),
      agentType: mentionedAgent as any,
      attachments: attachments?.map((file) => ({
        id: nanoid(),
        type: file.type.startsWith('image/') ? 'image' : 'document',
        name: file.name,
        url: URL.createObjectURL(file),
        size: file.size,
      })),
    }

    setMessages((prev) => [...prev, userMessage])
    setIsLoading(true)

    // Simulate AI response (replace with actual API call)
    setTimeout(() => {
      const assistantMessage: Message = {
        id: nanoid(),
        role: 'assistant',
        content: `I understand you want to ${content.toLowerCase()}. I'll help you with that using ${
          mentionedAgent || 'our general AI'
        }.`,
        timestamp: new Date(),
        agentType: mentionedAgent as any,
      }
      setMessages((prev) => [...prev, assistantMessage])
      setIsLoading(false)
    }, 1500)
  }

  const handleThink = async (query: string) => {
    if (!query.trim()) return

    const userMessage: Message = {
      id: nanoid(),
      role: 'user',
      content: query,
      timestamp: new Date(),
      agentType: 'think' as any,
    }

    setMessages((prev) => [...prev, userMessage])
    setIsLoading(true)

    // Call Think Mode API (DuckDuckGo search + analysis)
    setTimeout(() => {
      const assistantMessage: Message = {
        id: nanoid(),
        role: 'assistant',
        content: `🔍 **Think Mode Activated**\n\nSearching the web for: "${query}"\n\nI'm using DuckDuckGo to search and analyze the latest information. This will include web scraping and intelligent analysis of the results.\n\n*This is a simulated response. Connect to backend /api/think endpoint for real results.*`,
        timestamp: new Date(),
        agentType: 'think' as any,
      }
      setMessages((prev) => [...prev, assistantMessage])
      setIsLoading(false)
    }, 2000)
  }

  return (
    <div className="h-full flex flex-col relative">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto">
        {messages.length === 0 ? (
          <WelcomeScreen onQuickAction={handleSendMessage} />
        ) : (
          <div className="max-w-4xl mx-auto px-4 py-6 space-y-6">
            <AnimatePresence mode="popLayout">
              {messages.map((message, index) => (
                <ChatMessage key={message.id} message={message} index={index} />
              ))}
            </AnimatePresence>

            {isLoading && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex items-center gap-3"
              >
                <div className="w-8 h-8 rounded-full bg-dark-hover border border-dark-border flex items-center justify-center">
                  <div className="w-2 h-2 bg-white rounded-full animate-pulse" />
                </div>
                <div className="flex gap-1">
                  <div className="w-2 h-2 bg-white rounded-full animate-bounce [animation-delay:-0.3s]" />
                  <div className="w-2 h-2 bg-white rounded-full animate-bounce [animation-delay:-0.15s]" />
                  <div className="w-2 h-2 bg-white rounded-full animate-bounce" />
                </div>
              </motion.div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input Area - Centered */}
      <div className="border-t border-dark-border bg-dark-bg py-6">
        <div className="max-w-4xl mx-auto px-4">
          <ChatInput
            onSend={handleSendMessage}
            onThink={handleThink}
            disabled={isLoading}
          />
        </div>
      </div>
    </div>
  )
}
