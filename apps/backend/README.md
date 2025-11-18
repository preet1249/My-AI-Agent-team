# AI Agent Team Backend

Professional-grade FastAPI backend orchestrating 7 AI agents with webhooks, workers, and real-time database integration.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Frontend (Next.js)                   │
│              https://my-ai-agent-team-seven.vercel.app   │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              FastAPI Orchestrator (main.py)              │
│  ┌─────────────────────────────────────────────────┐   │
│  │  7 AI Agents:                                    │   │
│  │  • Product Manager (NVIDIA NeMo)                 │   │
│  │  • Finance Manager (NVIDIA NeMo)                 │   │
│  │  • Marketing Strategist (NVIDIA NeMo)            │   │
│  │  • Lead Gen Scraper (Claude Haiku)               │   │
│  │  • Outbound Emailer (Claude Haiku)               │   │
│  │  • Booking/Call Prep (Claude Haiku)              │   │
│  │  • Engineer (Claude Haiku)                       │   │
│  └─────────────────────────────────────────────────┘   │
│                                                          │
│  ┌─────────────────────────────────────────────────┐   │
│  │  4 Webhook Endpoints (HMAC Secured):            │   │
│  │  • /webhook/email - Gmail push notifications    │   │
│  │  • /webhook/calendar - Calendar updates         │   │
│  │  • /webhook/scrape - Scrape completions         │   │
│  │  • /webhook/task - Task completions             │   │
│  └─────────────────────────────────────────────────┘   │
└────────┬────────────────────────┬─────────────────────┘
         │                        │
         ▼                        ▼
┌──────────────────┐    ┌──────────────────┐
│  Scrape Worker   │    │   Email Worker   │
│  (Playwright)    │    │   (Gmail API)    │
└────────┬─────────┘    └────────┬─────────┘
         │                       │
         └───────────┬───────────┘
                     ▼
         ┌───────────────────────┐
         │   Redis/Upstash Queue │
         └───────────────────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │  Supabase (Postgres)  │
         │  • 11 Tables          │
         │  • RLS Policies       │
         │  • Realtime           │
         └───────────────────────┘
```

## 📁 Project Structure

```
apps/backend/
├── app/
│   ├── agents/                    # 7 AI agent handlers
│   │   ├── product_manager.py
│   │   ├── finance_manager.py
│   │   ├── marketing_strategist.py
│   │   ├── leadgen_scraper.py
│   │   ├── outbound_emailer.py
│   │   ├── booking_callprep.py
│   │   └── engineer.py
│   │
│   ├── webhooks/                  # 4 webhook endpoints
│   │   ├── email_webhook.py       # HMAC secured
│   │   ├── calendar_webhook.py
│   │   ├── scrape_webhook.py
│   │   └── task_webhook.py
│   │
│   ├── workers/                   # Background workers
│   │   ├── scrape_worker.py       # Web scraping with politeness
│   │   └── email_worker.py        # Gmail API email sending
│   │
│   ├── utils/                     # Utilities
│   │   ├── openrouter_client.py   # LLM API client
│   │   ├── gmail_client.py        # Gmail API wrapper
│   │   ├── toon_converter.py      # Token optimization (30-50% savings)
│   │   └── security.py            # HMAC, JWT, signatures
│   │
│   ├── config.py                  # Pydantic settings
│   ├── database.py                # Supabase client
│   ├── redis_client.py            # Redis queue manager
│   └── main.py                    # FastAPI application
│
├── supabase_schema.sql            # Complete database schema
├── BACKEND_IMPLEMENTATION_GUIDE.md
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd apps/backend
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

```bash
cp .env.example .env
# Edit .env with your credentials
```

Required credentials:
- **SUPABASE_URL** and **SUPABASE_KEY**: From Supabase dashboard
- **REDIS_URL**: From Upstash or local Redis
- **OPENROUTER_API_KEY**: From https://openrouter.ai
- **GMAIL_CREDENTIALS_JSON**: Service account JSON from Google Cloud
- **INTERNAL_SIGNING_KEY**: Generate with `openssl rand -hex 32`
- **WEBHOOK_SECRET**: Generate with `openssl rand -hex 32`

### 3. Set Up Database

```bash
# Run the schema SQL in your Supabase SQL editor
cat supabase_schema.sql
```

### 4. Run Locally

```bash
# Start orchestrator
uvicorn app.main:app --reload --port 8000

# In separate terminals, start workers:
python -m app.workers.scrape_worker
python -m app.workers.email_worker
```

