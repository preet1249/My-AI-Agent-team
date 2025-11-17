'use client'

import { useParams } from 'next/navigation'
import { MainLayout } from '@/components/layouts/MainLayout'
import { AgentChatInterface } from '@/components/agent/AgentChatInterface'
import { AGENTS } from '@/lib/constants'
import { notFound } from 'next/navigation'

export default function AgentPage() {
  const params = useParams()
  const agentId = params.id as string

  const agent = AGENTS.find(a => a.id === agentId)

  if (!agent) {
    notFound()
  }

  return (
    <MainLayout>
      <AgentChatInterface agent={agent} />
    </MainLayout>
  )
}
