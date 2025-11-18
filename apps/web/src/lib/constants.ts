import { Agent, Department } from '@/types'
import { Target, DollarSign, Megaphone, Search, Mail, Phone, Settings, BarChart3, TrendingUp, Briefcase, Code, Sparkles } from 'lucide-react'

export const AGENTS: Agent[] = [
  {
    id: 'product_manager',
    name: 'Alex',
    fullTitle: 'Product Manager',
    description: 'Analyzes trends, creates product insights, and manages roadmaps',
    icon: Target,
    color: '#FFFFFF',
  },
  {
    id: 'finance_manager',
    name: 'Marcus',
    fullTitle: 'Finance Manager',
    description: 'Handles budgets, forecasts, and financial planning',
    icon: DollarSign,
    color: '#FFFFFF',
  },
  {
    id: 'marketing_strategist',
    name: 'Ryan',
    fullTitle: 'Marketing Strategist',
    description: 'Creates marketing content and campaign strategies',
    icon: Megaphone,
    color: '#FFFFFF',
  },
  {
    id: 'leadgen_scraper',
    name: 'Jake',
    fullTitle: 'Lead Generator',
    description: 'Scrapes and collects qualified leads',
    icon: Search,
    color: '#FFFFFF',
  },
  {
    id: 'outbound_emailer',
    name: 'Chris',
    fullTitle: 'Outbound Emailer',
    description: 'Manages email campaigns and personalization',
    icon: Mail,
    color: '#FFFFFF',
  },
  {
    id: 'booking_callprep',
    name: 'Daniel',
    fullTitle: 'Call Prep Agent',
    description: 'Prepares call scripts and manages bookings',
    icon: Phone,
    color: '#FFFFFF',
  },
  {
    id: 'engineer',
    name: 'Kevin',
    fullTitle: 'Engineer',
    description: 'Handles technical issues and system monitoring',
    icon: Code,
    color: '#FFFFFF',
  },
  {
    id: 'personal_assistant',
    name: 'Sophia',
    fullTitle: 'Personal AI Assistant',
    description: 'Your intelligent assistant with access to all data. Coordinates with all agents.',
    icon: Sparkles,
    color: '#FFFFFF',
  },
]

export const DEPARTMENTS: Department[] = [
  {
    id: 'product',
    name: 'Product',
    icon: Target,
    description: 'Product management and insights',
    agents: ['product_manager'],
  },
  {
    id: 'finance',
    name: 'Finance',
    icon: DollarSign,
    description: 'Financial planning and budgets',
    agents: ['finance_manager'],
  },
  {
    id: 'marketing',
    name: 'Marketing',
    icon: Megaphone,
    description: 'Marketing and content creation',
    agents: ['marketing_strategist'],
  },
  {
    id: 'sales',
    name: 'Sales',
    icon: Briefcase,
    description: 'Lead generation and outreach',
    agents: ['leadgen_scraper', 'outbound_emailer', 'booking_callprep'],
  },
  {
    id: 'engineering',
    name: 'Engineering',
    icon: Settings,
    description: 'Technical support and monitoring',
    agents: ['engineer'],
  },
  {
    id: 'assistant',
    name: 'Assistant',
    icon: Sparkles,
    description: 'Your personal AI assistant',
    agents: ['personal_assistant'],
  },
]

export const QUICK_ACTIONS = [
  {
    id: 'trend-analysis',
    label: 'Analyze Trends',
    icon: TrendingUp,
    agent: 'product_manager' as const,
  },
  {
    id: 'generate-leads',
    label: 'Generate Leads',
    icon: Target,
    agent: 'leadgen_scraper' as const,
  },
  {
    id: 'create-campaign',
    label: 'Create Campaign',
    icon: Mail,
    agent: 'marketing_strategist' as const,
  },
  {
    id: 'budget-plan',
    label: 'Budget Planning',
    icon: DollarSign,
    agent: 'finance_manager' as const,
  },
]
