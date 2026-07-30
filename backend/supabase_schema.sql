# StreamGuard AI - Supabase Database Schema
# Run these SQL commands in Supabase SQL Editor

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =============================================
-- Stream Sessions Table
-- =============================================
CREATE TABLE IF NOT EXISTS stream_sessions (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    youtube_video_id TEXT,
    streamer_name TEXT NOT NULL DEFAULT 'Streamer',
    demo_mode BOOLEAN DEFAULT TRUE,
    is_active BOOLEAN DEFAULT TRUE,
    started_at TIMESTAMPTZ DEFAULT NOW(),
    ended_at TIMESTAMPTZ,
    total_revenue FLOAT DEFAULT 0.0,
    total_chats INTEGER DEFAULT 0,
    chats_read INTEGER DEFAULT 0,
    chats_skipped INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================
-- Super Chats Table
-- =============================================
CREATE TABLE IF NOT EXISTS super_chats (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    session_id UUID REFERENCES stream_sessions(id) ON DELETE CASCADE,
    author_name TEXT NOT NULL,
    author_channel_id TEXT,
    message TEXT NOT NULL,
    amount FLOAT NOT NULL DEFAULT 0.0,
    currency TEXT DEFAULT 'USD',
    
    -- AI Analysis Results
    sentiment TEXT DEFAULT 'neutral',
    intent TEXT DEFAULT 'other',
    priority_score INTEGER DEFAULT 50,
    tier TEXT DEFAULT 'bronze',
    risk_level TEXT DEFAULT 'low',
    is_safe BOOLEAN DEFAULT TRUE,
    moderation_flags JSONB DEFAULT '[]'::jsonb,
    suggested_reply TEXT,
    
    -- Status
    status TEXT DEFAULT 'pending',
    received_at TIMESTAMPTZ DEFAULT NOW(),
    read_at TIMESTAMPTZ,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================
-- Indexes for Performance
-- =============================================
CREATE INDEX IF NOT EXISTS idx_super_chats_session 
    ON super_chats(session_id);
    
CREATE INDEX IF NOT EXISTS idx_super_chats_status 
    ON super_chats(status);
    
CREATE INDEX IF NOT EXISTS idx_super_chats_priority 
    ON super_chats(priority_score DESC);

CREATE INDEX IF NOT EXISTS idx_sessions_active 
    ON stream_sessions(is_active);

-- =============================================
-- Row Level Security (RLS)
-- =============================================
ALTER TABLE stream_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE super_chats ENABLE ROW LEVEL SECURITY;

-- Allow all operations for now (configure per-user in production)
CREATE POLICY "Allow all on stream_sessions" ON stream_sessions
    FOR ALL USING (true) WITH CHECK (true);

CREATE POLICY "Allow all on super_chats" ON super_chats
    FOR ALL USING (true) WITH CHECK (true);
