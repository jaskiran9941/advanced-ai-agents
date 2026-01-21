"""
Database schema for Product-Market-Fit platform
"""

DATABASE_SCHEMA = """
-- Products/Ideas table
CREATE TABLE IF NOT EXISTS ideas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT DEFAULT 'default_user',
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    target_market TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'draft'
);

-- Research results
CREATE TABLE IF NOT EXISTS research (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    idea_id INTEGER NOT NULL,
    market_size TEXT,
    competitors TEXT,
    trends TEXT,
    pain_points TEXT,
    opportunities TEXT,
    sources TEXT,
    raw_findings TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (idea_id) REFERENCES ideas (id) ON DELETE CASCADE
);

-- ICP (Ideal Customer Profile)
CREATE TABLE IF NOT EXISTS icp_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    idea_id INTEGER NOT NULL,
    demographics TEXT,
    psychographics TEXT,
    behaviors TEXT,
    pain_points TEXT,
    goals TEXT,
    decision_criteria TEXT,
    confidence_score REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (idea_id) REFERENCES ideas (id) ON DELETE CASCADE
);

-- Synthetic Personas
CREATE TABLE IF NOT EXISTS personas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    icp_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    avatar_url TEXT,
    age INTEGER,
    occupation TEXT,
    location TEXT,
    background_story TEXT,
    personality_traits TEXT,
    communication_style TEXT,
    knowledge_base TEXT,
    preferences TEXT,
    objections TEXT,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (icp_id) REFERENCES icp_profiles (id) ON DELETE CASCADE
);

-- Chat conversations with personas
CREATE TABLE IF NOT EXISTS persona_conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    persona_id INTEGER NOT NULL,
    session_id TEXT NOT NULL,
    user_message TEXT NOT NULL,
    persona_response TEXT NOT NULL,
    sentiment TEXT,
    topics_discussed TEXT,
    insights_extracted TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (persona_id) REFERENCES personas (id) ON DELETE CASCADE
);

-- Workflow execution tracking
CREATE TABLE IF NOT EXISTS workflow_executions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    idea_id INTEGER NOT NULL,
    workflow_type TEXT,
    status TEXT,
    current_step TEXT,
    progress_percent INTEGER DEFAULT 0,
    step_message TEXT,
    input_state TEXT,
    output_state TEXT,
    error_message TEXT,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (idea_id) REFERENCES ideas (id) ON DELETE CASCADE
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_ideas_user_id ON ideas(user_id);
CREATE INDEX IF NOT EXISTS idx_ideas_status ON ideas(status);
CREATE INDEX IF NOT EXISTS idx_research_idea_id ON research(idea_id);
CREATE INDEX IF NOT EXISTS idx_icp_idea_id ON icp_profiles(idea_id);
CREATE INDEX IF NOT EXISTS idx_personas_icp_id ON personas(icp_id);
CREATE INDEX IF NOT EXISTS idx_personas_active ON personas(is_active);
CREATE INDEX IF NOT EXISTS idx_conversations_persona_id ON persona_conversations(persona_id);
CREATE INDEX IF NOT EXISTS idx_conversations_session ON persona_conversations(session_id);
CREATE INDEX IF NOT EXISTS idx_workflows_idea_id ON workflow_executions(idea_id);
"""
