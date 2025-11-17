import { LucideIcon } from 'lucide-react'

export type AgentType =
  | 'product_manager'
  | 'finance_manager'
  | 'marketing_strategist'
  | 'leadgen_scraper'
  | 'outbound_emailer'
  | 'booking_callprep'
  | 'engineer'

export interface Agent {
  id: AgentType
  name: string
  description: string
  icon: LucideIcon
  color: string
}

export interface Message {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: Date
  agentType?: AgentType
  attachments?: Attachment[]
  metadata?: Record<string, any>
}

export interface Attachment {
  id: string
  type: 'image' | 'document' | 'file'
  name: string
  url: string
  size: number
  extractedText?: string
}

export interface Conversation {
  id: string
  title: string
  preview: string
  lastMessage: Date
  agentType?: AgentType
  messages: Message[]
  createdAt: Date
  updatedAt: Date
}

export interface Sheet {
  id: string
  name: string
  type: 'leads' | 'tasks' | 'insights' | 'custom'
  columns: SheetColumn[]
  rows: SheetRow[]
  createdAt: Date
  updatedAt: Date
}

export interface SheetColumn {
  id: string
  name: string
  type: 'text' | 'number' | 'date' | 'select' | 'multiselect' | 'url' | 'email'
  options?: string[]
}

export interface SheetRow {
  id: string
  data: Record<string, any>
  createdAt: Date
  updatedAt: Date
}

export interface CalendarEvent {
  id: string
  title: string
  description?: string
  startTime: Date
  endTime: Date
  type: 'call' | 'task' | 'meeting' | 'reminder'
  metadata?: Record<string, any>
  status: 'pending' | 'completed' | 'cancelled'
}

export interface Department {
  id: string
  name: string
  icon: LucideIcon
  description: string
  agents: AgentType[]
}
