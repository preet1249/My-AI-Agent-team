-- ============================================
-- AI Agent Team - Fixed Supabase Schema
-- Simplified for Supabase compatibility
-- ============================================

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- 1. AGENT TASKS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS agent_tasks (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id text NOT NULL,
  agent_name text NOT NULL,
  input jsonb NOT NULL,
  output jsonb,
  status text DEFAULT 'queued',
  error text,
  external_id text,
  created_at timestamptz DEFAULT now(),
  completed_at timestamptz
);

CREATE INDEX IF NOT EXISTS idx_agent_tasks_user ON agent_tasks(user_id);
CREATE INDEX IF NOT EXISTS idx_agent_tasks_status ON agent_tasks(status);
CREATE INDEX IF NOT EXISTS idx_agent_tasks_created ON agent_tasks(created_at DESC);
CREATE UNIQUE INDEX IF NOT EXISTS idx_agent_tasks_external ON agent_tasks(external_id);

-- ============================================
-- 2. LEADS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS leads (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id text NOT NULL,
  email text,
  company text,
  score integer DEFAULT 0,
  metadata jsonb DEFAULT '{}'::jsonb,
  history jsonb DEFAULT '[]'::jsonb,
  status text DEFAULT 'new',
  created_at timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_leads_user ON leads(user_id);
CREATE INDEX IF NOT EXISTS idx_leads_email ON leads(email);
CREATE INDEX IF NOT EXISTS idx_leads_score ON leads(score DESC);

-- ============================================
-- 3. EMAIL EVENTS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS email_events (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id text NOT NULL,
  lead_id uuid REFERENCES leads(id),
  event_type text NOT NULL,
  metadata jsonb DEFAULT '{}'::jsonb,
  created_at timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_email_events_user ON email_events(user_id);
CREATE INDEX IF NOT EXISTS idx_email_events_lead ON email_events(lead_id);
CREATE INDEX IF NOT EXISTS idx_email_events_type ON email_events(event_type);

-- ============================================
-- 4. PRODUCT INSIGHTS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS product_insights (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id text NOT NULL,
  title text NOT NULL,
  content text,
  tags text[],
  priority text DEFAULT 'medium',
  source text,
  metadata jsonb DEFAULT '{}'::jsonb,
  created_at timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_insights_user ON product_insights(user_id);
CREATE INDEX IF NOT EXISTS idx_insights_created ON product_insights(created_at DESC);

-- ============================================
-- 5. CALENDAR EVENTS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS calendar_events (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id text NOT NULL,
  title text NOT NULL,
  start_time timestamptz NOT NULL,
  duration_minutes integer DEFAULT 30,
  metadata jsonb DEFAULT '{}'::jsonb,
  created_at timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_calendar_user ON calendar_events(user_id);
CREATE INDEX IF NOT EXISTS idx_calendar_start ON calendar_events(start_time);

-- ============================================
-- 6. ALERTS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS alerts (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id text NOT NULL,
  type text NOT NULL,
  message text NOT NULL,
  read boolean DEFAULT false,
  metadata jsonb DEFAULT '{}'::jsonb,
  created_at timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_alerts_user ON alerts(user_id);
CREATE INDEX IF NOT EXISTS idx_alerts_read ON alerts(read);
CREATE INDEX IF NOT EXISTS idx_alerts_created ON alerts(created_at DESC);

-- ============================================
-- 7. SCRAPES TABLE (Cache)
-- ============================================
CREATE TABLE IF NOT EXISTS scrapes (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  url text NOT NULL,
  content text,
  metadata jsonb DEFAULT '{}'::jsonb,
  status text DEFAULT 'completed',
  created_at timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_scrapes_url ON scrapes(url);
CREATE INDEX IF NOT EXISTS idx_scrapes_created ON scrapes(created_at DESC);

-- ============================================
-- 8. WEBHOOK EVENTS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS webhook_events (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  source text NOT NULL,
  event_type text NOT NULL,
  payload jsonb NOT NULL,
  processed boolean DEFAULT false,
  created_at timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_webhooks_source ON webhook_events(source);
CREATE INDEX IF NOT EXISTS idx_webhooks_processed ON webhook_events(processed);

-- ============================================
-- 9. CALL SCRIPTS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS call_scripts (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id text NOT NULL,
  lead_id uuid REFERENCES leads(id),
  meeting_type text,
  script jsonb NOT NULL,
  metadata jsonb DEFAULT '{}'::jsonb,
  created_at timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_scripts_user ON call_scripts(user_id);
CREATE INDEX IF NOT EXISTS idx_scripts_lead ON call_scripts(lead_id);

-- ============================================
-- 10. CAMPAIGNS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS campaigns (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id text NOT NULL,
  name text NOT NULL,
  channel text DEFAULT 'email',
  status text DEFAULT 'draft',
  metadata jsonb DEFAULT '{}'::jsonb,
  created_at timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_campaigns_user ON campaigns(user_id);
CREATE INDEX IF NOT EXISTS idx_campaigns_status ON campaigns(status);

-- ============================================
-- 11. DOMAIN BACKOFF TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS domain_backoff (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  domain text NOT NULL UNIQUE,
  backoff_until timestamptz NOT NULL,
  reason text,
  created_at timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_backoff_domain ON domain_backoff(domain);
CREATE INDEX IF NOT EXISTS idx_backoff_until ON domain_backoff(backoff_until);

-- ============================================
-- 12. CONVERSATION MESSAGES TABLE (Memory)
-- ============================================
CREATE TABLE IF NOT EXISTS conversation_messages (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  conversation_id text NOT NULL,
  role text NOT NULL,
  content text NOT NULL,
  agent_name text,
  metadata jsonb DEFAULT '{}'::jsonb,
  created_at timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_messages_conversation ON conversation_messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_created ON conversation_messages(created_at DESC);

-- ============================================
-- SUCCESS! All 12 tables created
-- ============================================
