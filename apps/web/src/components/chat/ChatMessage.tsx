'use client'

import { Message } from '@/types'
import { motion } from 'framer-motion'
import { User, Sparkles, Image as ImageIcon, FileText, Copy, Check } from 'lucide-react'
import { AGENTS } from '@/lib/constants'
import Image from 'next/image'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { oneDark } from 'react-syntax-highlighter/dist/cjs/styles/prism'
import { useState } from 'react'

interface ChatMessageProps {
  message: Message
  index: number
}

export function ChatMessage({ message, index }: ChatMessageProps) {
  const isUser = message.role === 'user'
  const agent = message.agentType
    ? AGENTS.find((a) => a.id === message.agentType)
    : null
  const [copiedCode, setCopiedCode] = useState<string | null>(null)

  const copyToClipboard = async (code: string) => {
    await navigator.clipboard.writeText(code)
    setCopiedCode(code)
    setTimeout(() => setCopiedCode(null), 2000)
  }

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
          <div className="w-8 h-8 rounded-full bg-dark-hover border border-dark-border flex items-center justify-center">
            <User className="w-4 h-4 text-white" />
          </div>
        ) : (
          <div className="w-8 h-8 rounded-full bg-dark-hover border border-dark-border flex items-center justify-center">
            {agent ? (
              <agent.icon className="w-4 h-4 text-white" />
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
              ? 'bg-white text-dark-bg'
              : 'bg-dark-surface border border-dark-border text-dark-text-primary'
          }`}
        >
          <div className="text-sm leading-relaxed prose prose-invert prose-sm max-w-none">
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={{
                code({ node, className, children, ...props }) {
                  const match = /language-(\w+)/.exec(className || '')
                  const codeString = String(children).replace(/\n$/, '')

                  if (match) {
                    return (
                      <div className="relative group my-3">
                        <div className="absolute right-2 top-2 opacity-0 group-hover:opacity-100 transition-opacity">
                          <button
                            onClick={() => copyToClipboard(codeString)}
                            className="p-1.5 rounded bg-dark-hover hover:bg-dark-border transition-colors"
                          >
                            {copiedCode === codeString ? (
                              <Check className="w-3.5 h-3.5 text-green-400" />
                            ) : (
                              <Copy className="w-3.5 h-3.5 text-dark-text-tertiary" />
                            )}
                          </button>
                        </div>
                        <SyntaxHighlighter
                          style={oneDark}
                          language={match[1]}
                          PreTag="div"
                          customStyle={{
                            margin: 0,
                            borderRadius: '8px',
                            fontSize: '12px',
                          }}
                          {...props}
                        >
                          {codeString}
                        </SyntaxHighlighter>
                      </div>
                    )
                  }

                  return (
                    <code className="bg-dark-hover px-1.5 py-0.5 rounded text-xs font-mono" {...props}>
                      {children}
                    </code>
                  )
                },
                h1: ({ children }) => <h1 className="text-xl font-bold mt-4 mb-2">{children}</h1>,
                h2: ({ children }) => <h2 className="text-lg font-bold mt-3 mb-2">{children}</h2>,
                h3: ({ children }) => <h3 className="text-base font-semibold mt-3 mb-1">{children}</h3>,
                p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
                ul: ({ children }) => <ul className="list-disc pl-4 mb-2">{children}</ul>,
                ol: ({ children }) => <ol className="list-decimal pl-4 mb-2">{children}</ol>,
                li: ({ children }) => <li className="mb-1">{children}</li>,
                a: ({ href, children }) => (
                  <a href={href} target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:underline">
                    {children}
                  </a>
                ),
                blockquote: ({ children }) => (
                  <blockquote className="border-l-2 border-dark-border pl-3 italic text-dark-text-secondary my-2">
                    {children}
                  </blockquote>
                ),
                table: ({ children }) => (
                  <div className="overflow-x-auto my-2">
                    <table className="min-w-full border border-dark-border rounded">{children}</table>
                  </div>
                ),
                th: ({ children }) => <th className="border border-dark-border px-3 py-1.5 bg-dark-hover font-semibold">{children}</th>,
                td: ({ children }) => <td className="border border-dark-border px-3 py-1.5">{children}</td>,
                strong: ({ children }) => <strong className="font-bold">{children}</strong>,
                em: ({ children }) => <em className="italic">{children}</em>,
              }}
            >
              {message.content}
            </ReactMarkdown>
          </div>
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
