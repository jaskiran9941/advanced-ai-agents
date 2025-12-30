"""
Multi-agent system for content repurposing.

Agent Classification:
- ✅ REAL: Provides genuine multi-agent value (API calls, parallelization, tool use)
- 🔄 SEMI-REAL: Adds value through iteration/debate
- ⚠️ EDUCATIONAL: Could be done with single LLM, separated for learning
"""

from .base_agent import BaseAgent

__all__ = ["BaseAgent"]
