"""
Substack Platform Agent

✅ REAL MULTI-AGENT VALUE
Why: Substack requires HTML formatting, newsletter structure, and its own publishing API.
"""
from typing import Dict, Any, Optional
from agents.base_agent import BaseAgent
from tools.social_tools import publish_to_substack

class SubstackAgent(BaseAgent):
    """Agent specialized in Substack newsletter formatting and publishing."""

    def __init__(self, llm_provider: str = "claude"):
        super().__init__(
            name="Substack_Publisher",
            role="Substack newsletter specialist",
            llm_provider=llm_provider,
            tools=[publish_to_substack]
        )

    def _default_instructions(self) -> str:
        return """You are a Substack newsletter specialist.

Substack content guidelines:
- Long-form: 800+ words
- Newsletter/editorial tone
- Personal, conversational but authoritative
- Clear structure: intro, body sections, conclusion
- Compelling headline and subtitle
- Subheadings for scannability
- Examples, stories, and data
- Strong CTA at end

Substack readers expect depth, insight, and a personal voice."""

    def format_and_publish(
        self,
        content: str,
        title: Optional[str] = None,
        subtitle: Optional[str] = None,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """Format content for Substack and publish."""

        # Generate title if not provided
        if not title:
            title = self._generate_title(content)

        # Optimize content for Substack
        formatted = self.optimize_for_substack(content)

        result = {
            "title": title,
            "subtitle": subtitle,
            "content": formatted,
            "word_count": len(formatted.split()),
            "platform": "substack"
        }

        if not dry_run:
            post_result = publish_to_substack(title, formatted, subtitle)
            result["post_result"] = post_result

        return result

    def optimize_for_substack(self, content: str) -> str:
        """Optimize content for Substack newsletter format."""

        task = f"""Optimize this content for Substack:

{content}

Make it:
- Long-form newsletter style (800+ words)
- Personal, conversational but authoritative
- Clear sections with ## subheadings
- Include introduction and conclusion
- Stories, examples, or data to support points
- End with strong CTA
- Format in Markdown

Return the optimized newsletter content."""

        response = self.run(task)
        return response.content if hasattr(response, 'content') else str(response)

    def _generate_title(self, content: str) -> str:
        """Generate a compelling title from content."""

        task = f"""Create a compelling newsletter title for this content:

{content[:500]}...

Requirements:
- Clear and specific
- Intriguing but not clickbait
- 6-12 words
- Captures main value proposition

Return ONLY the title, nothing else."""

        response = self.run(task)
        title = response.content if hasattr(response, 'content') else str(response)
        return title.strip().strip('"').strip("'")

    def generate_subtitle(self, content: str) -> str:
        """Generate a subtitle for the newsletter."""

        task = f"""Create a subtitle for this newsletter content:

{content[:500]}...

The subtitle should:
- Expand on the title
- 10-20 words
- Give readers a reason to read

Return ONLY the subtitle."""

        response = self.run(task)
        subtitle = response.content if hasattr(response, 'content') else str(response)
        return subtitle.strip().strip('"').strip("'")
