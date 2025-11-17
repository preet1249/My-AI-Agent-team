/**
 * Shared TypeScript types across all apps
 */

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
  icon: string
  color: string
  status: 'active' | 'busy' | 'offline'
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

export interface Task {
  id: string
  user_id?: string
  agent_name: AgentType
  status: 'queued' | 'processing' | 'completed' | 'failed'
  progress: number
  input: any
  output?: any
  created_at: Date
  updated_at: Date
}

export interface Sheet {
  id: string
  name: string
  type: 'leads' | 'tasks' | 'insights' | 'custom'
  columns: SheetColumn[]
  rows: SheetRow[]
  created_at: Date
  updated_at: Date
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
  created_at: Date
  updated_at: Date
}

export interface CalendarEvent {
  id: string
  title: string
  description?: string
  start_time: Date
  end_time: Date
  type: 'call' | 'task' | 'meeting' | 'reminder'
  metadata?: Record<string, any>
  status: 'pending' | 'completed' | 'cancelled'
}
