"""
Twitter/X Platform Agent

✅ REAL MULTI-AGENT VALUE
Why: Twitter has unique requirements (280 char limit, threading logic) and
its own API. This agent handles Twitter-specific formatting and posting.
"""
from typing import Dict, Any, List, Optional
from agents.base_agent import BaseAgent
from tools.social_tools import post_to_twitter, post_twitter_thread

class TwitterAgent(BaseAgent):
    """
    Agent specialized in Twitter/X content formatting and posting.

    Responsibilities:
    - Format content for Twitter (280 char limit)
    - Split long content into threads
    - Add appropriate hashtags and mentions
    - Post via Twitter API
    - Handle Twitter-specific best practices
    """

    def __init__(self, llm_provider: str = "gemini"):
        """
        Initialize Twitter Agent.

        Args:
            llm_provider: LLM provider (gemini for speed/cost)
        """
        super().__init__(
            name="Twitter_Publisher",
            role="Twitter content specialist",
            llm_provider=llm_provider,
            tools=[post_to_twitter, post_twitter_thread]
        )

    def _default_instructions(self) -> str:
        return """You are a Twitter/X content specialist.

Your responsibilities:
1. Format content to fit Twitter's 280 character limit
2. Create engaging threads when content is longer
3. Optimize for Twitter engagement (hooks, questions, CTAs)
4. Add strategic hashtags (2-3 max)
5. Post content via Twitter API

Twitter best practices:
- Hook readers in first 30 characters
- Use line breaks for readability
- Ask questions to drive engagement
- Include relevant hashtags (but not too many)
- End threads with a CTA
- Each tweet should work standalone but flow together

Thread structure:
- Tweet 1: Hook/attention grabber
- Middle tweets: One key point per tweet
- Final tweet: Summary + CTA + hashtags

Always optimize for Twitter's unique culture and format.
"""

    def format_and_post(
        self,
        content: str,
        hashtags: Optional[List[str]] = None,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Format content for Twitter and post it.

        Args:
            content: Content to post
            hashtags: Optional hashtags to include
            dry_run: If True, format but don't actually post

        Returns:
            Formatted content and posting result
        """
        # Check if content needs to be a thread
        if len(content) <= 280:
            # Single tweet
            tweets = [self._add_hashtags(content, hashtags)]
        else:
            # Need to create a thread
            tweets = self._create_thread(content, hashtags)

        result = {
            "format": "thread" if len(tweets) > 1 else "single",
            "tweet_count": len(tweets),
            "tweets": tweets
        }

        # Post if not dry run
        if not dry_run:
            if len(tweets) == 1:
                post_result = post_to_twitter(tweets[0])
            else:
                post_result = post_twitter_thread(tweets)

            result["post_result"] = post_result

        return result

    def _create_thread(
        self,
        content: str,
        hashtags: Optional[List[str]] = None
    ) -> List[str]:
        """
        Split content into a thread of tweets.

        Args:
            content: Long-form content
            hashtags: Optional hashtags

        Returns:
            List of tweets
        """
        task = f"""Convert this content into a Twitter thread:

{content}

Requirements:
- Each tweet MAX 280 characters
- 5-8 tweets total (adjust based on content)
- Tweet 1: Compelling hook
- Middle tweets: Key points (one per tweet)
- Final tweet: Summary + CTA

Return ONLY the tweets, one per line, numbered.
Do NOT include hashtags yet (we'll add them)."""

        response = self.run(task)
        thread_text = response.content if hasattr(response, 'content') else str(response)

        # Parse tweets
        tweets = []
        for line in thread_text.split('\n'):
            line = line.strip()
            if line and (line[0].isdigit() or 'tweet' in line.lower()):
                # Remove numbering
                import re
                cleaned = re.sub(r'^(\d+[.)]\s*|Tweet\s*\d+:?\s*)', '', line, flags=re.IGNORECASE)
                if cleaned and len(cleaned) <= 280:
                    tweets.append(cleaned)

        # Add hashtags to final tweet
        if tweets and hashtags:
            final = tweets[-1]
            hashtag_str = " ".join(hashtags[:3])  # Max 3 hashtags
            if len(final) + len(hashtag_str) + 1 <= 280:
                tweets[-1] = f"{final}\n\n{hashtag_str}"

        return tweets

    def _add_hashtags(self, text: str, hashtags: Optional[List[str]]) -> str:
        """
        Add hashtags to a tweet if they fit.

        Args:
            text: Tweet text
            hashtags: Hashtags to add

        Returns:
            Tweet with hashtags if they fit
        """
        if not hashtags:
            return text

        hashtag_str = " ".join(hashtags[:3])  # Max 3 hashtags
        combined = f"{text}\n\n{hashtag_str}"

        if len(combined) <= 280:
            return combined
        else:
            return text  # Return without hashtags if they don't fit

    def optimize_for_twitter(self, content: str) -> str:
        """
        Optimize content specifically for Twitter engagement.

        Args:
            content: Original content

        Returns:
            Twitter-optimized version
        """
        task = f"""Optimize this content for Twitter:

{content}

Make it:
- More punchy and concise
- Start with a strong hook
- Use Twitter's casual, direct tone
- Break into short, scannable lines
- End with an engaging question or CTA

Stay under 280 characters.
Return ONLY the optimized tweet."""

        response = self.run(task)
        return response.content if hasattr(response, 'content') else str(response)

    def preview_thread(self, content: str, hashtags: Optional[List[str]] = None) -> str:
        """
        Create a visual preview of how the thread will look.

        Args:
            content: Content for thread
            hashtags: Optional hashtags

        Returns:
            Formatted preview string
        """
        tweets = self._create_thread(content, hashtags)

        preview = "=" * 50 + "\n"
        preview += f"TWITTER THREAD PREVIEW ({len(tweets)} tweets)\n"
        preview += "=" * 50 + "\n\n"

        for i, tweet in enumerate(tweets, 1):
            preview += f"Tweet {i}/{len(tweets)}\n"
            preview += "-" * 50 + "\n"
            preview += tweet + "\n"
            preview += f"({len(tweet)} characters)\n\n"

        return preview
