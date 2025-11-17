'use client'

import { motion } from 'framer-motion'

interface WelcomeScreenProps {
  onQuickAction: (prompt: string) => void
}

export function WelcomeScreen({ onQuickAction }: WelcomeScreenProps) {
  const userName = 'Preet' // This should come from user context

  return (
    <div className="h-full flex flex-col">
      <div className="px-6 py-8 border-b border-dark-border">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <h1 className="text-3xl font-semibold text-white">
            Hello, {userName}
          </h1>
        </motion.div>
      </div>
      <div className="flex-1 flex items-center justify-center px-4">
        <p className="text-lg text-dark-text-tertiary">
          Start a conversation...
        </p>
      </div>
    </div>
  )
}
