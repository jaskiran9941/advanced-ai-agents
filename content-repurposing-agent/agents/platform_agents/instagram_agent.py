"""
Instagram Platform Agent

✅ REAL MULTI-AGENT VALUE
Why: Instagram requires images, has unique caption format, and different API.
"""
from typing import Dict, Any, Optional, List
from agents.base_agent import BaseAgent
from tools.social_tools import post_to_instagram

class InstagramAgent(BaseAgent):
    """Agent specialized in Instagram content formatting and posting."""

    def __init__(self, llm_provider: str = "gemini"):
        super().__init__(
            name="Instagram_Publisher",
            role="Instagram content and publishing specialist",
            llm_provider=llm_provider,
            tools=[post_to_instagram]
        )

    def _default_instructions(self) -> str:
        return """You are an Instagram content specialist.

Instagram caption best practices:
- 150-200 words for engagement
- Casual, authentic, relatable tone
- Strong opening hook (first 125 chars visible)
- Line breaks for readability
- Storytelling or lifestyle angle
- CTA: ask to like, save, share, or comment
- Emojis sparingly and naturally
- 10-15 hashtags (mix popular + niche)

Instagram is visual-first, personal, and community-focused."""

    def format_and_post(
        self,
        content: str,
        image_path: str,
        hashtags: Optional[List[str]] = None,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """Format caption and post to Instagram."""

        caption = self.optimize_for_instagram(content, hashtags)

        result = {
            "caption": caption,
            "image_path": image_path,
            "character_count": len(caption),
            "platform": "instagram"
        }

        if not dry_run:
            post_result = post_to_instagram(caption, image_path)
            result["post_result"] = post_result

        return result

    def optimize_for_instagram(
        self,
        content: str,
        hashtags: Optional[List[str]] = None
    ) -> str:
        """Optimize content for Instagram."""

        hashtag_note = f"Use these hashtags: {' '.join(hashtags)}" if hashtags else "Generate 10-15 relevant hashtags"

        task = f"""Optimize this content for Instagram:

{content}

Make it:
- Casual, authentic, relatable
- 150-200 words
- Strong hook in first line
- Line breaks between thoughts
- Lifestyle or personal angle
- End with engaging CTA
- {hashtag_note}

Return the optimized Instagram caption."""

        response = self.run(task)
        return response.content if hasattr(response, 'content') else str(response)
