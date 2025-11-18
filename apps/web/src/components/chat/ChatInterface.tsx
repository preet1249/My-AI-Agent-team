'use client'

import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { ChatInput } from './ChatInput'
import { ChatMessage } from './ChatMessage'
import { WelcomeScreen } from './WelcomeScreen'
import { Message } from '@/types'
import { nanoid } from 'nanoid'
import { API_URL } from '@/lib/constants'

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

    try {
      // Determine which agent endpoint to call
      const agentEndpoint = mentionedAgent
        ? `/api/agents/${mentionedAgent.replace('_', '-')}`
        : '/api/agents/personal-assistant'

      // Call real backend API
      const response = await fetch(`${API_URL}${agentEndpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: 'user-123', // Replace with actual user ID from auth
          prompt: content,
          context: {
            conversation_id: conversationId || 'default',
          },
        }),
      })

      if (!response.ok) {
        throw new Error(`API error: ${response.statusText}`)
      }

      const data = await response.json()

      // Backend returns: {success: true, data: {response: "...", ...}}
      const agentData = data.data || data
      const assistantMessage: Message = {
        id: nanoid(),
        role: 'assistant',
        content: agentData.response || agentData.output?.response || 'No response from agent',
        timestamp: new Date(),
        agentType: mentionedAgent as any,
      }

      setMessages((prev) => [...prev, assistantMessage])
    } catch (error) {
      console.error('Error calling agent:', error)

      const errorMessage: Message = {
        id: nanoid(),
        role: 'assistant',
        content: `❌ Error: ${error instanceof Error ? error.message : 'Failed to get response from agent'}. Please make sure the backend is running at ${API_URL}`,
        timestamp: new Date(),
        agentType: mentionedAgent as any,
      }

      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleThink = async (query: string) => {
    if (!query.trim()) return

    const userMessage: Message = {
      id: nanoid(),
      role: 'user',
      content: `🔍 ${query}`,
      timestamp: new Date(),
      agentType: 'think' as any,
    }

    setMessages((prev) => [...prev, userMessage])
    setIsLoading(true)

    try {
      // Call Think Mode API (DuckDuckGo search + analysis)
      const response = await fetch(`${API_URL}/api/think`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: 'user-123', // Replace with actual user ID from auth
          query: query,
          max_results: 5,
        }),
      })

      if (!response.ok) {
        throw new Error(`API error: ${response.statusText}`)
      }

      const data = await response.json()

      // Backend returns: {success: true, data: {response: "...", sources: [...], ...}}
      const thinkData = data.data || data

      // Format Think mode response with sources
      let thinkContent = `🔍 **Think Mode Results**\n\n`
      thinkContent += `**Answer:**\n${thinkData.response || thinkData.answer || 'No answer generated'}\n\n`

      if (thinkData.sources && thinkData.sources.length > 0) {
        thinkContent += `**Sources:**\n`
        thinkData.sources.forEach((source: any, index: number) => {
          thinkContent += `${index + 1}. [${source.title || 'Source'}](${source.url})\n`
        })
        thinkContent += `\n**Total sources:** ${thinkData.sources.length}`
      }

      if (thinkData.agent_used) {
        thinkContent += `\n\n*Analyzed by: ${thinkData.agent_used}*`
      }

      const assistantMessage: Message = {
        id: nanoid(),
        role: 'assistant',
        content: thinkContent,
        timestamp: new Date(),
        agentType: 'think' as any,
      }

      setMessages((prev) => [...prev, assistantMessage])
    } catch (error) {
      console.error('Error in Think mode:', error)

      const errorMessage: Message = {
        id: nanoid(),
        role: 'assistant',
        content: `❌ Think Mode Error: ${error instanceof Error ? error.message : 'Failed to search and analyze'}. Please make sure the backend is running at ${API_URL}`,
        timestamp: new Date(),
        agentType: 'think' as any,
      }

      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
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
