AI Agent Team

Tech Stack

Frontend (Web)
Next.js
React
TailwindCSS
Next-PWA (for installable PWA)

Frontend (Mobile App)
Expo (React Native)
React Native Web (shared UI components)
AsyncStorage / SecureStore
React Navigation

Shared Code (Monorepo)
Turborepo / PNPM workspace
Shared UI package (React Native Web compatible)
Shared Lib package (API client, TOON converters)

Backend
FastAPI (Orchestrator API)
Python Worker Pool
Redis / Upstash (Task queue)
Docker 
Puppeteer (Scraping)
LangChain
LangGraph

Database & Storage
Supabase Postgres
Supabase Storage
Supabase Realtime
Authentication
Supabase Auth
OAuth Redirect (Google)
LLM Providers

OpenRouter
NVIDIA NeMo 12B 2-VL (All agents)
Claude 3 Haiku (Engineer agent)

Email
Gmail API (Google Cloud)
Google Pub/Sub (Gmail push notifications)
Monitoring (currently not available but only custom python script just structure for ready to use in future)

Prometheus
Alertmanager
Notifications

Expo Notifications (Mobile)
Web Push (PWA)

Hosting
Render (Backend + workers)
Vercel (Next.js web)

Data Serialization
TOON Format (for agent → worker → model messages)


1 — User workflow (what you do in the app)

Chat box (or quick command) — “Give me a new product design as per trend.”

UI: you pick agent = ProductManager (dropdown) or leave default “smart route”.

Result: ProductManager scrapes trends, asks Engineer agent feasibility, returns final design and saves it to Product Insights and History sheet (lead-like table, versioned).

Lead scraping: you command LeadGen: “Scrape leads for niche=X, location=Y.”

System runs scrapers, dedupes leads, populates the Leads Sheet (table UI you requested), each row linked to a lead history and outbound email log.

Email campaign: you click “Send campaign” on selected leads → Outbound agent personalizes (uses PM insights) and sends via Gmail API. Replies are processed automatically and trigger auto-reply rules.

Booking a call: client fills website booking form → saved to in-app Calendar (not Google Calendar). System generates a call script tailored to lead + booking answers, saved to call history and calendar event.

Monitoring: custom Python cron + Prometheus scrape runs independently; alerts create incidents in the Alerts table; Engineer (Claude) triages and writes a playbook into the incident row.

All outputs are saved as records you can filter, export CSV, or view per-agent history in the sheet UI.

2 — High-level backend orchestration (short)

Front-end (Next.js) ⇄ Orchestrator API (FastAPI / Python)

Orchestrator writes agent_tasks in Supabase and enqueues jobs in Redis (Upstash)

Worker pool picks jobs → runs scraper (Playwright) / model calls (OpenRouter) / sends emails (Gmail API) → stores outputs in Supabase.

For agent-to-agent checks, orchestrator makes an internal agent call (internal authenticated API) — e.g., ProductManager → Engineer (Claude) for feasibility.

All LLM inputs/outputs to models are serialized using TOON (token-efficient) before calling OpenRouter. Store canonical JSON in DB; convert JSON ↔ TOON in middleware. 
GitHub
+1

3 — System architecture (Mermaid diagram)

Paste this Mermaid into your Markdown / docs to visualize:

flowchart LR
  subgraph UI
    U[Next.js App (Web + Android PWA)]
  end

  subgraph Backend
    API[Next.js API Routes]
    Orch[Orchestrator (FastAPI)]
    Queue[Redis / Upstash]
    Worker[Worker Pool (Python)]
    Scraper[Playwright Scrapers]
    OpenRouter[OpenRouter (NeMo 12B-2VL & Claude 3 Haiku)]
    LangChain[LangChain / LangGraph Middleware]
  end

  subgraph Data
    DB[Supabase Postgres + Storage]
  end

  subgraph Integrations
    Gmail[Gmail API (Google Cloud)]
    Push[Push Notifications / In-App]
    Prom[Prometheus + Alertmanager]
  end

  U --> API
  API --> Orch
  Orch --> Queue
  Queue --> Worker
  Worker --> Scraper
  Worker --> OpenRouter
  Worker --> DB
  Worker --> Gmail
  Worker --> Prom
  LangChain -.-> Worker
  OpenRouter -->|Claude| Worker
  DB --> U
  Prom --> Worker
  Worker --> Push

4 — Sequence flows (two key ones)
A) “Product design” (user → PM → Engineer → saved)
sequenceDiagram
  participant U as User (Next.js)
  participant API as Next.js API
  participant Q as Redis Queue
  participant W as Worker
  participant S as Scraper (Playwright)
  participant LC as LangChain/LangGraph
  participant OR as OpenRouter (NeMo)
  participant ENG as Engineer (Claude via OpenRouter)
  participant DB as Supabase

  U->>API: POST /api/orchestrator/ask {agent:product_manager, prompt}
  API->>DB: insert agent_task (queued)
  API->>Q: push task
  Q->>W: worker pops task
  W->>S: run scraping job (cache)
  S-->>W: returns summaries
  W->>LC: pre-process (summarize, format -> TOON)
  W->>OR: call ProductManager model (TOON payload)
  OR-->>W: draft design
  W->>API: internal call -> call Engineer agent (Claude) with condensed TOON
  OR-->>W: engineer result (feasible/constraints)
  W->>DB: save product_insight + create calendar tasks
  W->>API: mark task done & emit realtime update
  API->>U: push result (realtime)

B) Lead scraping → send campaign → inbound reply handling
sequenceDiagram
  participant U
  participant API
  participant Q
  participant W
  participant Scraper
  participant DB
  participant Gmail
  participant OR

  U->>API: "Scrape leads niche=A location=B"
  API->>Q: enqueue scrape
  Q->>W: pop
  W->>Scraper: run playwrigh/pupeteer
  Scraper-->>W: leads list
  W->>DB: insert leads (dedupe)
  U->>API: "Send campaign to selected leads"
  API->>Q: enqueue send job
  W->>DB: fetch leads & PM insights
  W->>OR: LLM (Marketing) personalize (TOON)
  W->>Gmail: send via Gmail API
  Gmail-->>API: webhook (push via Pub/Sub or forwarding)
  API->>DB: inbound email -> email_events
  API->>Q: enqueue auto-reply job
  W->>OR: LLM (AutoReply) -> reply text
  W->>Gmail: send reply
  W->>DB: update lead status

5 — Webhook endpoints & Toon payload examples

Security: All webhooks validate an HMAC x-signature header; internal calls use a JWT signed with an internal key. Use TLS.

1) POST /api/webhook/gmail/push

