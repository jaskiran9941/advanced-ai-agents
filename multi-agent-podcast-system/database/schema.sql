-- Multi-Agent Podcast System Database Schema
-- SQLite database for learning and state management

-- Enable foreign key constraints
PRAGMA foreign_keys = ON;

-- Performance optimizations
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA cache_size = -64000;  -- 64MB cache
PRAGMA temp_store = MEMORY;

-- ============================================================================
-- USERS & PREFERENCES
-- ============================================================================

-- Core user tracking
CREATE TABLE IF NOT EXISTS users (
    user_id TEXT PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    preferences_json TEXT,  -- JSON blob for flexibility: {"topics": [...], "length": "detailed"}
    last_active TIMESTAMP,
    email TEXT,
    timezone TEXT DEFAULT 'UTC'
);

-- Learned preferences (discovered over time from behavior)
CREATE TABLE IF NOT EXISTS learned_preferences (
    preference_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    preference_key TEXT NOT NULL,  -- 'preferred_topics', 'summary_depth', 'delivery_time'
    preference_value TEXT NOT NULL,
    confidence REAL CHECK(confidence BETWEEN 0 AND 1),  -- how sure we are (0-1)
    learned_from TEXT CHECK(learned_from IN ('explicit', 'implicit')),  -- user set or inferred
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    evidence_count INTEGER DEFAULT 1,  -- how many interactions support this
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_learned_prefs_user ON learned_preferences(user_id, preference_key);

-- ============================================================================
-- CONTENT TRACKING
-- ============================================================================

-- Episodes and podcasts (everything user might interact with)
CREATE TABLE IF NOT EXISTS content (
    content_id TEXT PRIMARY KEY,
    content_type TEXT CHECK(content_type IN ('episode', 'podcast')),
    title TEXT NOT NULL,
    description TEXT,
    metadata_json TEXT,  -- {tags, topics, length, difficulty, podcast_name, etc.}
    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source TEXT,  -- 'itunes', 'rss', 'manual'
    embedding_vector BLOB  -- Optional: for semantic search
);

CREATE INDEX IF NOT EXISTS idx_content_type ON content(content_type);
CREATE INDEX IF NOT EXISTS idx_content_first_seen ON content(first_seen DESC);

-- Full-text search for content
CREATE VIRTUAL TABLE IF NOT EXISTS content_fts USING fts5(
    content_id,
    title,
    description,
    content='content',
    tokenize='porter unicode61'
);

-- ============================================================================
-- USER INTERACTIONS
-- ============================================================================

-- What users do with content (clicks, saves, dismisses, etc.)
CREATE TABLE IF NOT EXISTS interactions (
    interaction_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    content_id TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    event_type TEXT NOT NULL,  -- 'click', 'save', 'skip', 'read', 'share', 'dismiss'
    context_json TEXT,  -- {time_of_day, device, location, user_state}
    duration_seconds INTEGER,  -- how long they engaged
    scroll_depth REAL,  -- % of content scrolled (0-1)
    completion_rate REAL,  -- % completed (0-1)
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (content_id) REFERENCES content(content_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_interactions_user_time ON interactions(user_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_interactions_content ON interactions(content_id);
CREATE INDEX IF NOT EXISTS idx_interactions_event_type ON interactions(event_type);

-- ============================================================================
-- AGENT DECISIONS
-- ============================================================================

-- Track every decision made by any agent
CREATE TABLE IF NOT EXISTS agent_decisions (
    decision_id TEXT PRIMARY KEY,
    agent_name TEXT NOT NULL,  -- 'discovery', 'curator', 'personalization', 'delivery', 'orchestrator'
    user_id TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    decision_type TEXT NOT NULL,  -- 'recommend', 'filter', 'summarize', 'schedule', 'route'
    input_data_json TEXT NOT NULL,  -- Full input the agent received
    output_data_json TEXT NOT NULL,  -- Full output the agent produced
    reasoning TEXT,  -- AI's explanation of its decision
    confidence_score REAL CHECK(confidence_score BETWEEN 0 AND 1),
    execution_time_ms INTEGER,  -- How long this decision took
    parent_task_id TEXT,  -- Link to orchestrator task
    dependencies_json TEXT,  -- List of decision_ids this depends on
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_decisions_agent_user ON agent_decisions(agent_name, user_id);
CREATE INDEX IF NOT EXISTS idx_decisions_timestamp ON agent_decisions(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_decisions_parent_task ON agent_decisions(parent_task_id);

-- ============================================================================
-- FEEDBACK LOOP
-- ============================================================================

-- Link agent decisions to user interactions (outcome tracking)
CREATE TABLE IF NOT EXISTS decision_outcomes (
    outcome_id TEXT PRIMARY KEY,
    decision_id TEXT NOT NULL,
    interaction_id TEXT,  -- NULL if no interaction happened
    success_metric TEXT NOT NULL,  -- 'clicked', 'saved', 'ignored', 'dismissed'
    success_value REAL CHECK(success_value BETWEEN -1 AND 1),  -- 1.0 = great, 0.0 = neutral, -1.0 = bad
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,  -- Additional context about the outcome
    FOREIGN KEY (decision_id) REFERENCES agent_decisions(decision_id) ON DELETE CASCADE,
    FOREIGN KEY (interaction_id) REFERENCES interactions(interaction_id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_outcomes_decision ON decision_outcomes(decision_id);
CREATE INDEX IF NOT EXISTS idx_outcomes_timestamp ON decision_outcomes(timestamp DESC);

-- ============================================================================
-- AGENT PERFORMANCE TRACKING
-- ============================================================================

-- Aggregated performance metrics per agent
CREATE TABLE IF NOT EXISTS agent_performance (
    metric_id TEXT PRIMARY KEY,
    agent_name TEXT NOT NULL,
    time_window TEXT NOT NULL,  -- 'hourly', 'daily', 'weekly'
    window_start TIMESTAMP NOT NULL,
    window_end TIMESTAMP NOT NULL,
    decisions_made INTEGER DEFAULT 0,
    avg_confidence REAL,
    success_rate REAL,  -- % of decisions with positive outcomes
    avg_response_time_ms INTEGER,
    total_api_cost REAL,  -- Estimated cost in dollars
    metadata_json TEXT  -- Additional metrics
);

CREATE INDEX IF NOT EXISTS idx_performance_agent_window ON agent_performance(agent_name, window_start DESC);

-- ============================================================================
-- USER SUBSCRIPTIONS
-- ============================================================================

-- Podcasts the user is subscribed to
CREATE TABLE IF NOT EXISTS user_subscriptions (
    subscription_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    podcast_id TEXT NOT NULL,  -- References content_id where content_type='podcast'
    subscribed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    priority INTEGER DEFAULT 5,  -- 1-10, user can prioritize certain podcasts
    active BOOLEAN DEFAULT 1,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (podcast_id) REFERENCES content(content_id) ON DELETE CASCADE,
    UNIQUE(user_id, podcast_id)
);

CREATE INDEX IF NOT EXISTS idx_subscriptions_user ON user_subscriptions(user_id);

-- ============================================================================
-- ORCHESTRATOR TASKS
-- ============================================================================

-- Track high-level tasks coordinated by orchestrator
CREATE TABLE IF NOT EXISTS orchestrator_tasks (
    task_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    user_goal TEXT NOT NULL,  -- Original user request
    intent_classification_json TEXT,  -- {primary_intent, required_agents, optional_agents}
    agent_sequence_json TEXT,  -- Ordered list of agents that executed
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    status TEXT CHECK(status IN ('pending', 'in_progress', 'completed', 'failed')),
    result_json TEXT,  -- Final aggregated result
    error_message TEXT,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_tasks_user_status ON orchestrator_tasks(user_id, status);
CREATE INDEX IF NOT EXISTS idx_tasks_started ON orchestrator_tasks(started_at DESC);

-- ============================================================================
-- ANALYTICS VIEWS
-- ============================================================================

-- View: User engagement summary
CREATE VIEW IF NOT EXISTS user_engagement AS
SELECT
    u.user_id,
    u.email,
    COUNT(DISTINCT i.interaction_id) as total_interactions,
    COUNT(DISTINCT CASE WHEN i.event_type = 'save' THEN i.interaction_id END) as saves,
    COUNT(DISTINCT CASE WHEN i.event_type = 'share' THEN i.interaction_id END) as shares,
    COUNT(DISTINCT CASE WHEN i.event_type = 'dismiss' THEN i.interaction_id END) as dismisses,
    AVG(i.duration_seconds) as avg_engagement_seconds,
    MAX(i.timestamp) as last_interaction
FROM users u
LEFT JOIN interactions i ON u.user_id = i.user_id
GROUP BY u.user_id;

-- View: Agent success rates
CREATE VIEW IF NOT EXISTS agent_success_rates AS
SELECT
    ad.agent_name,
    COUNT(ad.decision_id) as total_decisions,
    AVG(ad.confidence_score) as avg_confidence,
    CAST(COUNT(CASE WHEN do.success_value > 0.5 THEN 1 END) AS FLOAT) /
        NULLIF(COUNT(do.outcome_id), 0) as success_rate,
    AVG(ad.execution_time_ms) as avg_latency_ms
FROM agent_decisions ad
LEFT JOIN decision_outcomes do ON ad.decision_id = do.decision_id
WHERE ad.timestamp > datetime('now', '-7 days')
GROUP BY ad.agent_name;

-- View: Topic popularity (from content interactions)
CREATE VIEW IF NOT EXISTS topic_popularity AS
SELECT
    json_extract(c.metadata_json, '$.topics') as topic,
    COUNT(DISTINCT i.interaction_id) as interaction_count,
    COUNT(DISTINCT CASE WHEN i.event_type = 'save' THEN i.interaction_id END) as save_count,
    COUNT(DISTINCT CASE WHEN i.event_type = 'dismiss' THEN i.interaction_id END) as dismiss_count
FROM content c
JOIN interactions i ON c.content_id = i.content_id
WHERE json_extract(c.metadata_json, '$.topics') IS NOT NULL
GROUP BY topic
ORDER BY interaction_count DESC;

-- ============================================================================
-- SAMPLE DATA INSERTION (for testing)
-- ============================================================================

-- Create default user
INSERT OR IGNORE INTO users (user_id, email, preferences_json)
VALUES (
    'default_user',
    'user@example.com',
    '{"recent_topics": ["AI", "technology", "machine learning"], "preferred_length": "detailed", "skip_topics": ["sports", "politics"]}'
);

-- ============================================================================
-- CLEANUP & MAINTENANCE QUERIES
-- ============================================================================

-- Cleanup old interactions (older than 1 year)
-- DELETE FROM interactions WHERE timestamp < datetime('now', '-1 year');

-- Vacuum database periodically
-- VACUUM;

-- Analyze for query optimization
-- ANALYZE;
