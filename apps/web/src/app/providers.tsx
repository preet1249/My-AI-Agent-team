'use client'

import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from 'react-hot-toast'
import { useState } from 'react'

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 60 * 1000,
            refetchOnWindowFocus: false,
          },
        },
      })
  )

  return (
    <QueryClientProvider client={queryClient}>
      {children}
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 3000,
          style: {
            background: '#1A1A1A',
            color: '#E8E8E8',
            border: '1px solid #2D2D2D',
            borderRadius: '10px',
            fontSize: '14px',
            fontFamily: 'var(--font-poppins)',
          },
          success: {
            iconTheme: {
              primary: '#4F9EFF',
              secondary: '#E8E8E8',
            },
          },
          error: {
            iconTheme: {
              primary: '#FF6B9D',
              secondary: '#E8E8E8',
            },
          },
        }}
      />
    </QueryClientProvider>
  )
}