(Gmail push via Google Pub/Sub subscriber or via SMTP-forwarding) — example TOON payload (inbound email) the webhook handler receives after conversion to TOON:

email:
  id: msg-abc123
  from: "raj@acme.com"
  to: "you@yourdomain.com"
  subject: "Re: Quick idea"
  body_text: "Yes I'm interested. Tue 10AM works"
  timestamp: 2025-11-21T09:00:00+05:30


Server action:

find lead by from or create lead row → insert email_event → enqueue reply logic.

2) POST /api/webhook/scrape/done

TOON:

scrape_result:
  task_id: task-777
  status: done
  source: "https://example.com/article"
  summary: "Key UX trend: micro-tutorials"
  extracted:
    - title: "..."
    - links: [...]


Server: store scrape, dedupe, notify orchestrator.

3) POST /api/webhook/calendar/booking

TOON:

booking:
  id: book-942
  name: "Maya Singh"
  email: "maya@company.com"
  start: 2025-11-27T16:00:00+05:30
  end: 2025-11-27T16:30:00+05:30
  answers:
    team_size: 8
    use_case: "onboarding"


Server: create calendar_events row in Supabase, generate call script via Model.

4) POST /api/webhook/monitor/alert

TOON:

alert:
  id: alert-1001
  service: "api-gateway"
  severity: P1
  message: "503 spike > 30s"
  logs: |
    [last 50 lines...]
  metrics:
    5m_rate: 12.3


Server: create alert row, spawn Claude triage job, notify.

6 — DB Schema (Supabase SQL) — includes sheet-style leads + custom calendar

Key tables (paste into Supabase SQL editor):

