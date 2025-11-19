-- ================================================
-- Conversations Table Schema for Supabase
-- Run this in Supabase SQL Editor to create the conversations table
-- ================================================

-- Create conversations table
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    title TEXT DEFAULT 'New Chat',
    agent_type TEXT,  -- Primary agent for this conversation (optional)
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create index on user_id for fast lookups
CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id);

-- Create index on updated_at for sorting
CREATE INDEX IF NOT EXISTS idx_conversations_updated_at ON conversations(updated_at DESC);

-- Enable Row Level Security (RLS)
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;

-- Create policy to allow users to see their own conversations
CREATE POLICY "Users can view their own conversations"
    ON conversations
    FOR SELECT
    USING (true);  -- Change to (auth.uid()::text = user_id) if using Supabase Auth

-- Create policy to allow users to create conversations
CREATE POLICY "Users can create conversations"
    ON conversations
    FOR INSERT
    WITH CHECK (true);  -- Change to (auth.uid()::text = user_id) if using Supabase Auth

-- Create policy to allow users to update their own conversations
CREATE POLICY "Users can update their own conversations"
    ON conversations
    FOR UPDATE
    USING (true);  -- Change to (auth.uid()::text = user_id) if using Supabase Auth

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to auto-update updated_at
DROP TRIGGER IF EXISTS update_conversations_updated_at ON conversations;
CREATE TRIGGER update_conversations_updated_at
    BEFORE UPDATE ON conversations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ================================================
-- NOTE: The conversation_messages table should already exist
-- If not, uncomment and run this:
-- ================================================

-- CREATE TABLE IF NOT EXISTS conversation_messages (
--     id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
--     conversation_id TEXT NOT NULL,
--     role TEXT NOT NULL,  -- 'user', 'assistant', 'system'
--     content TEXT NOT NULL,
--     agent_name TEXT,  -- Which agent sent this message
--     metadata JSONB DEFAULT '{}'::jsonb,
--     created_at TIMESTAMPTZ DEFAULT NOW()
-- );

-- CREATE INDEX IF NOT EXISTS idx_conversation_messages_conversation_id
--     ON conversation_messages(conversation_id);

-- CREATE INDEX IF NOT EXISTS idx_conversation_messages_created_at
--     ON conversation_messages(created_at);

-- ALTER TABLE conversation_messages ENABLE ROW LEVEL SECURITY;

-- CREATE POLICY "Users can view messages"
--     ON conversation_messages
--     FOR SELECT
--     USING (true);

-- CREATE POLICY "Users can create messages"
--     ON conversation_messages
--     FOR INSERT
--     WITH CHECK (true);
