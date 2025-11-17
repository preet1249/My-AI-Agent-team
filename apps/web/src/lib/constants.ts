import { Agent, Department } from '@/types'

export const AGENTS: Agent[] = [
  {
    id: 'product_manager',
    name: 'Product Manager',
    description: 'Analyzes trends, creates product insights, and manages roadmaps',
    icon: '🎯',
    color: '#4F9EFF',
  },
  {
    id: 'finance_manager',
    name: 'Finance Manager',
    description: 'Handles budgets, forecasts, and financial planning',
    icon: '💰',
    color: '#10B981',
  },
  {
    id: 'marketing_strategist',
    name: 'Marketing Strategist',
    description: 'Creates marketing content and campaign strategies',
    icon: '📱',
    color: '#F59E0B',
  },
  {
    id: 'leadgen_scraper',
    name: 'Lead Generator',
    description: 'Scrapes and collects qualified leads',
    icon: '🔍',
    color: '#8B5CF6',
  },
  {
    id: 'outbound_emailer',
    name: 'Outbound Emailer',
    description: 'Manages email campaigns and personalization',
    icon: '📧',
    color: '#EC4899',
  },
  {
    id: 'booking_callprep',
    name: 'Call Prep Agent',
    description: 'Prepares call scripts and manages bookings',
    icon: '📞',
    color: '#06B6D4',
  },
  {
    id: 'engineer',
    name: 'Engineer Agent',
    description: 'Handles technical issues and system monitoring',
    icon: '⚙️',
    color: '#EF4444',
  },
]

export const DEPARTMENTS: Department[] = [
  {
    id: 'product',
    name: 'Product',
    icon: '🎯',
    description: 'Product management and insights',
    agents: ['product_manager'],
  },
  {
    id: 'finance',
    name: 'Finance',
    icon: '💰',
    description: 'Financial planning and budgets',
    agents: ['finance_manager'],
  },
  {
    id: 'marketing',
    name: 'Marketing',
    icon: '📱',
    description: 'Marketing and content creation',
    agents: ['marketing_strategist'],
  },
  {
    id: 'sales',
    name: 'Sales',
    icon: '💼',
    description: 'Lead generation and outreach',
    agents: ['leadgen_scraper', 'outbound_emailer', 'booking_callprep'],
  },
  {
    id: 'engineering',
    name: 'Engineering',
    icon: '⚙️',
    description: 'Technical support and monitoring',
    agents: ['engineer'],
  },
]

export const QUICK_ACTIONS = [
  {
    id: 'trend-analysis',
    label: 'Analyze Trends',
    icon: '📊',
    agent: 'product_manager' as const,
  },
  {
    id: 'generate-leads',
    label: 'Generate Leads',
    icon: '🎯',
    agent: 'leadgen_scraper' as const,
  },
  {
    id: 'create-campaign',
    label: 'Create Campaign',
    icon: '📧',
    agent: 'marketing_strategist' as const,
  },
  {
    id: 'budget-plan',
    label: 'Budget Planning',
    icon: '💰',
    agent: 'finance_manager' as const,
  },
]