-- agent tasks
CREATE TABLE agent_tasks (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid REFERENCES auth.users(id),
  agent_name text NOT NULL,
  input jsonb,
  output jsonb,
  status text NOT NULL DEFAULT 'queued',
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- sheet-style leads
CREATE TABLE leads (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  created_by uuid REFERENCES auth.users(id),
  name text,
  email text,
  company text,
  role text,
  score integer DEFAULT 0,
  metadata jsonb,
  history jsonb DEFAULT '[]'::jsonb, -- array of events / email logs
  status text DEFAULT 'new',
  created_at timestamptz DEFAULT now()
);

-- email events
CREATE TABLE email_events (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  lead_id uuid REFERENCES leads(id),
  direction text, -- inbound/outbound
  subject text,
  body text,
  raw jsonb,
  sent_at timestamptz DEFAULT now()
);

-- product insights
CREATE TABLE product_insights (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  title text,
  user_id uuid REFERENCES auth.users(id),
  task_id uuid REFERENCES agent_tasks(id),
  summary text,
  sources jsonb,
  output jsonb,
  created_at timestamptz DEFAULT now()
);

-- custom calendar (in-app)
CREATE TABLE calendar_events (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid REFERENCES auth.users(id),
  title text,
  description text,
  start_at timestamptz,
  end_at timestamptz,
  metadata jsonb,   -- e.g., call script id, booking_id, external link
  created_at timestamptz DEFAULT now()
);

-- monitoring alerts
CREATE TABLE alerts (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  alert_id text,
  service text,
  severity text,
  payload jsonb,
  acknowledged boolean DEFAULT false,
  created_at timestamptz DEFAULT now()
);


Notes:

Keep canonical data in JSON (DB), but convert to TOON only for model calls to save tokens; store the canonical JSON so your app and Android UI remain interoperable.

7 — Gmail integration (send & receive) — how to wire (free)

Enable Gmail API in Google Cloud project (OAuth client).

Send email: use Gmail API users.messages.send (requires OAuth). For server-side sending from a single account, create a service account + domain delegation or use OAuth client + refresh token stored securely.

Receive / reply automation: Gmail push notifications → Google Pub/Sub (Gmail watch/watch requests sends notifications to Pub/Sub) → your Pub/Sub subscription push endpoint /api/webhook/gmail/push receives a small notification with message id → call Gmail API users.messages.get to fetch full message → process. This is a recommended approach for real-time inbound mail without polling. (Docs: Gmail push with Pub/Sub).

Auto-reply flow: webhook -> lookup lead -> run AutoReply agent (TOON request) -> Gmail API send reply.
Security: store OAuth refresh token in Supabase Secrets or server env. Rotate periodically.

(If you cannot use Pub/Sub, smaller approach: forward inbound email to your own SMTP endpoint, but Pub/Sub is free on GCP in many quotas and is reliable.)

8 — LangChain + LangGraph usage (free + where to use)

LangChain: In Python worker you can use LangChain for prompt templates, LLM wrappers, caching, and chains (esp. for Marketing agent multi-step tasks). Use local memory and a small LRU cache to avoid repeated calls. LangChain open-source is free.

LangGraph: Use for building visual flows / agent orchestration; convert complex orchestrations into graph definitions. Useful for mapping agent-to-agent flows visually and editing agent pipelines in dev. Prefer this for building marketing → PM → engineer flows.

Avoid LangSmith: you said no — that's fine. LangChain + self-hosted Redis + Supabase for state will be sufficient. (LangChain has local disk/db storage libs.)

9 — JSON ↔ TOON conversion (where & how)

Keep JSON as canonical storage format in DB (Supabase).

Before sending to the model, run a conversion json_to_toon() in your worker (small library; there are implementations on Github / npm / Elixir libs). Use TOON when the payload is large (lists, arrays of leads, long tables). Convert model outputs back to JSON with toon_to_json() and persist. This gives the best of both worlds: DB interoperability + token savings. 
GitHub
+1

Example: JSON → TOON

JSON:

{
  "lead": {
    "name": "Maya Singh",
    "email": "maya@company.com",
    "company": "AcmeApps"
  }
}


TOON (simple style):

lead:
  name: Maya Singh
  email: maya@company.com
  company: AcmeApps


For arrays / tables, TOON uses compact tabular patterns to reduce repeated keys (see TOON spec). Use the conversion library to be safe. 
GitHub

10 — Model selection & prompt rules

ProductManager / Marketing / LeadGen: NVIDIA NeMo 12B-2VL via OpenRouter (your paid usage). Use temperature=0.0 for factual outputs or 0.3-0.7 for creative marketing.

Engineer: Claude 3 Haiku via OpenRouter for triage and code/log reasoning (you said Claude for engineering).

Prompting pattern: always include:

system (role + strict reply schema)

context_summary (4–6 lines per source) — pre-summarize scraped pages to save tokens

data_table (if large, pass in TOON)

instruction (expected output shape — prefer TOON schema output)

Caching: if identical prompt and sources, return cached output for 24h.

11 — Monitoring, reliability & operational rules (zero-budget friendly)

Queue everything (Redis). No blocking HTTP.

Backoff & retries for network/model failures (exponential backoff, 3 attempts). Persist status to agent_tasks.

Rate limit OpenRouter calls per minute (token bucket) and use a small in-memory counter + Redis for distributed.

Cache scraped pages 24–72h to reduce scrape calls (Playwright).

Prometheus metrics: expose agent_task_duration, model_calls_total, email_sent_total, scrape_jobs_total. Configure Alertmanager for thresholds.

Sentry for exceptions. Use free tier.

Secrets: Supabase secrets or env; rotate.

12 — Minimal Docker Compose layout (starter)

Use small services on one VPS or local dev; deploy to Render (workers) and Vercel (Next.js). Example services:

nextjs (Vercel or container)

orchestrator (FastAPI)

worker (Python)

redis (Upstash or container)

playwright (headless)

prometheus + grafana (optional)

(You already have a working stack from previous message — keep that compose and add Gmail worker + Pub/Sub endpoints.)

13 — Small code / prompt snippets (ready-to-paste)
Internal agent-to-agent call (TOON)

Payload (TOON):

agent_call:
  from: product_manager
  to: engineer
  question: |
    feasibility_check: "Can we build an in-app 30s interactive tutorial overlay for Android PWA?
    constraints: memory <= 150MB, render_cpu not exceed 20ms/frame"
  context:
    infra:
      android_pwa_memory_limit: 150MB
      backend_runtime: python-3.11

ProductManager system prompt (TOON expected output)
system: |
  You are ProductManagerAgent. Output should be TOON with fields:
  title, insights[], roadmap[], tasks[], calendar_events[]

14 — Implementation checklist (prioritized)

Create Supabase project (DB, Auth, Storage).

Create Google Cloud project + Gmail API credentials (OAuth) and Pub/Sub subscription for push notifications.

Build Next.js UI + Auth (Supabase). Implement sheet-like Leads page and Calendar UI (local DB events).

Implement FastAPI Orchestrator + Redis queue (Upstash).

Implement Worker basics: OpenRouter test call, json↔toon conversion library, simple ProductManager chain (scrape → summarize → model).

Add Playwright scraper container with polite crawling + caching.

Add Gmail inbound webhook (Pub/Sub subscriber) + outbound send using Gmail API.

Add Prometheus + basic Grafana dashboards.

Hardening: HMAC webhooks, rate-limiting, retries, Sentry.

15 — Why this will work for your constraints

Zero budget / free-tier friendly: Supabase + Vercel free tier + Upstash free tier + Gmail API (Google Cloud) keeps cost very low. Only predictable expense: OpenRouter model calls.

Scale: design supports 10–15 users easily on small workers; everything is queued and cached.

Custom calendar: in-app DB driven calendar is simpler and avoids Google Calendar quotas; you still can sync to Google Calendar optionally.

TOON usage: minimizes your token spend when calling LLMs for large structured inputs (leads, tables, calendars).


WebHooks-----

Real-time webhooks — Full spec (endpoints, payload (TOON), security, timings, retries)

Below are the production-ready webhook endpoints with TOON examples, HMAC verification, JWT for internal calls, exact timing budgets, timeouts, retry/backoff rules, rate limits, and idempotency rules.

Common webhook rules (applies to all endpoints)

Transport: HTTPS only (TLS 1.2+).

Auth & security:

External integrations: HMAC SHA256 signature header x-webhook-signature: sha256=<hex> where signature = HMAC_SHA256(secret, raw_body). Secret stored in Supabase Secrets or env.

Internal agent calls: Use JWT signed by INTERNAL_SIGNING_KEY. Header Authorization: Bearer <internal-jwt>. JWT must have iss=orchestrator, aud=worker, exp within 60s for each call.

Idempotency: Every webhook payload must include an external_id (string). Server must store processed external_id and return 200 without reprocessing if seen before.

Response: Return 2xx on success. On temporary failure return 5xx (or 429 if rate limited). Include retry_after header in seconds when returning 429 or 503.

Max payload size: 2 MB. If larger, use presigned storage URL and send small webhook referencing it.

Time-to-ack: Process webhook quickly — acknowledge with 200 within 1 second. Heavy work must be enqueued; do not process heavy jobs synchronously.

Logging: Log webhook reception (status accepted/rejected) to an audit table webhook_events with timestamps and signature check result.

Endpoint A — POST /api/webhook/gmail/push

Purpose: Receive Gmail push notifications (Pub/Sub push → your endpoint), fetch message via Gmail API, process inbound email.
Expectations / timings:

Gmail Pub/Sub push contains only messageId and small metadata. Your endpoint must ack Pub/Sub within 10s (Pub/Sub requires fast ack).

On receive: immediately enqueue a background job to fetch the full message (Gmail API users.messages.get) — do not fetch synchronously in the webhook handler.

Background job fetch timeout: 10s for message fetch; retry once after 2s if network error.

Overall processing (incl. auto-reply) expected to complete within 30s typical; if longer, mark as “processing” and notify user when done.

TOON payload (after you fetch message):

email:
  external_id: msg-abc123
  from: "lead@company.com"
  to: "you@yourdomain.com"
  subject: "Re: Quick idea"
  body_text: "Yes I'm interested. Tue 10AM works"
  received_at: 2025-11-21T09:00:00+05:30
  thread_id: "thread-333"
  raw_headers: { "Message-Id":"...", "References":"..." }


Flow:

Pub/Sub -> POST to /api/webhook/gmail/push (ack within 10s).

Enqueue fetch job -> Worker fetches full message (use Gmail API messages.get).

Worker converts message to TOON and inserts email_events and attempts to match leads by from.

If matched and rules apply → enqueue auto-reply job.

Rate limits & quotas:

Gmail API: keep < 250 queries/minute per user to be safe (smaller quota if you're on free OAuth). Implement batching for messages.get if many events.

Pub/Sub push may batch; ensure your endpoint can handle bursts — use HTTP/2 or a small autoscaler.

Retries:

For Pub/Sub, Google will retry push; ensure idempotency by checking external_id.

For Gmail API failures: retry up to 2 times with exponential backoff (2s, then 6s). On repeated failure, persist a failure record and alert you.

Endpoint B — POST /api/webhook/scrape/done

Purpose: Scraper worker (possibly remote/clustered) notifies orchestrator that a scrape finished and provides a small summary / pointer to full result in storage.

TOON payload:

scrape_result:
  external_id: scrape-20251121-001
  task_id: task-abc123
  status: done
  source_url: "https://example.com/article"
  summary: "Key trend: micro tutorials and inline onboarding"
  storage_url: "supabase://bucket/path/page1.html"
  extracted:
    headlines: ["..."]
    links: ["..."]
  fetched_at: 2025-11-21T09:12:03Z


Timing & behavior:

Scraper should upload full raw HTML to Supabase Storage before sending webhook.

Webhook handler must ack within 1s and enqueue processing job to parse extracted and store in scrapes table.

If the scrape includes many items (e.g., 100 pages), send multiple scrape_result webhooks with external_id per batch (size <=100 items).

Cache TTL: default 24 hours for scraped pages; set longer (72h) for slow-changing sources (blogs/news). Save fetched_at.

Politeness & scraping rules (see detailed section below).

Endpoint C — POST /api/webhook/calendar/booking (your booking form)

Purpose: External booking form or internal booking action posts booking metadata to create a local calendar event & call script.

TOON payload:

booking:
  external_id: book-942
  name: "Maya Singh"
  email: "maya@company.com"
  start: 2025-11-27T16:00:00+05:30
  end: 2025-11-27T16:30:00+05:30
  timezone: "Asia/Kolkata"
  answers:
    team_size: 8
    use_case: "onboarding"


Timing:

Webhook ack within 1s.

Create calendar event in DB within 2s in background worker.

Call script generation (LLM) queued; expected completion within 12–25s depending on model queue and token volume. Update event record when call script ready.

Retries:

If calendar write fails, retry 2 times with backoff 3s → 9s. If still failing, set event status pending and notify user.

Endpoint D — POST /api/webhook/monitor/alert

Purpose: For Prometheus Alertmanager or custom monitor to push alerts to orchestrator.

TOON payload:

alert:
  external_id: alert-1001
  service: "api-gateway"
  severity: P1
  message: "503 spike > 30s"
  timestamp: 2025-11-21T02:12:03Z
  last_logs: |
    [last 50 lines...]
  metrics:
    cpu: 82
    error_rate_5m: 0.124


Timing & behavior:

Must ack within 500ms ideally (alerts are high-priority).

Orchestrator enqueues triage job and creates alerts row within 1s.

Triage (Claude) should be invoked asap; expected triage-to-result within 30–60s depending on model. If model is busy, fallback is to include checklist mitigation steps stored in DB for immediate actions.

Escalation:

P1: immediate Push + SMS + in-app notify + create incident.

P2: in-app notify + email.

P3: log & create ticket.

Scraping (Puppeteer) — politeness, caching, concurrency, timings

You said use Puppeteer in Docker — excellent. Below are precise operational rules to avoid blocks and to stay within free-tier constraints.

Puppeteer Docker config

Use headless Chrome image mcr.microsoft.com/playwright or browserless/chrome slim image. Run with --no-sandbox only if necessary and secure host.

Keep container memory limit configurable (start with 1.5GB). For multiple concurrent pages, increase memory.

Concurrency & pool size

Max concurrent browser instances: 2 on small VPS (or 4 if you have 4+GB RAM). Prefer 1 browser with multiple pages (tabs).

Max concurrent pages: 4 per browser instance. So if 2 browsers → up to 8 concurrent pages. Tune to memory.

Per-domain politeness (VERY IMPORTANT)

Delay between requests to same domain: 2–5 seconds (randomized jitter + exponential backoff on 429/403). Default: 3s ±1s jitter.

Max requests per domain per 24h: 200 (conservative). For news sites, reduce to 20–50 to be safe and avoid being blocked.

Robots.txt: Respect robots.txt by default (if robots.txt disallows scraping of path, skip). You can override for specific white-listed domains (make sure it's legal).

Scrape job timeouts

Page load timeout: 15s (if page heavy, increase but prefer to collect summaries).

Script runtime per page: 10s (DOM extraction JS).

Retry policy per page: 2 retries with incremental delays (2s, 6s). On 429 or 403 from server, backoff 60s, mark domain as temporarily blocked and reduce rate.

Caching

Cache raw HTML: store in Supabase Storage with a key sha256(url) and TTL metadata.

Cache TTL:

news/blogs: 24 hours

documentation/api pages: 72 hours

evergreen (static docs): 7 days

lead pages/contact pages: 7 days

Before scraping a URL, check cache: if cached and now - fetched_at < TTL, use cached summary instead of re-scraping.

Summarization pre-step

Always run a lightweight summarizer (local cheap method or short model call) to create 4–6 line summary and store summary to DB; use that summary in LLM prompts to reduce token usage.

Resource-saving tips

Render-only-essential: For many sites, use page.setRequestInterception(true) and block images/fonts/analytics scripts to reduce bandwidth and speed up loads.

Use mobile user-agent when scraping mobile-first pages to get lighter pages.

Rotate user-agents from a short list and randomize Accept-Language to match target region.

No JS if possible: For static sites, fetch raw HTML via requests first and only use Puppeteer for dynamic JS pages.

Model call timings & quotas (OpenRouter / NeMo / Claude)

Goal: keep model calls fast and cheap.

Per-call budgets

ProductManager (NeMo):

Timeout: 20s (for 12B model; may be slower under load).

Expected typical latency: 2–8s for short prompts; 8–20s for long contexts.

Max tokens per call: keep prompt+response < 8192 tokens (confirm OpenRouter limits). Use context summarization.

Engineer (Claude 3 Haiku):

Timeout: 30–60s (Claude triage can need more time for log reasoning).

Expected latency: 5–25s typical.

Rate-limiting & throttling

Global model call concurrency: max 3 concurrent calls on small setup. Use Redis token-bucket to limit concurrency across workers.

Per-user model calls: cap to 2 concurrent requests per user to avoid abuse.

If OpenRouter returns 429 or rate-limit, fallback:

Return cached answer if available.

If no cache, respond with short deterministic answer template and set task.status=delayed.

Prompt & token savings

Use TOON and pre-summarize sources. Keep temperature=0.0 for ProductManager outputs except Marketing where 0.5 is fine.

Use max_tokens strict cap in API call to limit cost.

Retry & backoff policies (concrete schedules)

General worker call retry (network / transient errors):

Attempt 1 (immediate)

Attempt 2 (after 2s)

Attempt 3 (after 8s)

If still failing: mark task.status = failed_retryable; create Sentry error and notify owner. For critical (email, alerts) escalate immediately.

Model call transient 429 / 503:

Retry 1: after 1s

Retry 2: after 4s

Retry 3: after 12s

If still limited: queue in deferred_model_calls with next run after 60s.

Scraper-specific:

On network error: retry 2 times with 2s and 6s delays.

On 429/403: pause domain scraping for 60 minutes by updating domain_backoff table with next_allowed = now() + 60m.

Payload examples (TOON) — quick paste-ready
1) Webhook: Gmail inbound (TOON)
email:
  external_id: msg-20251121-abc
  from: "raj@acme.com"
  to: "you@domain.com"
  subject: "Re: Quick idea"
  body_text: "Yes, let's take a 15-min call Tue 10AM IST"
  thread_id: "thr-987"
  received_at: 2025-11-21T09:00:00+05:30

2) Webhook: Scrape done (TOON)
scrape_result:
  external_id: scrape-20251121-001
  task_id: task-xyz
  status: done
  source_url: "https://example.com/article"
  summary: "Trend: in-app micro tutorials improve day-1 retention"
  storage_url: "supabase://bucket/page1.html"
  fetched_at: 2025-11-21T09:12:03Z

3) Webhook: Monitor alert (TOON)
alert:
  external_id: alert-1001
  service: api-gw
  severity: P1
  message: "503 spike >30s"
  timestamp: 2025-11-21T02:12:03Z
  last_logs: |
    [..last 50 lines of logs..]

