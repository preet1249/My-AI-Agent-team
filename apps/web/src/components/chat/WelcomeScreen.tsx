'use client'

import { motion } from 'framer-motion'
import { QUICK_ACTIONS } from '@/lib/constants'
import { Sparkles } from 'lucide-react'

interface WelcomeScreenProps {
  onQuickAction: (prompt: string) => void
}

export function WelcomeScreen({ onQuickAction }: WelcomeScreenProps) {
  const userName = 'Preet' // This should come from user context

  return (
    <div className="h-full flex items-center justify-center px-4">
      <div className="max-w-3xl w-full">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="text-center space-y-8"
        >
          {/* Greeting */}
          <div className="space-y-3">
            <div className="flex items-center justify-center gap-3 mb-6">
              <div className="w-16 h-16 rounded-ai-lg bg-gradient-to-br from-brand-primary via-brand-secondary to-brand-accent flex items-center justify-center animate-pulse-slow">
                <Sparkles className="w-8 h-8 text-white" />
              </div>
            </div>
            <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-brand-primary via-brand-secondary to-brand-accent bg-clip-text text-transparent">
              Hello, {userName}
            </h1>
            <p className="text-lg text-dark-text-secondary">
              How can I help you today?
            </p>
          </div>

          {/* Quick Actions */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2, duration: 0.5 }}
            className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3"
          >
            {QUICK_ACTIONS.map((action, index) => (
              <motion.button
                key={action.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 * index, duration: 0.4 }}
                whileHover={{ scale: 1.02, y: -2 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => onQuickAction(action.label)}
                className="p-4 bg-dark-surface border border-dark-border rounded-ai-lg hover:border-brand-primary/50 hover:bg-dark-hover transition-all group"
              >
                <div className="text-3xl mb-2 group-hover:scale-110 transition-transform">
                  {action.icon}
                </div>
                <p className="text-sm font-medium text-dark-text-primary group-hover:text-brand-primary transition-colors">
                  {action.label}
                </p>
              </motion.button>
            ))}
          </motion.div>

          {/* Suggestions */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.4, duration: 0.5 }}
            className="pt-8 space-y-3"
          >
            <p className="text-sm text-dark-text-tertiary font-medium">
              Or try asking:
            </p>
            <div className="flex flex-wrap gap-2 justify-center">
              {[
                'Generate leads for SaaS niche',
                'Create a marketing campaign',
                'Analyze product trends',
                'Prepare monthly budget',
              ].map((suggestion) => (
                <button
                  key={suggestion}
                  onClick={() => onQuickAction(suggestion)}
                  className="px-4 py-2 bg-dark-surface/50 border border-dark-border rounded-ai text-sm text-dark-text-secondary hover:text-dark-text-primary hover:border-brand-primary/50 hover:bg-dark-surface transition-all"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </motion.div>

          {/* Footer Note */}
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.6, duration: 0.5 }}
            className="text-xs text-dark-text-tertiary pt-4"
          >
            Use <span className="text-brand-primary font-medium">@</span> to mention specific agents or ask me anything
          </motion.p>
        </motion.div>
      </div>
    </div>
  )
}
