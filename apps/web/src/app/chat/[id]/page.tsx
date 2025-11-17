'use client'

import { useParams } from 'next/navigation'
import { MainLayout } from '@/components/layouts/MainLayout'
import { ChatInterface } from '@/components/chat/ChatInterface'

export default function ChatPage() {
  const params = useParams()
  const chatId = params.id as string

  return (
    <MainLayout>
      <ChatInterface conversationId={chatId} />
    </MainLayout>
  )
}
