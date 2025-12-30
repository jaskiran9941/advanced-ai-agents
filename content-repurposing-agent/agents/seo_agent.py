"""
SEO Research Agent

✅ REAL MULTI-AGENT VALUE
Why: LLMs don't have real-time SEO data, keyword trends, or search volumes.
This agent calls SerpAPI to get actual trending keywords and search data.
"""
from typing import Dict, Any
import json
from agents.base_agent import BaseAgent
from tools.seo_tools import search_trending_keywords, get_related_queries, analyze_keyword_difficulty

class SEOResearchAgent(BaseAgent):
    """
    Agent specialized in SEO research and keyword analysis.

    Responsibilities:
    - Find trending keywords related to content topic
    - Analyze search volumes and competition
    - Suggest SEO-optimized terms for content
    - Provide related queries for content ideas
    """

    def __init__(self, llm_provider: str = "gemini"):
        """
        Initialize SEO Research Agent.

        Args:
            llm_provider: LLM provider (default: gemini for cost efficiency)
        """
        super().__init__(
            name="SEO_Researcher",
            role="SEO and keyword research specialist",
            llm_provider=llm_provider,
            tools=[
                search_trending_keywords,
                get_related_queries,
                analyze_keyword_difficulty
            ]
        )

    def _default_instructions(self) -> str:
        return """You are an SEO research specialist.

Your job is to:
1. Research trending keywords related to the given topic
2. Find related search queries people are actually searching for
3. Analyze keyword difficulty and competition
4. Provide actionable SEO recommendations for content optimization

When given a topic:
- Use search_trending_keywords() to find what's trending
- Use get_related_queries() to discover related searches
- Use analyze_keyword_difficulty() to assess competition
- Synthesize findings into clear recommendations

Output format:
{
    "primary_keywords": ["keyword1", "keyword2", ...],
    "long_tail_keywords": ["longer phrase 1", "longer phrase 2", ...],
    "trending_topics": ["trend1", "trend2", ...],
    "seo_recommendations": "Brief recommendations for optimizing content",
    "hashtags": ["#hashtag1", "#hashtag2", ...]
}

Be concise and actionable. Focus on keywords that will help content rank and get discovered.
"""

    def research_topic(self, topic: str) -> Dict[str, Any]:
        """
        Conduct comprehensive SEO research on a topic.

        Args:
            topic: Content topic to research

        Returns:
            SEO research results with keywords and recommendations
        """
        task = f"""Research SEO keywords and trends for this topic: "{topic}"

Use all available tools to:
1. Find trending keywords
2. Discover related queries
3. Analyze keyword difficulty
4. Provide optimization recommendations

Return structured JSON with findings."""

        response = self.run(task)

        # Parse response into structured format
        # Agno returns response.content
        return self._parse_seo_response(response)

    def _parse_seo_response(self, response) -> Dict[str, Any]:
        """
        Parse agent response into structured SEO data.

        Args:
            response: Agent response object

        Returns:
            Structured SEO research data
        """
        # Extract content from Agno response
        if hasattr(response, 'content'):
            content = response.content
        else:
            content = str(response)

        # Try to parse as JSON, fallback to structured parsing
        import json
        try:
            # Look for JSON in the response
            start = content.find('{')
            end = content.rfind('}') + 1
            if start != -1 and end != 0:
                json_str = content[start:end]
                return json.loads(json_str)
        except:
            pass

        # Fallback: return basic structure
        self.logger.warning("Could not parse SEO response as JSON, using fallback")
        return {
            "primary_keywords": [],
            "long_tail_keywords": [],
            "trending_topics": [],
            "seo_recommendations": content[:500],
            "hashtags": []
        }

    def _get_mock_response(self, task: str) -> str:
        """
        Generate mock SEO response when API is unavailable.
        """
        # Extract topic from task if possible
        topic = "AI and Climate Change"
        if '"' in task:
            parts = task.split('"')
            if len(parts) > 1:
                topic = parts[1]

        mock_data = {
            "primary_keywords": [
                "AI climate solutions",
                "machine learning climate change",
                "artificial intelligence sustainability",
                "AI environmental technology"
            ],
            "long_tail_keywords": [
                "how AI helps fight climate change",
                "best AI solutions for environmental problems",
                "machine learning climate modeling",
                "AI powered renewable energy optimization"
            ],
            "trending_topics": [
                "AI carbon capture",
                "climate tech innovation",
                "green AI technology",
                "sustainable machine learning"
            ],
            "seo_recommendations": f"Focus on keywords combining AI and climate action. Target long-tail phrases for specific solutions. Include case studies and real-world applications. Optimize for 'how AI helps' queries which have high search intent.",
            "hashtags": [
                "#AIforClimate",
                "#ClimateAction",
                "#GreenTech",
                "#SustainableAI",
                "#ClimateTech",
                "#AIInnovation"
            ]
        }

        # Create a mock response object that mimics the real response
        class MockResponse:
            def __init__(self, content):
                self.content = json.dumps(mock_data, indent=2)

        return MockResponse(json.dumps(mock_data))

    def suggest_hashtags(self, topic: str, count: int = 10) -> list:
        """
        Suggest relevant hashtags for social media.

        Args:
            topic: Content topic
            count: Number of hashtags to suggest

        Returns:
            List of hashtags
        """
        task = f"""Suggest {count} relevant hashtags for social media posts about: "{topic}"

Make them:
- Relevant and specific
- Mix of popular and niche
- Platform-appropriate (works for Instagram, Twitter, LinkedIn)

Return as a simple list."""

        response = self.run(task)
        content = response.content if hasattr(response, 'content') else str(response)

        # Extract hashtags from response
        hashtags = []
        for line in content.split('\n'):
            if '#' in line:
                tags = [word for word in line.split() if word.startswith('#')]
                hashtags.extend(tags)

        return hashtags[:count]
