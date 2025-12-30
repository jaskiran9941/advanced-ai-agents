"""
LinkedIn Platform Agent

✅ REAL MULTI-AGENT VALUE
Why: LinkedIn has different API, professional tone requirements, and formatting needs.
"""
from typing import Dict, Any, Optional
from agents.base_agent import BaseAgent
from tools.social_tools import post_to_linkedin

class LinkedInAgent(BaseAgent):
    """Agent specialized in LinkedIn content formatting and posting."""

    def __init__(self, llm_provider: str = "claude"):
        super().__init__(
            name="LinkedIn_Publisher",
            role="LinkedIn content and publishing specialist",
            llm_provider=llm_provider,
            tools=[post_to_linkedin]
        )

    def _default_instructions(self) -> str:
        return """You are a LinkedIn content specialist.

Format content for LinkedIn:
- Professional, thought-leadership tone
- 200-300 words ideal (up to 3000 max)
- Short paragraphs (1-2 sentences)
- Storytelling or insight-driven
- End with discussion question
- 3-5 relevant hashtags

LinkedIn culture: Value-driven, professional networking, authentic expertise."""

    def format_and_post(
        self,
        content: str,
        image_url: Optional[str] = None,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """Format content for LinkedIn and post it."""

        formatted = self.optimize_for_linkedin(content)

        result = {
            "formatted_content": formatted,
            "character_count": len(formatted),
            "platform": "linkedin"
        }

        if not dry_run:
            post_result = post_to_linkedin(formatted, image_url)
            result["post_result"] = post_result

        return result

    def optimize_for_linkedin(self, content: str) -> str:
        """Optimize content for LinkedIn's professional audience."""

        task = f"""Optimize this content for LinkedIn:

{content}

Make it:
- Professional but authentic
- Value-driven (insights, lessons, expertise)
- Short paragraphs with line breaks
- Include a hook and discussion question
- 200-300 words
- Add 3-5 relevant hashtags at end

Return the optimized LinkedIn post."""

        response = self.run(task)
        return response.content if hasattr(response, 'content') else str(response)
