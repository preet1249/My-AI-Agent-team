import { Agent, Department } from '@/types'
import { Target, DollarSign, Megaphone, Search, Mail, Phone, Settings, BarChart3, TrendingUp, Briefcase, Code } from 'lucide-react'

export const AGENTS: Agent[] = [
  {
    id: 'product_manager',
    name: 'Product Manager',
    description: 'Analyzes trends, creates product insights, and manages roadmaps',
    icon: Target,
    color: '#FFFFFF',
  },
  {
    id: 'finance_manager',
    name: 'Finance Manager',
    description: 'Handles budgets, forecasts, and financial planning',
    icon: DollarSign,
    color: '#FFFFFF',
  },
  {
    id: 'marketing_strategist',
    name: 'Marketing Strategist',
    description: 'Creates marketing content and campaign strategies',
    icon: Megaphone,
    color: '#FFFFFF',
  },
  {
    id: 'leadgen_scraper',
    name: 'Lead Generator',
    description: 'Scrapes and collects qualified leads',
    icon: Search,
    color: '#FFFFFF',
  },
  {
    id: 'outbound_emailer',
    name: 'Outbound Emailer',
    description: 'Manages email campaigns and personalization',
    icon: Mail,
    color: '#FFFFFF',
  },
  {
    id: 'booking_callprep',
    name: 'Call Prep Agent',
    description: 'Prepares call scripts and manages bookings',
    icon: Phone,
    color: '#FFFFFF',
  },
  {
    id: 'engineer',
    name: 'Engineer Agent',
    description: 'Handles technical issues and system monitoring',
    icon: Code,
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
