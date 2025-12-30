"""
Content Writer Agent

⚠️ EDUCATIONAL SEPARATION
Why it's "fake": A single LLM prompt could generate all platform-specific content.
Why we separate it: To learn agent specialization patterns and demonstrate
how to structure multi-agent systems even when not strictly necessary.

HONEST ASSESSMENT: This agent doesn't add technical value over a single LLM call.
It's here for educational purposes to show how to structure specialized agents.
"""
from typing import Dict, Any, Optional, List
from agents.base_agent import BaseAgent

class ContentWriterAgent(BaseAgent):
    """
    Agent specialized in creating long-form content.

    Responsibilities:
    - Generate comprehensive content on given topics
    - Create platform-specific variations (but could be done in one call)
    - Incorporate SEO keywords
    - Match brand voice and tone

    TRANSPARENCY NOTE: This agent is separated for educational purposes.
    In a production system optimized for cost/speed, you could use a single
    LLM call to generate all content variations at once.
    """

    def __init__(self, llm_provider: str = "claude"):
        """
        Initialize Content Writer Agent.

        Args:
            llm_provider: LLM provider (default: claude for quality writing)
        """
        super().__init__(
            name="Content_Writer",
            role="Content creation specialist",
            llm_provider=llm_provider
        )

    def _get_mock_response(self, task: str) -> str:
        """
        Generate mock content response when API is unavailable.
        """
        # Determine platform type from task
        if "LinkedIn" in task:
            content = """🚀 The Future of AI in Climate Change Solutions

Climate change is one of humanity's greatest challenges, but AI is emerging as a powerful ally in our fight for a sustainable future.

Here's how AI is making a difference:

🌍 Predictive Climate Modeling: Machine learning algorithms analyze vast datasets to create more accurate climate predictions, helping us prepare for and mitigate extreme weather events.

⚡ Energy Optimization: AI-powered systems optimize renewable energy grids, reducing waste and maximizing efficiency across solar and wind installations.

🌱 Smart Agriculture: Precision farming powered by AI reduces water usage, optimizes crop yields, and minimizes environmental impact.

♻️ Carbon Capture: AI accelerates the development of carbon capture technologies by rapidly testing molecular combinations and optimizing processes.

The potential is enormous, but we need collaboration between tech companies, researchers, policymakers, and environmental organizations to make it a reality.

What role do you think AI should play in addressing climate change? Let's discuss in the comments.

#ClimateAction #AIforGood #Sustainability #GreenTech"""
        elif "Twitter" in task or "tweet" in task.lower():
            content = """[
"🌍 AI is revolutionizing how we fight climate change. From optimizing renewable energy grids to predicting extreme weather events, machine learning is becoming our most powerful tool for planetary protection. Here's what you need to know 🧵",
"1/ CLIMATE MODELING: AI analyzes petabytes of climate data to create predictions that are 40% more accurate than traditional models. This means better preparation for extreme weather and more effective policy planning.",
"2/ ENERGY OPTIMIZATION: Smart grids powered by AI reduce renewable energy waste by up to 30%. They predict demand, optimize storage, and ensure every watt of solar and wind power is used efficiently.",
"3/ CARBON CAPTURE: AI is accelerating carbon capture tech development by 10x. Machine learning tests millions of molecular combinations in silico, finding solutions that would take humans decades to discover.",
"4/ The intersection of AI and climate science represents our best shot at a sustainable future. But technology alone isn't enough—we need policy, investment, and collective action. What climate tech innovations excite you most? 🌱 #ClimateAction #AIforClimate"
]"""
        elif "Instagram" in task:
            content = """🌍 Can AI Save Our Planet?

Climate change is real, and the clock is ticking. But here's some hope: artificial intelligence is emerging as a game-changer in our fight for a sustainable future.

AI is helping us:
✨ Predict climate patterns with unprecedented accuracy
⚡ Optimize clean energy systems to reduce waste
🌱 Revolutionize sustainable agriculture
♻️ Accelerate carbon capture technology

The future is being written right now, and technology is giving us tools we've never had before. But AI alone won't save us—it takes all of us working together.

Swipe to learn more about how AI is tackling climate change →

#ClimateAction #AIforGood #Sustainability #GreenTech #ClimateChange #Innovation #FutureOfEarth #SustainableLiving #TechForGood"""
        else:
            # Default long-form content
            content = """The Future of AI in Climate Change Solutions: A New Hope for Planetary Protection

Introduction

As climate change accelerates and its impacts become increasingly severe, humanity is turning to one of its most powerful tools: artificial intelligence. The convergence of AI technology and climate science represents not just a technological advancement, but potentially our best opportunity to address one of civilization's greatest challenges.

How AI is Transforming Climate Action

1. Revolutionizing Climate Modeling and Prediction

Traditional climate models, while sophisticated, struggle with the sheer complexity of Earth's interconnected systems. AI-powered models can analyze petabytes of data from satellites, ocean buoys, weather stations, and historical records to identify patterns that humans might miss. Machine learning algorithms have improved prediction accuracy by up to 40%, giving policymakers and communities better tools to prepare for extreme weather events.

2. Optimizing Renewable Energy Systems

One of the biggest challenges with renewable energy is intermittency—the sun doesn't always shine and the wind doesn't always blow. AI addresses this through:

- Predictive analytics that forecast energy generation 48-72 hours in advance
- Smart grid management that balances supply and demand in real-time
- Energy storage optimization that reduces waste by 25-30%
- Automated maintenance systems that prevent failures before they occur

3. Accelerating Carbon Capture Technology

Perhaps one of the most exciting applications is AI's role in developing carbon capture solutions. Machine learning can:

- Test millions of molecular combinations virtually
- Identify promising materials for CO2 absorption
- Optimize capture processes for maximum efficiency
- Reduce development time from decades to years

4. Transforming Agriculture for Sustainability

Agriculture is both a victim of climate change and a significant contributor to greenhouse gas emissions. AI-powered precision farming is changing this equation:

- Satellite imagery and drone data optimize water usage
- Predictive models reduce fertilizer waste
- Automated systems minimize pesticide use
- Crop yield forecasting improves food security

The Challenges Ahead

While the potential is enormous, we must acknowledge the challenges:

- AI systems themselves consume significant energy
- Data quality and availability vary globally
- Implementation requires substantial investment
- Ethical considerations around automated climate decisions

Conclusion

AI is not a silver bullet for climate change, but it is a powerful tool in our arsenal. The technology gives us unprecedented ability to understand, predict, and respond to climate challenges. However, technology alone won't save us—it must be coupled with policy changes, international cooperation, and collective action.

The question isn't whether AI can help fight climate change—it's whether we'll deploy it fast enough and wisely enough to make a difference while there's still time."""

        # Create mock response object
        class MockResponse:
            def __init__(self, content):
                self.content = content

        return MockResponse(content)

    def _default_instructions(self) -> str:
        return """You are an expert content writer specializing in creating engaging,
informative content optimized for different platforms.

Your responsibilities:
1. Research and understand the topic deeply
2. Create well-structured, engaging content
3. Incorporate SEO keywords naturally
4. Adapt tone and style for target audience
5. Ensure accuracy and credibility

Writing principles:
- Hook readers in the first sentence
- Use clear, concise language
- Break up text with short paragraphs
- Include specific examples and data when possible
- End with actionable takeaways

Platform-specific adaptations:
- Substack: Long-form, newsletter style, personal voice
- LinkedIn: Professional, value-driven, thought leadership
- Twitter: Concise, punchy, conversation-starting
- Instagram: Visual-focused, casual, lifestyle-oriented

Always produce high-quality, original content that provides genuine value.
"""

    def write_long_form(
        self,
        topic: str,
        keywords: Optional[List[str]] = None,
        tone: str = "professional",
        min_words: int = 800
    ) -> str:
        """
        Generate long-form content (for Substack/blog).

        Args:
            topic: Content topic
            keywords: SEO keywords to incorporate
            tone: Writing tone
            min_words: Minimum word count

        Returns:
            Long-form content
        """
        keyword_str = ", ".join(keywords) if keywords else "none specified"

        task = f"""Write a comprehensive, engaging article about: {topic}

Requirements:
- Minimum {min_words} words
- Tone: {tone}
- Incorporate these SEO keywords naturally: {keyword_str}
- Include:
  * Compelling headline
  * Strong opening hook
  * Clear sections with subheadings
  * Specific examples or data
  * Actionable conclusion

Write in a narrative, engaging style suitable for Substack or a blog.
Focus on providing genuine value and insight."""

        response = self.run(task)
        return response.content if hasattr(response, 'content') else str(response)

    def write_linkedin_post(
        self,
        topic: str,
        keywords: Optional[List[str]] = None,
        hook: Optional[str] = None
    ) -> str:
        """
        Generate LinkedIn-optimized content.

        Args:
            topic: Content topic
            keywords: SEO keywords
            hook: Optional opening hook

        Returns:
            LinkedIn post content
        """
        keyword_str = ", ".join(keywords) if keywords else "none specified"
        hook_str = f"\nOpening hook: {hook}" if hook else ""

        task = f"""Write a professional LinkedIn post about: {topic}

Requirements:
- 200-300 words (LinkedIn sweet spot)
- Professional, thought-leadership tone
- Keywords: {keyword_str}{hook_str}
- Structure:
  * Strong opening statement/question
  * 2-3 key insights or takeaways
  * Call to action or discussion prompt
- Use short paragraphs (1-2 sentences each)
- Include 3-5 relevant hashtags at the end

Make it engaging and conversation-starting. Focus on professional value."""

        response = self.run(task)
        return response.content if hasattr(response, 'content') else str(response)

    def write_twitter_thread(
        self,
        topic: str,
        keywords: Optional[List[str]] = None,
        num_tweets: int = 5
    ) -> List[str]:
        """
        Generate Twitter thread.

        Args:
            topic: Content topic
            keywords: SEO keywords
            num_tweets: Number of tweets in thread

        Returns:
            List of tweets
        """
        keyword_str = ", ".join(keywords) if keywords else "none specified"

        task = f"""Write a {num_tweets}-tweet thread about: {topic}

Requirements:
- Each tweet max 280 characters
- Keywords to weave in: {keyword_str}
- Structure:
  * Tweet 1: Hook/attention-grabber
  * Tweets 2-{num_tweets-1}: Key points (one per tweet)
  * Tweet {num_tweets}: Summary + CTA
- Use clear, punchy language
- Make each tweet self-contained but part of coherent narrative
- Include 2-3 relevant hashtags in final tweet

Format: Return each tweet on a new line, numbered."""

        response = self.run(task)
        content = response.content if hasattr(response, 'content') else str(response)

        # Parse into individual tweets
        tweets = []
        for line in content.split('\n'):
            line = line.strip()
            # Remove numbering (1., 2., etc.)
            if line and (line[0].isdigit() or line.startswith('Tweet')):
                # Remove number/label and any following punctuation
                import re
                cleaned = re.sub(r'^(\d+\.|Tweet\s*\d+:?)\s*', '', line)
                if cleaned:
                    tweets.append(cleaned)

        return tweets[:num_tweets]

    def write_instagram_caption(
        self,
        topic: str,
        keywords: Optional[List[str]] = None,
        hashtags: Optional[List[str]] = None
    ) -> str:
        """
        Generate Instagram caption.

        Args:
            topic: Content topic
            keywords: SEO keywords
            hashtags: Suggested hashtags

        Returns:
            Instagram caption
        """
        keyword_str = ", ".join(keywords) if keywords else "none specified"
        hashtag_str = " ".join(hashtags) if hashtags else ""

        task = f"""Write an Instagram caption about: {topic}

Requirements:
- 150-200 words (sweet spot for engagement)
- Casual, relatable, lifestyle-oriented tone
- Keywords: {keyword_str}
- Structure:
  * Opening hook/question
  * 2-3 short paragraphs with value
  * Call to action (like, save, share, comment)
- Use emojis sparingly and naturally
- Include hashtags at end: {hashtag_str if hashtag_str else "generate 10 relevant hashtags"}

Make it feel authentic and encourage engagement."""

        response = self.run(task)
        return response.content if hasattr(response, 'content') else str(response)

    def write_all_platforms(
        self,
        topic: str,
        keywords: Optional[List[str]] = None,
        hashtags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generate content for all platforms at once.

        NOTE: This method demonstrates that we COULD do all content generation
        in a single agent call. The separation into different agents is educational.

        Args:
            topic: Content topic
            keywords: SEO keywords
            hashtags: Suggested hashtags

        Returns:
            Dictionary with content for each platform
        """
        self.logger.info(f"Generating content for all platforms: {topic}")

        return {
            "substack": self.write_long_form(topic, keywords),
            "linkedin": self.write_linkedin_post(topic, keywords),
            "twitter": self.write_twitter_thread(topic, keywords),
            "instagram": self.write_instagram_caption(topic, keywords, hashtags)
        }
