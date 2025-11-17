import { MainLayout } from '@/components/layouts/MainLayout'
import { ChatInterface } from '@/components/chat/ChatInterface'

export default function HomePage() {
  return (
    <MainLayout>
      <ChatInterface />
    </MainLayout>
  )
}