Recommended defaults (copy-paste)

Webhook ack limit: 1 second.

Queue processing start: within 2 seconds of enqueue on average.

Scraper per-domain delay: 3s ±1s jitter.

Scraper concurrency: max 8 pages total (start small, tune).

Scrape page timeout: 15s.

Model call timeout: 20s (NeMo), 60s (Claude).

Retry schedule: [immediate, +2s, +8s]; for model 1s/4s/12s.

Cache TTL (scrapes): 24h default.

OpenRouter concurrency: global 3 calls; per-user 2 calls.

Gmail API safe rate: <250 req/min (throttle to 4 req/sec).

Quick checklist (apply these to your code)

Implement HMAC verify helper for webhooks. Reject if signature missing or invalid.

For every webhook handler: verify signature → store webhook_events row → enqueue a job → return 200 immediately.

Enforce idempotency using external_id.

Scraper: implement domain backoff table and check before scheduling a page.

Use TOON conversion library for large payloads before model calls; convert back after response.

Instrument Prometheus metrics for webhook latency, task queue depth, worker success/fail rate, model call latency.

Add Sentry alerts for repeated failures >3 retries.

Feel free to copy-paste each TOON block directly into your code or spec docs. I kept naming consistent with your Supabase tables (agent_tasks, leads, email_events, scrapes, calendar_events, alerts, product_insights).

