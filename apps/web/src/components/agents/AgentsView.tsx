'use client'

import { motion } from 'framer-motion'
import { AGENTS, DEPARTMENTS } from '@/lib/constants'
import { Users, ArrowRight } from 'lucide-react'
import Link from 'next/link'

export function AgentsView() {
  return (
    <div className="h-full flex flex-col overflow-hidden">
      {/* Header */}
      <div className="border-b border-dark-border bg-dark-surface p-6">
        <div className="max-w-5xl mx-auto">
          <h1 className="text-2xl font-bold flex items-center gap-2 text-white">
            <Users className="w-6 h-6 text-white" />
            AI Agents
          </h1>
          <p className="text-dark-text-secondary mt-2">
            Explore and chat with specialized AI agents for different tasks
          </p>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-6">
        <div className="max-w-5xl mx-auto space-y-8">
          {DEPARTMENTS.map((dept, deptIndex) => (
            <motion.div
              key={dept.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: deptIndex * 0.1 }}
            >
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-ai bg-dark-hover border border-dark-border flex items-center justify-center">
                  <dept.icon className="w-5 h-5 text-white" />
                </div>
                <div>
                  <h2 className="text-xl font-semibold text-white">{dept.name}</h2>
                  <p className="text-sm text-dark-text-tertiary">{dept.description}</p>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {dept.agents.map((agentId, agentIndex) => {
                  const agent = AGENTS.find(a => a.id === agentId)
                  if (!agent) return null

                  return (
                    <motion.div
                      key={agent.id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: (deptIndex * 0.1) + (agentIndex * 0.05) }}
                    >
                      <Link
                        href={`/agent/${agent.id}`}
                        className="card p-5 hover:border-white/30 transition-all group block h-full"
                      >
                        <div className="flex items-start gap-4 mb-3">
                          <div className="w-12 h-12 rounded-ai bg-dark-hover border border-dark-border flex items-center justify-center group-hover:bg-white/10 transition-colors">
                            <agent.icon className="w-6 h-6 text-white" />
                          </div>
                          <div className="flex-1 min-w-0">
                            <h3 className="font-semibold text-white mb-1 group-hover:text-white transition-colors flex items-center gap-2">
                              {agent.name}
                              <ArrowRight className="w-4 h-4 opacity-0 group-hover:opacity-100 transition-opacity" />
                            </h3>
                            <p className="text-sm text-dark-text-secondary line-clamp-2">
                              {agent.description}
                            </p>
                          </div>
                        </div>
                      </Link>
                    </motion.div>
                  )
                })}
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  )
}
