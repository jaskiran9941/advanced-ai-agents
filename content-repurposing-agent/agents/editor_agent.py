"""
Editor/Quality Agent

🔄 SEMI-REAL VALUE
Why it adds some value: Having a separate "editor" perspective that critiques
and refines content can improve quality through iteration and debate.
Why it's semi-educational: You could achieve similar results with careful prompting
in a single agent, but the writer-editor dynamic does provide genuine benefits.

HONEST ASSESSMENT: This agent adds value when:
1. Content needs multiple rounds of refinement
2. You want different "perspectives" (writer vs editor mindset)
3. Quality standards require critique and revision

It's less valuable for simple, one-shot content generation.
"""
from typing import Dict, Any, List, Optional
from agents.base_agent import BaseAgent

class EditorAgent(BaseAgent):
    """
    Agent specialized in reviewing and refining content.

    Responsibilities:
    - Review content for quality, clarity, and engagement
    - Check grammar, style, and tone consistency
    - Ensure SEO optimization
    - Verify platform-specific requirements are met
    - Suggest improvements and refinements

    This agent provides a "second pair of eyes" and editorial perspective
    that can catch issues and improve content quality through iteration.
    """

    def __init__(self, llm_provider: str = "claude"):
        """
        Initialize Editor Agent.

        Args:
            llm_provider: LLM provider (default: claude for quality editing)
        """
        super().__init__(
            name="Editor",
            role="Content quality and editing specialist",
            llm_provider=llm_provider
        )

    def _default_instructions(self) -> str:
        return """You are an expert content editor with a critical eye for quality.

Your role:
1. Review content objectively for strengths and weaknesses
2. Check grammar, punctuation, and style
3. Ensure clarity, coherence, and flow
4. Verify tone matches target audience and platform
5. Suggest specific, actionable improvements

Editing principles:
- Be constructive but honest
- Focus on substance, not just surface-level fixes
- Consider the reader's perspective
- Ensure every sentence adds value
- Flag anything unclear, wordy, or off-brand

Quality checklist:
✓ Strong hook/opening
✓ Clear structure and flow
✓ Specific examples/data (not generic)
✓ Active voice, concise sentences
✓ Platform-appropriate length and tone
✓ SEO keywords integrated naturally
✓ Compelling CTA/conclusion

Provide both high-level feedback and specific line edits.
"""

    def review_content(
        self,
        content: str,
        platform: str,
        goals: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Review content and provide feedback.

        Args:
            content: Content to review
            platform: Target platform
            goals: Content goals/objectives

        Returns:
            Review with scores, feedback, and suggestions
        """
        goals_str = "\n".join(f"- {goal}" for goal in goals) if goals else "General engagement"

        task = f"""Review this {platform} content:

--- CONTENT ---
{content}
--- END CONTENT ---

Content goals:
{goals_str}

Provide a detailed review covering:

1. Overall Score: Rate 1-10 for quality and platform fit

2. Strengths: What works well (2-3 points)

3. Weaknesses: What needs improvement (2-3 points)

4. Specific Suggestions: Line-by-line improvements

5. SEO Check: Are keywords natural and effective?

6. Platform Fit: Does it meet {platform} best practices?

7. Revised Version: If needed, provide an improved version

Be honest and constructive. Focus on making this content excellent."""

        response = self.run(task)
        content = response.content if hasattr(response, 'content') else str(response)

        return self._parse_review(content)

    def quick_check(self, content: str, platform: str) -> Dict[str, Any]:
        """
        Quick quality check without full review.

        Args:
            content: Content to check
            platform: Target platform

        Returns:
            Quick assessment with pass/fail on key criteria
        """
        task = f"""Quick quality check for {platform} content:

{content}

Check these criteria (Yes/No for each):
1. Appropriate length for {platform}
2. Strong opening hook
3. Clear value proposition
4. No grammar/spelling errors
5. Platform-appropriate tone
6. Includes call-to-action
7. Overall: Ready to publish?

Also note any critical issues that MUST be fixed.

Format as a simple checklist."""

        response = self.run(task)
        content = response.content if hasattr(response, 'content') else str(response)

        return {"quick_check": content}

    def suggest_improvements(
        self,
        content: str,
        weakness: str
    ) -> str:
        """
        Suggest specific improvements for identified weaknesses.

        Args:
            content: Original content
            weakness: Specific weakness to address

        Returns:
            Improved version
        """
        task = f"""Improve this content to address: {weakness}

Original content:
{content}

Provide a revised version that specifically fixes this issue.
Maintain the overall structure and message, but enhance the weak point."""

        response = self.run(task)
        return response.content if hasattr(response, 'content') else str(response)

    def compare_versions(
        self,
        original: str,
        revised: str,
        platform: str
    ) -> Dict[str, Any]:
        """
        Compare original vs revised content.

        Args:
            original: Original content
            revised: Revised content
            platform: Target platform

        Returns:
            Comparison analysis
        """
        task = f"""Compare these two versions of {platform} content:

--- VERSION A (Original) ---
{original}

--- VERSION B (Revised) ---
{revised}

Analyze:
1. Which is better overall and why?
2. What improvements were made?
3. Were any strengths lost in revision?
4. Recommendation: Use A, B, or hybrid?

Be objective and specific."""

        response = self.run(task)
        content = response.content if hasattr(response, 'content') else str(response)

        return {"comparison": content}

    def _parse_review(self, review_text: str) -> Dict[str, Any]:
        """
        Parse review text into structured format.

        Args:
            review_text: Raw review text

        Returns:
            Structured review data
        """
        import re

        # Try to extract score
        score_match = re.search(r'score:?\s*(\d+)', review_text, re.IGNORECASE)
        score = int(score_match.group(1)) if score_match else None

        # Try to find pass/fail or approval
        ready = any(phrase in review_text.lower() for phrase in [
            'ready to publish',
            'approved',
            'looks good',
            'excellent quality'
        ])

        return {
            "score": score,
            "ready_to_publish": ready,
            "full_review": review_text,
            "has_revisions": "revised version" in review_text.lower()
        }

    def iterative_refinement(
        self,
        content: str,
        platform: str,
        max_iterations: int = 2
    ) -> Dict[str, Any]:
        """
        Perform iterative refinement until content meets quality standards.

        Args:
            content: Original content
            platform: Target platform
            max_iterations: Maximum refinement rounds

        Returns:
            Final content with improvement history
        """
        history = []
        current = content

        for i in range(max_iterations):
            self.logger.info(f"Refinement iteration {i+1}/{max_iterations}")

            review = self.review_content(current, platform)
            history.append({
                "iteration": i + 1,
                "review": review,
                "content": current
            })

            # If score is good enough or ready to publish, stop
            if review.get("score", 0) >= 8 or review.get("ready_to_publish"):
                self.logger.info(f"Content approved after {i+1} iterations")
                break

            # Extract revised version if present
            review_text = review["full_review"]
            if "revised version" in review_text.lower():
                # Try to extract the revised content
                parts = review_text.lower().split("revised version")
                if len(parts) > 1:
                    current = parts[1].strip()

        return {
            "final_content": current,
            "iterations": len(history),
            "history": history,
            "final_score": history[-1]["review"].get("score") if history else None
        }