Naming conventions & general rules (apply to all schemas)

external_id — string, globally unique id from the caller (used for idempotency). Required for webhooks.

ts — ISO 8601 timestamp. Use UTC if possible. Required.

All large text fields that will be shown to LLMs should include token_hint (approx characters / tokens) to help worker decide summarization.

Max payload size: 2 MB; if larger, include storage_url pointing to Supabase Storage.

Use TOON for model inputs/outputs; store canonical JSON in DB but use these TOON shapes for communication with workers & LLMs.

meta — optional object for routing/security: {source, signature, verification_status}

A — Webhook: Gmail Inbound (TOON) — webhook.gmail.inbound.toon
email:
  external_id: str            # REQUIRED: unique message id (eg. "msg-20251121-abc")
  ts: iso8601                # REQUIRED: received timestamp (UTC preferred)
  from: str                  # REQUIRED: sender email (single)
  to: list[str]              # REQUIRED: recipients (usually your address)
  cc: list[str]              # optional
  bcc: list[str]             # optional
  subject: str               # required (can be empty)
  body_text: str             # plain text body (trim to 100k chars or use storage_url)
  body_html: str?            # optional HTML (use storage_url if >200k chars)
  thread_id: str?            # optional (Gmail thread id)
  headers: map[str,str]?     # optional raw headers map
  attachments:              # optional list (use storage_url for large items)
    - {
        filename: str,
        mime: str,
        size_bytes: int,
        storage_url: str?    # put file in Supabase Storage and reference here
      }
  matched_lead_id: uuid?     # worker fills when lead is matched
  token_hint: int?           # approx tokens; optional helper for model
  meta?: {                  # optional routing/meta
    source: "gmail-pubsub" | "smtp-forward",
    pubsub_message_id: str?,
    signature: str?         # optional raw signature header for audit
  }


Validation & processing rules

Must include external_id and ts.

body_text should be provided when possible. If body_html or attachments exceed limits, uploader must set storage_url and not embed raw content.

Worker: On receive, create email_events row and try to matched_lead_id by matching from. Enqueue auto-reply if match + rule.

Idempotency: If external_id already processed, respond 200 and do nothing.

DB mapping hint: email_events → fields mapping; leads.history add event.

B — Webhook: Scrape Done (TOON) — webhook.scrape.done.toon
scrape_result:
  external_id: str            # REQUIRED: unique per-batch (eg. "scrape-20251121-001")
  ts: iso8601                 # REQUIRED
  task_id: uuid?              # optional: orchestrator task id
  status: enum(done | partial | failed)
  source_url: str             # REQUIRED: canonical URL scraped
  storage_url: str?           # optional: Supabase storage link to full HTML/asset bundle
  extracted:
    summary: str              # 1-6 sentence summary (short)
    title: str?
    headings: list[str]?
    links: list[str]?
    contact_info: list[{type: str, value: str}]? # e.g., email, phone
    structured: map?         # optional structured data (JSON-serializable)
  http_status: int?           # optional response code from fetch
  crawl_metadata:
    fetch_duration_ms: int?
    attempts: int?            # how many tries
    user_agent: str?
  token_hint: int?            # approx tokens for model use
  meta?: {
    domain: str,
    robots_allowed: bool,
    cache_ttl_seconds: int?
  }


Validation & processing rules

storage_url recommended for full HTML. summary required for quick model usage.

If status=failed, include http_status and extracted.summary should explain reason.

Idempotency: skip if external_id exists; if same source_url but newer ts, worker may refresh cache based on cache_ttl_seconds.

Caching: Worker must consult cache TTL (from meta.cache_ttl_seconds) before deciding to re-scrape.

DB mapping hint: scrapes table; store storage_url and extracted in extracted JSONB.

C — Webhook: Calendar Booking (TOON) — webhook.booking.create.toon
booking:
  external_id: str            # REQUIRED: unique booking id (eg. "book-942")
  ts: iso8601                 # REQUIRED: booking creation time
  name: str                   # REQUIRED
  email: str                  # REQUIRED
  phone: str?                 # optional
  company: str?               # optional
  timezone: str               # REQUIRED: tz name (eg. "Asia/Kolkata")
  start: iso8601              # REQUIRED: event start
  end: iso8601                # REQUIRED: event end
  title: str?                 # optional event title
  answers: map?               # optional booking form Q&A {key: value}
  source: str?                # where booking came from (site, calendly mirror, etc)
  token_hint: int?            # approx tokens for script generation
  meta?: {
    allow_google_sync: bool = false, # default false; if true worker syncs to Google Calendar
    calendar_visibility: "private" | "public" | "team"
  }