### 5. Deploy with Docker

```bash
# Build and run all services
docker-compose up --build

# Or deploy to Render/Railway/Fly.io using Dockerfile
```

## 📡 API Endpoints

### Agent Endpoints

- `POST /api/agents/product-manager` - Analyze trends, create insights
- `POST /api/agents/finance-manager` - Financial analysis and budgeting
- `POST /api/agents/marketing-strategist` - Campaign creation and optimization
- `POST /api/agents/leadgen-scraper` - Web scraping for leads
- `POST /api/agents/outbound-emailer` - Send personalized emails
- `POST /api/agents/booking-callprep` - Schedule meetings, generate scripts
- `POST /api/agents/engineer` - Code generation and debugging

### Query Endpoints

- `GET /api/tasks/{user_id}` - Get user's agent tasks
- `GET /api/leads/{user_id}` - Get user's leads
- `GET /api/insights/{user_id}` - Get product insights
- `GET /api/campaigns/{user_id}` - Get marketing campaigns
- `GET /api/alerts/{user_id}` - Get user alerts

### Webhook Endpoints (HMAC Secured)

- `POST /webhook/email` - Gmail push notifications
- `POST /webhook/calendar` - Calendar event updates
- `POST /webhook/scrape` - Scrape job completions
- `POST /webhook/task` - Task completions from workers

## 🔐 Security Features

- **HMAC SHA256** signature verification for all webhooks
- **JWT** authentication for internal agent-to-agent calls
- **Constant-time** signature comparison to prevent timing attacks
- **Idempotency keys** to prevent duplicate operations
- **Row-level security** (RLS) policies in Supabase
- **Rate limiting** and concurrency controls

## 🎯 Key Features

### TOON Format Converter
Converts JSON to YAML-like format, saving 30-50% tokens in LLM calls:
```python
from app.utils.toon_converter import toon_converter

# Automatic token savings
savings = toon_converter.get_token_savings(data)
# {'json_tokens': 1000, 'toon_tokens': 650, 'savings_percent': 35}
```

### Politeness & Caching
- **Scraping delays**: 2-5 seconds between requests
- **Domain backoff**: Temporary blocking after failures
- **Cache TTL**: 24 hours for scrapes and model calls
- **Retry logic**: Exponential backoff with 3 retries

### Agent Task Tracking
All agent operations are tracked in `agent_tasks` table:
- Idempotent with `external_id`
- Full input/output logging
- Status tracking (queued → processing → completed/failed)

## 📊 Database Schema

11 tables with full indexes, RLS, and triggers:

1. **agent_tasks** - Agent operation tracking
2. **leads** - Lead database with scoring
3. **email_events** - Email delivery tracking
4. **product_insights** - Product analysis results
5. **calendar_events** - Meeting scheduling
6. **alerts** - User notifications
7. **scrapes** - Scrape cache
8. **webhook_events** - Webhook audit log
9. **call_scripts** - Generated call prep materials
10. **campaigns** - Marketing campaigns
11. **domain_backoff** - Scraping politeness

## 🛠️ Development

### Run Tests
```bash
pytest
```

### Format Code
```bash
black app/
flake8 app/
```

### View Logs
```bash
# Docker
docker-compose logs -f orchestrator

# Local
tail -f logs/backend.log
```

## 🚢 Deployment

### Render (Recommended)
1. Connect GitHub repo
2. Select `apps/backend` as root directory
3. Use Docker deployment
4. Add environment variables from `.env.example`
5. Deploy!

### Railway
```bash
railway up
```

### Fly.io
```bash
fly launch
fly deploy
```

## 📝 Environment Variables Reference

See `.env.example` for complete list. Key variables:

- `SUPABASE_URL`, `SUPABASE_KEY` - Database
- `REDIS_URL` - Task queue
- `OPENROUTER_API_KEY` - LLM API
- `GMAIL_CREDENTIALS_JSON` - Email sending
- `INTERNAL_SIGNING_KEY` - JWT signing
- `WEBHOOK_SECRET` - HMAC verification

## 📚 Documentation

- [Backend Implementation Guide](./BACKEND_IMPLEMENTATION_GUIDE.md)
- [Database Schema](./supabase_schema.sql)
- API Documentation: Start server and visit `/docs`

## 🤝 Contributing

This is a production-grade implementation following best practices:
- Type hints everywhere
- Comprehensive error handling
- Structured logging
- Security-first design
- Idempotent operations
- Retry logic with backoff

## 📄 License

MIT
