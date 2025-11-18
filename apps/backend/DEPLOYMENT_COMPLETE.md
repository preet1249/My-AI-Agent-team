# ✅ DEPLOYMENT READY - AI Agent Team Backend

## 🎉 Everything Configured!

### **Credentials Set Up:**
- ✅ Supabase Database (PostgreSQL)
- ✅ Upstash Redis (Task Queue)
- ✅ OpenRouter API (NVIDIA NeMo + Claude)
- ✅ Security Keys Generated

### **Models Configured:**
| Agent | Name | Model | Reasoning |
|-------|------|-------|-----------|
| Product Manager | Alex | NVIDIA NeMo 12B | ✅ Enabled |
| Finance Manager | Marcus | NVIDIA NeMo 12B | ✅ Enabled |
| Marketing Strategist | Ryan | NVIDIA NeMo 12B | ✅ Enabled |
| Lead Generator | Jake | NVIDIA NeMo 12B | ✅ Enabled |
| Outbound Emailer | Chris | NVIDIA NeMo 12B | ✅ Enabled |
| Call Prep | Daniel | NVIDIA NeMo 12B | ✅ Enabled |
| **Engineer** | **Kevin** | **Claude 3 Haiku** | - |
| Personal Assistant | Sophia | NVIDIA NeMo 12B | ✅ Enabled |

---

## 📝 NEXT STEPS:

### **Step 1: Set Up Supabase Database**

1. Go to your Supabase project: https://whdtxycynbxwyaqpxajg.supabase.co
2. Click **SQL Editor** on the left sidebar
3. Copy the entire content from `apps/backend/supabase_schema.sql`
4. Paste into SQL Editor
5. Click **Run** to create all 11 tables

This creates:
- agent_tasks
- leads
- email_events
- product_insights
- calendar_events
- alerts
- scrapes
- webhook_events
- call_scripts
- campaigns
- domain_backoff

---

### **Step 2: Test Backend Locally**

```bash
cd apps/backend

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn app.main:app --reload --port 8000
```

Visit: http://localhost:8000
- Should see: "AI Agent Team Backend" with 8 agents listed

Visit: http://localhost:8000/docs
- Interactive API documentation

---

### **Step 3: Test Individual Endpoints**

#### Test Think Feature:
```bash
curl -X POST http://localhost:8000/api/think \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user-123",
    "query": "What are the latest AI trends?",
    "max_results": 3
  }'
```

Should:
1. Search DuckDuckGo
2. Scrape 3 websites
3. Analyze with NVIDIA NeMo
4. Return structured answer with sources

#### Test Sophia (Personal Assistant):
```bash
curl -X POST http://localhost:8000/api/agents/personal-assistant \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user-123",
    "prompt": "Help me organize my tasks"
  }'
```

#### Test Agent Communication:
```bash
curl -X POST http://localhost:8000/api/agents/product-manager \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user-123",
    "prompt": "Can we build a mobile app? How much will it cost?"
  }'
```

Alex (Product Manager) should:
1. Detect "cost" keyword
2. Automatically ask Marcus (Finance Manager)
3. Combine both perspectives
4. Return comprehensive answer

---

### **Step 4: Deploy to Render**

1. Go to https://render.com
2. Click **New** → **Web Service**
3. Connect your GitHub repo
4. Configure:
   - **Root Directory**: `apps/backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Environment**: Python 3.11

5. Add Environment Variables:
   - Copy all from `.env` file
   - Paste in Render's Environment Variables section

6. Click **Create Web Service**

7. Wait 5-10 minutes for deployment

8. Get your live URL (e.g., `https://my-backend.onrender.com`)

---

### **Step 5: Update Frontend**

1. Update `apps/web/.env.local`:
```env
NEXT_PUBLIC_API_URL=https://your-backend.onrender.com
```

2. Deploy to Vercel:
```bash
cd apps/web
vercel --prod
```

---

## 🧪 TESTING CHECKLIST

After deployment, test these scenarios:

### ✅ Basic Agent Calls
- [ ] Talk to Alex (Product Manager)
- [ ] Talk to Marcus (Finance Manager)
- [ ] Talk to Ryan (Marketing Strategist)
- [ ] Talk to Jake (Lead Generator)
- [ ] Talk to Chris (Outbound Emailer)
- [ ] Talk to Daniel (Call Prep)
- [ ] Talk to Kevin (Engineer)
- [ ] Talk to Sophia (Personal Assistant)

### ✅ Agent Communication
- [ ] Ask Alex a technical question → should consult Kevin
- [ ] Ask Alex a budget question → should consult Marcus
- [ ] Ask Ryan about email campaigns → should consult Chris

### ✅ Think Mode
- [ ] Click "Think" and ask about industry trends
- [ ] Verify sources are returned
- [ ] Check DuckDuckGo searches work

### ✅ @Mentions
- [ ] "@alex what's the product roadmap?"
- [ ] "@sophia organize my week"
- [ ] "@kevin can you fix this bug?"

### ✅ Sophia's Intelligence
- [ ] Ask Sophia to check calendar
- [ ] Ask Sophia to summarize recent activity
- [ ] Ask Sophia to assign tasks

---

## 📊 MONITORING

Once deployed, monitor:

### Health Check:
```
GET https://your-backend.onrender.com/health
```

Should return:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-18T...",
  "version": "2.0.0"
}
```

### API Docs:
```
https://your-backend.onrender.com/docs
```

Interactive Swagger UI with all endpoints

---

## 🔧 TROUBLESHOOTING

### If agents don't respond:
1. Check OpenRouter API key has credits
2. Check logs: Render Dashboard → Logs
3. Verify Supabase connection

### If Think mode doesn't work:
1. Install `duckduckgo-search`: `pip install duckduckgo-search==4.1.1`
2. Check `beautifulsoup4` and `lxml` are installed
3. Test DuckDuckGo search manually

### If database errors:
1. Verify Supabase schema was run
2. Check service_role key (not anon key!)
3. Test connection from Supabase dashboard

---

## 💰 COST ESTIMATE

### Monthly Costs:
- **Supabase**: FREE (up to 500MB)
- **Upstash Redis**: FREE (10K commands/day)
- **Render**: FREE tier available
- **OpenRouter**: ~$5-20/month (pay per use)
  - NVIDIA NeMo: ~$0.0002 per 1K tokens (FREE tier available!)
  - Claude Haiku: ~$0.00025 per 1K tokens

**Estimated Total**: $5-20/month (mostly OpenRouter usage)

---

## 🎯 READY TO USE!

Your AI Agent Team is fully configured and ready to deploy!

All 8 agents with:
- ✅ FREE web scraping (DuckDuckGo)
- ✅ Agent-to-agent communication
- ✅ NVIDIA NeMo reasoning (6 agents)
- ✅ Claude Haiku (Engineer)
- ✅ Personal Assistant with full context
- ✅ @mention routing
- ✅ Think mode for web research

**Questions? Issues?**
Check the logs and API docs at `/docs` endpoint!