Validation & processing rules

start < end and timezone present.

Worker: create calendar_events row; enqueue call_script_generation task that passes booking → Booking & Call Prep agent.

Idempotency: if external_id exists, update existing event if ts newer, else ignore.

DB mapping hint: calendar_events table; metadata should include booking.external_id.

D — Webhook: Monitor Alert (TOON) — webhook.monitor.alert.toon
alert:
  external_id: str            # REQUIRED: id from monitoring system (eg. "alert-1001")
  ts: iso8601                 # REQUIRED: alert timestamp
  service: str                # REQUIRED: service name (eg. "api-gateway")
  severity: enum(P1 | P2 | P3 | info)
  message: str                # REQUIRED: short description
  metrics: map?               # optional metric key-values (eg. {"error_rate_5m": 0.12})
  last_logs: str?             # optional text blob (limit 200k chars)
  trace_links: list[str]?     # links to logs/dashboards
  meta?: {                    # optional tooling info
    source: "prometheus" | "custom-monitor",
    prometheus_alertname: str?
  }


Validation & processing rules

severity determines immediate actions:

P1 → create incident, escalate SMS/push, enqueue engineer triage.

P2 → create ticket + in-app notification.

P3/info → log only or send digest.

Idempotency: dedupe by external_id. If same id but higher severity later, update and escalate.

Worker: persist to alerts and call Engineer agent for triage (Claude).

DB mapping hint: alerts table; create incident workflow entries when severity high.

Agent schemas — inputs & outputs (TOON)

Below are the 7 agents with their strict TOON input and output contracts. These are what orchestrator/worker and frontend use to call agents and accept responses.

Common agent call envelope:

agent_call:
  external_id: str         # REQUIRED: unique call id (task id)
  ts: iso8601              # REQUIRED: call time
  agent: str               # REQUIRED: agent name (e.g., "product_manager")
  user_id: uuid?           # optional: who requested
  payload: <agent-specific TOON>
  meta?: {                 # optional routing & security
    priority: int = 5,
    cache_allowed: bool = true,
    expected_ttl_seconds: int?
  }

1) Product Manager Agent — agent.product_manager.toon
Input payload
product_request:
  prompt: str                   # user instruction (eg "Give me a new product design as per trend")
  context_summaries: list[{     # scraped summaries (short) - prefer TOON summaries
    url: str,
    title: str,
    summary: str,
    ts: iso8601
  }]
  internal_metrics: {           # optional product metrics (small)
    active_users_7d: int?,
    retention_d1_pct: float?,
    top_features: list[str]?
  }
  require_feasibility_check: bool = true
  calendar_slot_pref: {         # optional: for scheduling weekly tasks
    day_of_week: int?,          # 0=Sun..6=Sat
    hour_local: int?            # 24h
  }
  token_hint: int?

Output (response) — strict TOON format
product_insight:
  external_id: str              # same as agent_call.external_id
  title: str
  summary: str                  # short summary, 3-6 lines
  insights: list[               # top 3 insights
    {text: str, source_url: str, confidence: "high" | "med" | "low"}
  ]
  roadmap: list[                # prioritized features
    { priority: "P0"|"P1"|"P2", title: str, description: str, impact_estimate: str, est_days: int, owner: str? }
  ]
  tasks: list[                  # actionable tasks to add to calendar
    { title: str, owner: str?, est_hours: int, due_in_days: int, calendar_event: bool }
  ]
  feasibility: {                # filled only if require_feasibility_check=true
    feasible: bool,
    constraints: list[str]?,
    engineer_notes: str?
  }
  created_ts: iso8601
  sources: list[{url: str, title: str}]
  token_hint: int?


Validation rules

feasibility must be present if require_feasibility_check true. Or contain {feasible: null} if engine couldn't respond.

Orchestrator must store product_insight in product_insights table and create calendar tasks marked calendar_event: true.

2) Finance Manager Agent — agent.finance_manager.toon
Input payload
finance_request:
  prompt: str                     # e.g., "Prepare next-month budget"
  period: { from: iso8601, to: iso8601 }?
  accounting_data_ref: str?       # pointer to DB summary or storage_url (preferred)
  allowed_budget_categories: list[str]?  # optional
  legal_info_query: str?          # if finance agent needs to scrape legal sources
  token_hint: int?

Output payload
finance_plan:
  external_id: str
  period: { from: iso8601, to: iso8601 }
  summary: str                    # executive summary
  income_forecast: list[{source: str, amount: number}]
  expense_forecast: list[{category: str, amount: number, notes: str?}]
  cashflow_projection: {opening:number, closing:number, monthly_net:number}
  recommendations: list[{text: str, urgency: "high"|"med"|"low"}]
  legal_notes: list[{text: str, source: str}]?  # if legal_info_query used
  created_ts: iso8601
  token_hint: int?


Validation rules

If accounting_data_ref missing but prompt requires numbers, return error field with explanation.

Save as budgets or a finance_reports table row.

3) Marketing Strategist Agent — agent.marketing_strategist.toon
Input payload
marketing_request:
  prompt: str                      # e.g., "Write IG post + YT short script about onboarding feature"
  product_insight_ref: uuid?       # optional reference to product insight
  audience: {region: str?, persona: str?}
  channels: list["instagram"|"youtube"|"x"|"facebook"|"threads"|"linkedin"|"medium"|"producthunt"|"reddit"|"dev.to"|"githubpages"]
  requirements: {length: "short"|"long", tone: "casual"|"professional"|"edgy"}
  include_camera_angles: bool = true
  include_sfx: bool = false
  token_hint: int?

Output payload
marketing_package:
  external_id: str
  created_ts: iso8601
  channel_outputs: map{                 # key = channel name -> content block
    instagram: { caption: str, hashtags: list[str], image_prompt: str? },
    youtube: { title: str, script: str, thumbnail_prompt: str? },
    x: { thread: list[str] },
    producthunt: { description: str, launch_notes: str }
    ...
  }
  ugc_ad_variants: list[{variant_id: str, script: str, duration_sec: int}]
  camera_angles: list[{scene:int, angle: str, notes: str}]?
  sfx_notes: list[str]?
  seo_meta: {title: str, description: str, keywords: list[str]}?
  token_hint: int?


