"""
Platform-specific agents for social media posting.

✅ ALL AGENTS IN THIS MODULE PROVIDE REAL MULTI-AGENT VALUE

Each platform has:
- Different API authentication
- Different content format requirements
- Different character limits and media handling
- Different posting logic

These agents genuinely need to be separate because they interface with
completely different external systems.
"""

from .linkedin_agent import LinkedInAgent
from .twitter_agent import TwitterAgent
from .instagram_agent import InstagramAgent
from .substack_agent import SubstackAgent

__all__ = [
    "LinkedInAgent",
    "TwitterAgent",
    "InstagramAgent",
    "SubstackAgent"
]
