/**
 * Shared constants across all apps
 */

export const AGENTS = [
  {
    id: 'product_manager',
    name: 'Product Manager',
    description: 'Analyzes trends, creates product insights, and manages roadmaps',
    icon: '🎯',
    color: '#4F9EFF',
    status: 'active',
  },
  {
    id: 'finance_manager',
    name: 'Finance Manager',
    description: 'Handles budgets, forecasts, and financial planning',
    icon: '💰',
    color: '#10B981',
    status: 'active',
  },
  {
    id: 'marketing_strategist',
    name: 'Marketing Strategist',
    description: 'Creates marketing content and campaign strategies',
    icon: '📱',
    color: '#F59E0B',
    status: 'active',
  },
  {
    id: 'leadgen_scraper',
    name: 'Lead Generator',
    description: 'Scrapes and collects qualified leads',
    icon: '🔍',
    color: '#8B5CF6',
    status: 'active',
  },
  {
    id: 'outbound_emailer',
    name: 'Outbound Emailer',
    description: 'Manages email campaigns and personalization',
    icon: '📧',
    color: '#EC4899',
    status: 'active',
  },
  {
    id: 'booking_callprep',
    name: 'Call Prep Agent',
    description: 'Prepares call scripts and manages bookings',
    icon: '📞',
    color: '#06B6D4',
    status: 'active',
  },
  {
    id: 'engineer',
    name: 'Engineer Agent',
    description: 'Handles technical issues and system monitoring',
    icon: '⚙️',
    color: '#EF4444',
    status: 'active',
  },
] as const

export const API_ENDPOINTS = {
  AGENTS: '/api/agents',
  TASKS: '/api/tasks',
  SHEETS: '/api/sheets',
  CALENDAR: '/api/calendar',
  WEBHOOKS: '/api/webhooks',
} as const