Validation rules

Provide per-channel required fields. Mark warnings if more context needed.

Save marketing_package to agent_tasks and possibly content table.

4) LeadGen / Scraper Agent — agent.leadgen_scraper.toon
Input payload
scrape_request:
  external_id: str
  ts: iso8601
  niche: str
  location: str?
  max_results: int = 200
  domains_allowlist: list[str]?    # optional domain whitelist
  dedupe_by: "email" | "domain" | "company"
  crawl_depth: int = 2
  politeness: { delay_ms: int = 3000, max_concurrent_pages: int = 4 }
  cache_ttl_seconds: int?          # override defaults
  token_hint: int?

Output payload (one batch per scrape_result)
scrape_result:
  external_id: str
  ts: iso8601
  status: enum(done|partial|failed)
  leads: list[
    {
      id: uuid,
      name: str?,
      email: str?,
      company: str?,
      role: str?,
      source_url: str,
      confidence: "high"|"med"|"low",
      metadata: map?      # raw data like linkedin url, phone etc
    }
  ]
  stats: {found:int, saved:int, duplicates:int}
  storage_url: str?      # optional raw pages bundle
  token_hint: int?


Validation & processing

Worker must dedupe before insert; saved leads each get id and history: [].

If status=partial, include reason in top-level response.

Save leads to leads table and emit real-time update.

5) Outbound Emailer Agent — agent.outbound_emailer.toon
Input payload
email_campaign:
  external_id: str
  ts: iso8601
  from: {name: str, email: str}
  subject_template: str            # may include placeholders like {{first_name}}
  body_template: str               # plaintext template + optional html_template
  personalization_fields: list[str] # fields to replace (email, first_name, company, etc)
  leads_ref: list[uuid]            # list of lead ids to send to
  send_rate_per_min: int = 60      # throttle
  followup_sequence: list[{delay_days:int, template:str}]?
  tracking: {open_tracking: bool, reply_hook: str?} # reply_hook = webhook endpoint
  token_hint: int?

Output payload (campaign result summary)
email_campaign_result:
  external_id: str
  ts: iso8601
  campaign_id: uuid
  scheduled: bool
  send_stats: {total:int, queued:int, sent:int, failed:int}
  failures: list[{lead_id: uuid, error: str}]?
  token_hint: int?


Processing rules

Worker must enqueue sends and adhere to send_rate_per_min.

Outbound must log each send in email_events with direction=outbound.

If replies arrive, reply_hook receives inbound TOON email and triggers auto-reply rules.

6) Booking & Call Prep Agent — agent.booking_callprep.toon
Input payload
call_prep_request:
  external_id: str
  ts: iso8601
  booking_ref: str | uuid         # booking.external_id or calendar_events.id
  lead_profile: {
    name: str,
    email: str,
    company: str?,
    role: str?,
    notes: str?
  }?
  booking_answers: map?           # Q&A from booking form
  tone: "consultative"|"sales"|"technical"
  expected_duration_min: int = 15
  token_hint: int?

Output payload
call_script:
  external_id: str
  ts: iso8601
  intro: str                     # 1-2 minute tailored intro
  top_questions: list[str]       # top 3-5 discovery questions
  demo_checklist: list[str]      # items to show if demo
  objections_prepare: list[{objection: str, reply: str}]
  closing_play: str              # closing ask (trial/signup)
  followup_tasks: list[{task: str, owner: str, due_in_days: int}]
  created_ts: iso8601
  token_hint: int?


Processing rules

Save call_script and attach to calendar_events metadata. Notify user when ready.

7) Engineer Agent (Claude) — agent.engineer.toon

This agent is used for triage, feasibility, and incident playbooks.

Input payload
engineer_request:
  external_id: str
  ts: iso8601
  purpose: enum("feasibility_check" | "incident_triage" | "remediation_suggestion")
  payload:
    # for feasibility_check:
    feature_description?: str
    infra_snapshot?: {ram_mb: int, cpu_cores: int, services: list[str], runtime: str}
    constraints?: list[str]

    # for incident_triage:
    alert_id?: str
    logs?: str?                  # last N lines (use storage_url if large)
    metrics?: map?
    recent_deploys?: list[{id:str, ts:iso8601, by:str}]?

    # for remediation_suggestion:
    current_state?: map?
    attempted_fixes?: list[str]?

  urgency: "high" | "normal" | "low"
  token_hint: int?

Output payload
engineer_response:
  external_id: str
  ts: iso8601
  result:
    feasible?: bool
    feasibility_details?: str
    constraints?: list[str]
    immediate_actions?: list[{action: str, command_hint: str?, risk: "low"|"med"|"high"}]
    root_cause_hypothesis?: str
    suggested_prs_or_links?: list[{title: str, url: str}]?   # point to playbook or repo
    estimated_effort_days?: int?
  severity_override?: "escalate" | "ok"
  created_ts: iso8601
  token_hint: int?


Processing & safety

For incident_triage include immediate_actions that are read-only recommended steps unless you explicitly allow auto-remediation.

Worker must persist response into alerts or incident_playbooks. If severity_override == escalate, call notification pipeline (SMS/Push).

Validation, size & performance hints (copy/paste)

Max body_text for emails: 100k chars; else use storage_url.

Max last_logs: 200k chars; else use storage_url.

Token_hint: approximate #tokens (1 token ≈ 4 chars), helpful for deciding summarization.

Model call batch size: combine at most 10 leads or 8 scrape_result items into a single model prompt; otherwise chunk and call multiple times.

Agent timeouts (worker expectation): product/marketing/leadgen = 20s; engineer triage = 60s. If longer, mark task delayed and return cached or partial response.

Quick mapping table: TOON → DB tables (for implementers)

webhook.gmail.inbound.toon → email_events + leads (match)

webhook.scrape.done.toon → scrapes table + Supabase Storage (raw)

webhook.booking.create.toon → calendar_events + call_scripts

webhook.monitor.alert.toon → alerts + incident_playbooks

agent.product_manager.toon → product_insights, agent_tasks, calendar tasks

agent.finance_manager.toon → finance_reports (new table)

agent.marketing_strategist.toon → marketing_package (new table)

agent.leadgen_scraper.toon → leads table and leads.history

agent.outbound_emailer.toon → email_events and campaigns table

agent.booking_callprep.toon → call_scripts + calendar_events

agent.engineer.toon → alerts and incident_playbooks

How the mobile app communicates with your backend

Use the same REST/GraphQL endpoints or Next.js API routes.

Use Supabase Auth for authentication (works in web & mobile). On mobile you’ll use OAuth via system browser (see details).

