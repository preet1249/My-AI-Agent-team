'use client'

import { useState } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import {
  PanelLeft,
  MessageSquarePlus,
  Sparkles,
  Clock,
  Table2,
  Calendar,
  FileText,
  Settings,
  ChevronRight,
  User,
} from 'lucide-react'
import { DEPARTMENTS, AGENTS } from '@/lib/constants'
import { motion } from 'framer-motion'

interface SidebarProps {
  onClose?: () => void
  mobile?: boolean
}

export function Sidebar({ onClose, mobile }: SidebarProps) {
  const pathname = usePathname()
  const [expandedDept, setExpandedDept] = useState<string | null>(null)

  const menuItems = [
    { icon: MessageSquarePlus, label: 'New Chat', href: '/', badge: null },
    { icon: Sparkles, label: 'Explore Agents', href: '/agents', badge: null },
  ]

  const recentChats = [
    { id: '1', title: 'Product design trends analysis', href: '/chat/1' },
    { id: '2', title: 'Lead generation for SaaS niche', href: '/chat/2' },
    { id: '3', title: 'Marketing campaign strategy', href: '/chat/3' },
  ]

  const workspaceItems = [
    { icon: Table2, label: 'Sheets', href: '/sheets' },
    { icon: Calendar, label: 'Calendar', href: '/calendar' },
    { icon: Clock, label: 'History', href: '/history' },
    { icon: FileText, label: 'Documents', href: '/documents' },
  ]

  return (
    <div className="h-full bg-dark-surface flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-dark-border flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-ai bg-gradient-to-br from-brand-primary to-brand-secondary flex items-center justify-center">
            <Sparkles className="w-4 h-4 text-white" />
          </div>
          <h1 className="font-semibold text-lg">AI Agent Team</h1>
        </div>
        {mobile && (
          <button onClick={onClose} className="btn-icon">
            <PanelLeft className="w-5 h-5" />
          </button>
        )}
      </div>

      {/* Scrollable Content */}
      <div className="flex-1 overflow-y-auto px-3 py-4 space-y-6">
        {/* Main Actions */}
        <div className="space-y-1">
          {menuItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              onClick={mobile ? onClose : undefined}
              className={`sidebar-item ${
                pathname === item.href ? 'sidebar-item-active' : ''
              }`}
            >
              <item.icon className="w-5 h-5 flex-shrink-0" />
              <span className="flex-1 text-sm font-medium">{item.label}</span>
              {item.badge && (
                <span className="px-2 py-0.5 text-xs bg-brand-primary/20 text-brand-primary rounded-ai-sm">
                  {item.badge}
                </span>
              )}
            </Link>
          ))}
        </div>

        {/* Departments */}
        <div>
          <h3 className="text-xs font-semibold text-dark-text-tertiary uppercase tracking-wider mb-2 px-3">
            Departments
          </h3>
          <div className="space-y-1">
            {DEPARTMENTS.map((dept) => (
              <div key={dept.id}>
                <button
                  onClick={() =>
                    setExpandedDept(expandedDept === dept.id ? null : dept.id)
                  }
                  className="sidebar-item w-full"
                >
                  <span className="text-lg">{dept.icon}</span>
                  <span className="flex-1 text-left text-sm font-medium">
                    {dept.name}
                  </span>
                  <ChevronRight
                    className={`w-4 h-4 transition-transform ${
                      expandedDept === dept.id ? 'rotate-90' : ''
                    }`}
                  />
                </button>
                {expandedDept === dept.id && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    className="ml-8 mt-1 space-y-1"
                  >
                    {dept.agents.map((agentId) => {
                      const agent = AGENTS.find((a) => a.id === agentId)
                      if (!agent) return null
                      return (
                        <Link
                          key={agent.id}
                          href={`/agent/${agent.id}`}
                          onClick={mobile ? onClose : undefined}
                          className="flex items-center gap-2 px-3 py-2 rounded-ai text-xs text-dark-text-secondary hover:bg-dark-hover hover:text-dark-text-primary transition-all"
                        >
                          <span>{agent.icon}</span>
                          <span>{agent.name}</span>
                        </Link>
                      )
                    })}
                  </motion.div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Workspace */}
        <div>
          <h3 className="text-xs font-semibold text-dark-text-tertiary uppercase tracking-wider mb-2 px-3">
            Workspace
          </h3>
          <div className="space-y-1">
            {workspaceItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                onClick={mobile ? onClose : undefined}
                className={`sidebar-item ${
                  pathname === item.href ? 'sidebar-item-active' : ''
                }`}
              >
                <item.icon className="w-5 h-5 flex-shrink-0" />
                <span className="text-sm font-medium">{item.label}</span>
              </Link>
            ))}
          </div>
        </div>

        {/* Recent Chats */}
        <div>
          <h3 className="text-xs font-semibold text-dark-text-tertiary uppercase tracking-wider mb-2 px-3">
            Recent
          </h3>
          <div className="space-y-1">
            {recentChats.map((chat) => (
              <Link
                key={chat.id}
                href={chat.href}
                onClick={mobile ? onClose : undefined}
                className="sidebar-item"
              >
                <MessageSquarePlus className="w-4 h-4 flex-shrink-0 opacity-50" />
                <span className="text-sm truncate">{chat.title}</span>
              </Link>
            ))}
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="border-t border-dark-border p-3">
        <Link href="/settings" className="sidebar-item">
          <Settings className="w-5 h-5" />
          <span className="text-sm font-medium">Settings</span>
        </Link>
        <div className="sidebar-item mt-1">
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-brand-primary to-brand-accent flex items-center justify-center">
            <User className="w-4 h-4 text-white" />
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium truncate">Your Name</p>
            <p className="text-xs text-dark-text-tertiary truncate">
              you@example.com
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
