# 🚀 DEPLOYMENT GUIDE - AI Agent Team

## ✅ Code Pushed to GitHub!

**Repository**: https://github.com/preet1249/My-AI-Agent-team

---

## 📝 Pre-Deployment Checklist

### ✅ Completed:
- [x] All 8 agents built with magic prompts
- [x] Conversation memory system
- [x] Agent-to-agent communication
- [x] DuckDuckGo search integration
- [x] Think mode functionality
- [x] All credentials configured in `.env`
- [x] Code pushed to GitHub

### 🔲 To Complete:
- [ ] Run Supabase schema
- [ ] Deploy backend to Render
- [ ] Deploy frontend to Vercel
- [ ] Test all endpoints

---

## 🗄️ STEP 1: Set Up Supabase Database (2 minutes)

1. **Go to your Supabase project**:
   https://whdtxycynbxwyaqpxajg.supabase.co

2. **Open SQL Editor**:
   - Click **SQL Editor** in left sidebar
   - Click **New Query**

3. **Run the Schema**:
   - Open `apps/backend/supabase_schema_FIXED.sql` from your project
   - Copy **ALL** content (210 lines)
   - Paste into SQL Editor
   - Click **Run** ▶️

4. **Verify Tables Created**:
   - Go to **Table Editor** (left sidebar)
   - Should see **12 tables**:
     * agent_tasks
     * leads
     * email_events
     * product_insights
     * calendar_events
     * alerts
     * scrapes
     * webhook_events
     * call_scripts
     * campaigns
     * domain_backoff
     * conversation_messages ⭐ (NEW - for memory!)

✅ **Database Ready!**

---

## 🖥️ STEP 2: Deploy Backend to Render (5 minutes)

### A. Create Web Service

1. **Go to Render**: https://render.com
2. **Click "New"** → **"Web Service"**
3. **Connect GitHub**:
   - Select repository: `preet1249/My-AI-Agent-team`
   - Click **Connect**

### B. Configure Service

**Basic Settings**:
- **Name**: `ai-agent-team-backend`
- **Region**: Choose closest to you
- **Branch**: `main`
- **Root Directory**: `apps/backend`
- **Runtime**: `Python 3`
- **Build Command**:
  ```bash
  pip install -r requirements.txt
  ```
- **Start Command**:
  ```bash
  uvicorn app.main:app --host 0.0.0.0 --port $PORT
  ```

### C. Add Environment Variables

Click **Advanced** → **Add Environment Variable**

Copy these (from your `.env` file):

```env
SUPABASE_URL=https://whdtxycynbxwyaqpxajg.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndoZHR4eWN5bmJ4d3lhcXB4YWpnIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MzQ2Mjc1MywiZXhwIjoyMDc5MDM4NzUzfQ.RI3MKmTApcmvOr2a5E0ZBY1ea5rPeBAPE__xDrLtOwo

REDIS_URL=redis://default:AWc1AAIncDJhOWJiMjZhOTAwYWU0MzBhODI5MDY4OWIzODUyNWYwZXAyMjY0MjE@wealthy-bear-26421.upstash.io:6379

OPENROUTER_API_KEY=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
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1

PRODUCT_MANAGER_MODEL=nvidia/nemotron-nano-12b-v2-vl:free
FINANCE_MANAGER_MODEL=nvidia/nemotron-nano-12b-v2-vl:free
MARKETING_STRATEGIST_MODEL=nvidia/nemotron-nano-12b-v2-vl:free
LEADGEN_MODEL=nvidia/nemotron-nano-12b-v2-vl:free
EMAILER_MODEL=nvidia/nemotron-nano-12b-v2-vl:free
CALLPREP_MODEL=nvidia/nemotron-nano-12b-v2-vl:free
ENGINEER_MODEL=anthropic/claude-3-haiku

INTERNAL_SIGNING_KEY=c90fa68ed1f554502fe1315f867852ecc3a29924f95dbd3a5590de75b5be5286
WEBHOOK_SECRET=0f1fb42d9197800426c8a8e26a6bc43e0891500562d0cd6b7f8eec9dde2c9a0b

GMAIL_CREDENTIALS_JSON={"type":"placeholder"}

PORT=8000
ENVIRONMENT=production
MODEL_CALL_TIMEOUT=30
SCRAPE_TIMEOUT=15
```

### D. Deploy!

1. Click **Create Web Service**
2. Wait 5-10 minutes for build
3. Copy your live URL (e.g., `https://ai-agent-team-backend.onrender.com`)