All secrets (OpenRouter keys, Gmail server secrets) must remain server-side; mobile only calls your backend that signs/forwards safe requests.

Key integrations & modules for mobile

Auth: Supabase Auth + OAuth via system browser (deep links). In React Native use expo-auth-session or react-native-app-auth.

API client: @supabase/supabase-js (with react-native-url-polyfill + fetch polyfill) or plain fetch with JWT header from Supabase session.

Push notifications:

For PWA: Web Push (Service Worker), limited on Android Chrome.

For native Expo app: Expo Notifications (backed by FCM on Android). Use Firebase Cloud Messaging for production push.

Offline/local storage: AsyncStorage (React Native) or IndexedDB for PWA; sync with Supabase when online.

Gmail: On mobile, prefer backend Gmail integration (server uses Gmail API). For user OAuth login to Gmail (if needed), use system browser and OAuth redirect.

Deep links: configure to open booking links and authentication redirects from browser/email.

Step-by-step: Expo managed workflow (native APK) — local build & install

If you want a real Android APK you can install on your phone:

Dev: Run on your device (no build)

Install Expo Go from Play Store on phone.

In repo apps/mobile run:

npm install
expo start


Scan QR code with Expo Go app → runs your app instantly (fast iteration).

Local build (produce APK) — free, no EAS required (React Native < 0.71 older method)

Note: Expo increasingly pushes EAS Build; classic expo build:android may be deprecated. If you want local builds without EAS, use React Native CLI or set up local gradle builds.

Using React Native CLI (if you eject / or use bare workflow)

Prerequisite: Android Studio + Android SDK installed.

Build release APK:

Generate keystore:

keytool -genkeypair -v -keystore my-release-key.keystore -alias my-key-alias -keyalg RSA -keysize 2048 -validity 10000


Place keystore in android/app and set gradle.properties with MYAPP_RELEASE_STORE_FILE, MYAPP_RELEASE_KEY_ALIAS, MYAPP_RELEASE_STORE_PASSWORD, MYAPP_RELEASE_KEY_PASSWORD.

Build:

cd android
./gradlew assembleRelease


APK path: android/app/build/outputs/apk/release/app-release.apk

Install APK on device:

adb install -r android/app/build/outputs/apk/release/app-release.apk


(Enable USB debugging on device; install Android SDK platform-tools to get adb.)

Using Expo + EAS (recommended for simplicity but EAS may have costs)

Install eas-cli.

Configure eas.json.

Build:

eas build -p android --profile preview


Download the .apk or .aab and install or upload to Play Console.

If you want zero-cost local approach — use React Native CLI local builds. Expo + EAS are easiest but may incur small fees for EAS hosted builds.


PWA (Add to Home screen) — no build. Recommended for fastest iteration.

Auth & Gmail OAuth on mobile — best practice

Supabase Auth:

Use supabase.auth.signInWithOAuth({provider:'google'}) on web.

On mobile, use system browser OAuth or expo-auth-session. Use deep links / universal links to catch the auth redirect. Store session token securely (SecureStore on Expo, Keychain/Keystore on native).

Gmail API:

Your backend handles Gmail API requests with a service account / OAuth refresh token stored server-side. Mobile app should never embed Gmail client secrets.

For account-specific Gmail access (if user must link Gmail), use OAuth flow via backend that exchanges code for refresh token and stores it securely.

Push notifications & background tasks

PWA Push: use Web Push (VAPID keys) — works on Chrome/Edge for Android. Setup server to send push messages via web-push with subscription endpoints saved in DB.

Native push (Expo):

Configure Firebase project for FCM.

Expo Notifications SDK integrates with FCM for Android.

Save push tokens to Supabase and send via your backend or via Expo push service.

Background tasks: For mobile background sync (e.g., syncing leads), use BackgroundFetch or periodic background worker libraries. For PWA background sync use Background Sync API (limited support).

Storage, offline sync & large files

Local cache:

Expo/React Native: @react-native-async-storage/async-storage or MMKV for performance.

PWA: IndexedDB via localForage.

Sync strategy: write-through approach — UI writes locally and enqueues background sync to Supabase worker; handle conflicts server-side.

Large files / images: upload directly to Supabase Storage using pre-signed URLs from server.

Security & secrets

Never store OpenRouter or Gmail secrets in mobile app. Always call your backend which holds secrets.

Use HTTPS always, validate JWT tokens on backend.

Use SecureStore (Expo) or Keychain/Keystore to store tokens securely on the device.

Protect API endpoints with Supabase auth checks and internal JWT for agent-to-agent calls.

Dev & CI suggestions

Local dev: run Next.js (yarn dev) + Expo (expo start) concurrently. Use tunneling (ngrok) for mobile if your backend is on localhost.

CI: use GitHub Actions to build Android AAB (gradle) and publish to Play Console (internal track) if you want automation.

Testing: use Play Store internal testing for sharing with a few testers; or distribute via Firebase App Distribution.

Quick checklist to ship Android app (start → install)

Create mono-repo skeleton (Next.js + Expo + packages/ui + packages/lib).

Implement shared API client (packages/lib/supabaseClient.ts).

Build minimal mobile screens: Login, Chat, Leads Sheet (reuse ui components).

Test in Expo Go on device.

Choose install path:

PWA: enable next-pwa, deploy to Vercel, add to home screen.

APK: perform local gradle build and adb install, or use EAS/Play Store for distribution.

Integrate secure storage for JWT and enable background sync/push tokens.

Minimal commands & examples

Start Next.js web:

cd apps/web
pnpm install
pnpm dev


Start Expo mobile:

cd apps/mobile
pnpm install
expo start


Build React Native APK (local, bare workflow):

cd apps/mobile/android
./gradlew assembleRelease
adb install -r app/build/outputs/apk/release/app-release.apk


Generate keystore:

keytool -genkeypair -v -keystore my-release-key.keystore \
  -alias my-key-alias -keyalg RSA -keysize 2048 -validity 10000

Small note about using Supabase on React Native

Add polyfills:

npm install react-native-url-polyfill


and in entry file:

import 'react-native-url-polyfill/auto'


Use @supabase/supabase-js as usual; ensure fetch polyfill present.

Final recommended path for you (practical)

Make the Next.js front-end a PWA — get fast product instantly installable on your Android. (Do this first.)

Start an Expo mobile app that reuses your packages/ui components — let Expo/React Native Web share components with Next.js. Test inside Expo Go.

When you want native install: build a local APK via React Native CLI or use EAS (if comfortable). For private personal use, sideload via adb install is fastest.

Keep all sensitive keys server-side; mobile only talks to your backend./resu