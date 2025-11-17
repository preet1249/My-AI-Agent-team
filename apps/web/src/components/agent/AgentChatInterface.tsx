'use client'

import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { ChatInput } from '../chat/ChatInput'
import { ChatMessage } from '../chat/ChatMessage'
import { Agent, Message } from '@/types'
import { nanoid } from 'nanoid'
import { ArrowLeft } from 'lucide-react'
import Link from 'next/link'

interface AgentChatInterfaceProps {
  agent: Agent
}

export function AgentChatInterface({ agent }: AgentChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Load messages from localStorage for this agent
  useEffect(() => {
    const savedMessages = localStorage.getItem(`agent_${agent.id}_messages`)
    if (savedMessages) {
      const parsed = JSON.parse(savedMessages)
      setMessages(parsed.map((msg: any) => ({
        ...msg,
        timestamp: new Date(msg.timestamp)
      })))
    }
  }, [agent.id])

  // Save messages to localStorage whenever they change
  useEffect(() => {
    if (messages.length > 0) {
      localStorage.setItem(`agent_${agent.id}_messages`, JSON.stringify(messages))
    }
  }, [messages, agent.id])

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
      agentType: agent.id,
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

    // Simulate AI response from this specific agent
    setTimeout(() => {
      const assistantMessage: Message = {
        id: nanoid(),
        role: 'assistant',
        content: `As your ${agent.name}, I'll help you with ${content.toLowerCase()}. ${agent.description}`,
        timestamp: new Date(),
        agentType: agent.id,
      }
      setMessages((prev) => [...prev, assistantMessage])
      setIsLoading(false)
    }, 1500)
  }

  return (
    <div className="h-full flex flex-col relative">
      {/* Agent Header */}
      <div className="border-b border-dark-border bg-dark-surface px-6 py-4">
        <div className="max-w-4xl mx-auto flex items-center gap-4">
          <Link href="/" className="btn-icon">
            <ArrowLeft className="w-5 h-5 text-white" />
          </Link>
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-ai bg-dark-hover border border-dark-border flex items-center justify-center">
              <agent.icon className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-lg font-semibold text-white">{agent.name}</h1>
              <p className="text-sm text-dark-text-tertiary">{agent.description}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto">
        {messages.length === 0 ? (
          <div className="h-full flex items-center justify-center px-4">
            <div className="text-center max-w-md">
              <div className="w-16 h-16 mx-auto mb-4 rounded-ai-lg bg-dark-hover border border-dark-border flex items-center justify-center">
                <agent.icon className="w-8 h-8 text-white" />
              </div>
              <h2 className="text-xl font-semibold text-white mb-2">
                Chat with {agent.name}
              </h2>
              <p className="text-dark-text-secondary">
                {agent.description}. Start a conversation below.
              </p>
            </div>
          </div>
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

      {/* Input Area */}
      <div className="border-t border-dark-border bg-dark-bg py-6">
        <div className="max-w-4xl mx-auto px-4">
          <ChatInput onSend={handleSendMessage} disabled={isLoading} />
        </div>
      </div>
    </div>
  )
}
