"""
Configuration for the Real-Time Collaborative Content Creator
This module defines all constants, model configs, and settings.

LEARNING POINT #1: Configuration Management
- Centralized config reduces hardcoding
- Makes it easy to swap models, APIs, or experiment with different agent parameters
- Enables environment-specific settings (dev, staging, prod)
"""

import os
from typing import Optional

# ============ API & MODEL CONFIGURATION ============
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
MODEL = "claude-3-5-sonnet-20241022"

# Temperature controls creativity vs consistency
# Lower temp (0.3-0.5): More deterministic, good for factual tasks
# Higher temp (0.7-1.0): More creative, good for brainstorming
RESEARCHER_TEMP = 0.5  # Lower - needs factual accuracy
WRITER_TEMP = 0.7      # Medium-high - needs creativity but consistency
EDITOR_TEMP = 0.4      # Lower - needs precise judgment
DESIGNER_TEMP = 0.6    # Medium - balanced approach

# ============ MEMORY CONFIGURATION ============
# LEARNING POINT #2: Memory Storage Strategy
# - Vector DB for semantic search of past findings
# - Metadata for tracking source credibility
# - TTL (time-to-live) for forgetting old information

MEMORY_CONFIG = {
      "max_findings_per_topic": 10,  # Prevent memory bloat
      "credibility_threshold": 0.6,   # Only store high-credibility sources
      "memory_ttl_days": 30,          # Forget findings older than 30 days
}

# ============ AGENT PARAMETERS ============
# LEARNING POINT #3: Agent-Specific Configurations
# Each agent has different roles and thus different parameters

RESEARCHER_CONFIG = {
      "role": "Research Specialist",
      "description": "Finds reliable sources and extracts structured information",
      "max_search_results": 5,
      "min_credibility_score": 0.7,
}

WRITER_CONFIG = {
      "role": "Content Writer",
      "description": "Creates engaging content based on research findings",
      "min_sources_required": 2,  # Must cite at least 2 sources
      "tone": "professional",
      "target_length": 800,  # words
}

EDITOR_CONFIG = {
      "role": "Editor & Reviewer",
      "description": "Reviews content for accuracy, clarity, and consistency",
      "feedback_focus": ["accuracy", "clarity", "consistency", "tone"],
      "revision_threshold": 0.6,  # Requires revision if feedback score < 0.6
}

DESIGNER_CONFIG = {
      "role": "Fact Checker & Designer",
      "description": "Validates claims against research findings and suggests visuals",
      "fact_check_threshold": 0.8,  # Claim must match research with 80% confidence
      "visual_suggestions_count": 3,
}

# ============ COLLABORATION PARAMETERS ============
# LEARNING POINT #4: Consensus & Conflict Resolution
# When agents disagree, we need a strategy to resolve

CONSENSUS_CONFIG = {
      "max_revision_rounds": 3,  # Prevent infinite loops
      "consensus_threshold": 0.7,  # 70% agent agreement needed
      "timeout_seconds": 120,      # Don't wait forever for agent responses
}

# ============ VECTOR DB CONFIGURATION ============
# For semantic memory and source tracking
VECTOR_DB_CONFIG = {
      "db_path": "./collaborative-content-creator/memory_db",
      "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
      "collection_name": "research_findings",
      "similarity_threshold": 0.5,
}
