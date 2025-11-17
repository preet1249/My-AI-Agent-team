# AI Agent Team

A powerful multi-agent AI system for business automation with a beautiful ChatGPT-like interface.

## Features

- 🤖 **7 Specialized AI Agents**
  - Product Manager
  - Finance Manager
  - Marketing Strategist
  - Lead Generator
  - Outbound Emailer
  - Call Prep Agent
  - Engineer Agent

- 💬 **ChatGPT-like Interface**
  - Dark theme with Poppins font
  - @ mention system for agent selection
  - Image upload with OCR support
  - Real-time chat interface

- 📊 **Built-in Tools**
  - Custom Sheets (Notion-like tables)
  - Calendar for tasks and calls
  - History tracking
  - Document management

- 🎨 **Beautiful UI/UX**
  - Dark theme optimized
  - 9-12px border radius design system
  - Smooth animations with Framer Motion
  - Responsive mobile-first design

## Tech Stack

### Frontend
- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: TailwindCSS
- **Animations**: Framer Motion
- **Icons**: Lucide React
- **State Management**: Zustand
- **Data Fetching**: TanStack Query

### Backend (Coming Soon)
- **API**: FastAPI (Python)
- **Queue**: Redis/Upstash
- **Database**: Supabase (Postgres)
- **Workers**: Python Worker Pool
- **LLMs**: OpenRouter (NVIDIA NeMo + Claude 3 Haiku)

## Getting Started

### Prerequisites

- Node.js 18+ installed
- pnpm 8+ installed (recommended) or npm

### Installation

1. **Clone the repository**
   ```bash
   cd "C:\Users\mt\AI Agents\AI Agent Team"
   ```

2. **Install dependencies**
   ```bash
   pnpm install
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env.local
   ```

   Edit `.env.local` and add your credentials:
   - Supabase URL and keys
   - OpenRouter API key
   - Gmail API credentials (optional)
   - Redis URL (optional)

4. **Run the development server**
   ```bash
   pnpm dev
   ```

5. **Open your browser**
   Navigate to [http://localhost:3000](http://localhost:3000)

## Project Structure

```
AI Agent Team/
├── apps/
│   └── web/                 # Next.js frontend application
│       ├── src/
│       │   ├── app/        # Next.js app router pages
│       │   ├── components/ # React components
│       │   ├── lib/        # Utilities and constants
│       │   ├── types/      # TypeScript types
│       │   └── styles/     # Global styles
│       ├── public/         # Static assets
│       └── package.json
├── packages/               # Shared packages (future)
│   ├── ui/                # Shared UI components
│   └── lib/               # Shared utilities
├── .env.example           # Environment variables template
├── .gitignore            # Git ignore rules
├── package.json          # Root package.json
├── pnpm-workspace.yaml   # pnpm workspace config
├── turbo.json           # Turborepo configuration
└── README.md            # This file
```

## Available Scripts

### Development
```bash
pnpm dev          # Start development server
pnpm build        # Build for production
pnpm start        # Start production server
pnpm lint         # Run ESLint
pnpm format       # Format code with Prettier
```

### Workspace Commands
```bash
pnpm dev          # Run dev in all workspaces
pnpm build        # Build all workspaces
pnpm clean        # Clean all build artifacts
```

## Features Guide

### 1. Chat Interface
- Type your message in the chat input
- Use `@` to mention specific agents
- Upload images for OCR analysis
- Press Enter to send, Shift+Enter for new line

### 2. Agents
- Click on departments in the sidebar to view agents
- Each agent has specialized capabilities
- Agents can work together on complex tasks

### 3. Sheets
- Create custom tables like Notion
- Import/export data as CSV
- Filter and search functionality
- Different column types (text, number, date, select)

### 4. Calendar
- View all tasks and scheduled calls
- Create new events
- Integrate with external calendars via API

### 5. History
- View all past conversations
- Search and filter
- Resume previous chats

## Design System

- **Font**: Poppins (300, 400, 500, 600, 700)
- **Border Radius**: 9-12px
- **Theme**: Dark mode optimized
- **Colors**:
  - Primary: #4F9EFF
  - Secondary: #7B61FF
  - Accent: #FF6B9D
  - Background: #0F0F0F
  - Surface: #1A1A1A

## Cost Optimization

This system is designed to run on free tiers:

- ✅ Supabase Free Tier
- ✅ Vercel Free Tier
- ✅ Upstash Redis Free Tier
- ✅ Gmail API (Free within quotas)
- ⚠️ OpenRouter API (Pay per use for LLM calls)

**Total Cost**: ~$0 for infrastructure + LLM API usage costs

## Roadmap

- [ ] Backend API implementation (FastAPI)
- [ ] Real AI agent integration
- [ ] Supabase database setup
- [ ] Authentication with Supabase Auth
- [ ] Real-time updates with Supabase Realtime
- [ ] Gmail integration
- [ ] Lead scraping functionality
- [ ] Email campaign automation
- [ ] Mobile app (Expo/React Native)
- [ ] PWA support

## Contributing

This is a personal project. Feel free to fork and customize for your needs.

## License

Private - All rights reserved

## Support

For issues and questions, refer to the documentation in `Prompt.md` or create an issue in the repository.

---

**Built with ❤️ using Next.js, TypeScript, and TailwindCSS**
