import type { Config } from 'tailwindcss'
import typography from '@tailwindcss/typography'

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        poppins: ['var(--font-poppins)', 'sans-serif'],
      },
      colors: {
        dark: {
          bg: '#0F0F0F',
          surface: '#1A1A1A',
          hover: '#252525',
          border: '#2D2D2D',
          text: {
            primary: '#E8E8E8',
            secondary: '#A0A0A0',
            tertiary: '#707070',
          },
        },
        brand: {
          primary: '#FFFFFF',
          secondary: '#E8E8E8',
          accent: '#A0A0A0',
        },
      },
      borderRadius: {
        'ai': '10px',
        'ai-sm': '9px',
        'ai-lg': '12px',
      },
      animation: {
        'fade-in': 'fadeIn 0.3s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
      },
    },
  },
  plugins: [typography],
}

export default config