### E. Test Backend

Visit: `https://your-backend-url.onrender.com`

Should see:
```json
{
  "message": "AI Agent Team Backend",
  "version": "2.0.0",
  "agents": [
    "product_manager (Alex)",
    "finance_manager (Marcus)",
    ...
  ]
}
```

Visit: `https://your-backend-url.onrender.com/docs`
- Interactive API documentation ✨

✅ **Backend Deployed!**

---

## 🌐 STEP 3: Deploy Frontend to Vercel (3 minutes)

### A. Update Frontend Environment Variable

1. **Go to**: `apps/web/.env.local`
2. **Update**:
   ```env
   NEXT_PUBLIC_API_URL=https://your-backend-url.onrender.com
   ```

3. **Commit**:
   ```bash
   git add apps/web/.env.local
   git commit -m "Update backend URL"
   git push
   ```

### B. Deploy to Vercel

**Option 1: Automatic (if already connected)**
- Vercel will auto-deploy on push

**Option 2: Manual Deploy**
```bash
cd apps/web
vercel --prod
```

### C. Test Frontend

Visit: https://my-ai-agent-team-seven.vercel.app

Should see:
- Updated UI with 8 agents
- Alex, Marcus, Ryan, Jake, Chris, Daniel, Kevin, Sophia
- White icons
- Everything working!

✅ **Frontend Deployed!**

---

## 🧪 STEP 4: Test Complete System

### Test 1: Agent Conversation with Memory

```bash
# First message
curl -X POST https://your-backend.onrender.com/api/agents/product-manager \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-123",
    "prompt": "What should our product roadmap focus on?",
    "context": {"conversation_id": "test-conv-1"}
  }'

# Second message (should remember first)
curl -X POST https://your-backend.onrender.com/api/agents/product-manager \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-123",
    "prompt": "Can you elaborate on the first point?",
    "context": {"conversation_id": "test-conv-1"}
  }'
```

Alex should remember the previous conversation! 🎉

### Test 2: Think Mode

```bash
curl -X POST https://your-backend.onrender.com/api/think \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-123",
    "query": "What are the latest trends in B2B SaaS?",
    "max_results": 3
  }'
```

Should:
1. Search DuckDuckGo
2. Scrape 3 websites
3. Return answer with sources

### Test 3: Sophia (Personal Assistant)

```bash
curl -X POST https://your-backend.onrender.com/api/agents/personal-assistant \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-123",
    "prompt": "What tasks should I focus on today?"
  }'
```

Sophia should analyze ALL your data and provide intelligent suggestions!

### Test 4: Agent Communication

```bash
curl -X POST https://your-backend.onrender.com/api/agents/product-manager \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-123",
    "prompt": "Can we build a mobile app? How much will it cost?"
  }'
```

Alex should:
1. Detect technical + budget question
2. Consult Kevin (Engineer) and Marcus (Finance)
3. Return combined answer

---

## 📊 MONITORING & LOGS

### Render Dashboard:
- Go to https://dashboard.render.com
- Click your service → **Logs**
- Monitor requests in real-time

### Check Health:
```bash
curl https://your-backend.onrender.com/health
```

### View Conversations:
Check Supabase → `conversation_messages` table

---

## 🎯 FEATURES NOW LIVE:

✅ **8 AI Agents** with human names
✅ **Magic System Prompts** for perfect answers
✅ **Conversation Memory** - remembers chat history
✅ **Agent Communication** - agents collaborate
✅ **Think Mode** - FREE web search + analysis
✅ **@Mentions** - `@alex`, `@sophia`, etc.
✅ **TOON Format** - 30-50% token savings
✅ **NVIDIA NeMo** reasoning for 6 agents
✅ **Claude Haiku** for Engineer
✅ **Personal Assistant** (Sophia) with full context

---

## 🎉 YOU'RE LIVE!

Your AI Agent Team is now fully deployed and operational!

**Frontend**: https://my-ai-agent-team-seven.vercel.app
**Backend**: https://your-backend.onrender.com
**Docs**: https://your-backend.onrender.com/docs

All agents are ready to work with:
- Conversation memory
- Web search capabilities
- Agent-to-agent collaboration
- Business context awareness

---

## 💡 NEXT STEPS:

1. **Test each agent** on frontend
2. **Try Think mode** for research questions
3. **Talk to Sophia** for task management
4. **Add business context** to customize agents
5. **Monitor usage** on Render + Supabase dashboards

Questions? Check `/docs` endpoint or `README.md`!
