"""
Research Agent - conducts market research using Claude Sonnet + Tavily Web Search

AGENTIC FEATURES:
- Real web search via Tavily API
- Iterative query planning and refinement
- Quality validation and self-correction
- Source attribution and transparency
"""
import json
from typing import Dict, Any, List, Tuple
from .base_agent import BaseAgent
from .tools.tavily_search import TavilySearch
from .tools.tool_executor import ToolExecutor


class ResearchAgent(BaseAgent):
    """
    Agentic market research agent with web search capabilities

    Process:
    1. Plan search queries using LLM
    2. Execute searches using Tavily API
    3. Synthesize findings using LLM
    4. Validate completeness
    5. Retry with refined queries if needed
    """

    def __init__(self):
        super().__init__(name="ResearchAgent", provider="anthropic")

        # Initialize web search tool
        self.tavily = TavilySearch()

        # Register tool in executor
        self.tool_executor = ToolExecutor()
        self.tool_executor.register_tool(
            "web_search",
            self.tavily.search,
            description="Search the web for market research data"
        )

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute agentic research with web search

        Args:
            input_data: {
                "concept": str,               # Product description
                "market": str,                # Target market
                "refinement_feedback": List[str],  # (Optional) Improvements from validation
                "previous_attempt": Dict       # (Optional) Previous research output
            }

        Returns:
            {
                "market_size": str,
                "competitors": List[Dict],
                "trends": List[str],
                "pain_points": List[str],
                "opportunities": List[str],
                "sources": List[str],
                "raw_findings": str,
                "search_queries": List[str]  # Queries used
            }
        """
        concept = input_data.get("concept")
        market = input_data.get("market")
        refinement_feedback = input_data.get("refinement_feedback", [])

        self._log(f"🔍 Researching: {concept} in {market} market")

        # Step 1: Plan search queries using LLM
        queries = self._plan_search_queries(concept, market, refinement_feedback)
        self._log(f"📋 Planned {len(queries)} search queries")

        # Step 2: Execute searches using Tavily
        search_results = []
        for query in queries:
            self._log(f"🌐 Searching: {query}")
            result = self.tavily.search(query, max_results=5)
            search_results.append({
                "query": query,
                "results": result
            })

        # Step 3: Synthesize findings from search results
        research_data = self._synthesize_findings(concept, market, search_results)

        # Add query tracking for transparency
        research_data["search_queries"] = queries

        self._log("✅ Research synthesis complete")
        return research_data

    def _plan_search_queries(
        self,
        concept: str,
        market: str,
        refinement_feedback: List[str]
    ) -> List[str]:
        """
        Use LLM to plan optimal search queries

        Args:
            concept: Product concept
            market: Target market
            refinement_feedback: Suggestions from validation (if retrying)

        Returns:
            List of search query strings
        """
        system_prompt = """You are a market research planner. Generate specific, targeted search queries to thoroughly research a product concept.

Focus on:
- Market size and growth data
- Direct and indirect competitors
- Customer pain points and needs
- Industry trends and emerging patterns
- Pricing models and business strategies

Generate 3-5 specific search queries that will yield comprehensive data.

Return ONLY a JSON array of search query strings (no explanation).

Example output:
["AI fitness app market size 2024", "fitness tracking app competitors analysis", "workout app user pain points"]"""

        refinement_context = ""
        if refinement_feedback:
            refinement_context = f"\n\nPrevious search was incomplete. Address these gaps:\n" + "\n".join(f"- {feedback}" for feedback in refinement_feedback)

        user_message = f"""Product: {concept}
Target Market: {market}{refinement_context}

Generate search queries (JSON array):"""

        messages = [{"role": "user", "content": user_message}]

        try:
            response = self._call_llm(
                messages,
                system=system_prompt,
                temperature=0.7
            )

            # Parse JSON array
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            else:
                json_str = response.strip()

            queries = json.loads(json_str)

            # Ensure it's a list
            if not isinstance(queries, list):
                queries = [str(queries)]

            return queries[:5]  # Limit to 5 queries max

        except Exception as e:
            self._log(f"⚠️  Query planning failed, using fallback queries: {e}")
            # Fallback queries
            return [
                f"{concept} market size {market}",
                f"{concept} competitors",
                f"{market} customer pain points"
            ]

    def _synthesize_findings(
        self,
        concept: str,
        market: str,
        search_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Synthesize web search results into structured research

        Args:
            concept: Product concept
            market: Target market
            search_results: List of Tavily search results

        Returns:
            Structured research dictionary
        """
        # Format search results for LLM
        search_context = self._format_search_results(search_results)

        system_prompt = """You are a market analyst. Synthesize web search results into comprehensive, structured market research.

Be specific and data-driven. Cite numbers, names, and facts from the search results.

Format response as JSON with these exact keys:
{
  "market_size": "Specific market size with numbers and sources",
  "competitors": [
    {
      "name": "Company name",
      "description": "What they do",
      "strengths": "Their advantages",
      "weaknesses": "Their limitations"
    }
  ],
  "trends": ["Specific trend 1", "Specific trend 2", ...],
  "pain_points": ["Specific customer pain 1", "Specific customer pain 2", ...],
  "opportunities": ["Specific opportunity 1", "Specific opportunity 2", ...],
  "analysis_notes": "Additional insights and synthesis"
}

Include at least 3 competitors, 3 trends, 5 pain points, and 3 opportunities."""

        user_message = f"""Product: {concept}
Target Market: {market}

Web Search Results:
{search_context}

Synthesize into structured market research (JSON):"""

        messages = [{"role": "user", "content": user_message}]

        try:
            response = self._call_llm(
                messages,
                system=system_prompt,
                temperature=0.5  # Lower temperature for factual synthesis
            )

            # Parse JSON
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            else:
                json_str = response.strip()

            research_data = json.loads(json_str)

            # Add metadata
            research_data["raw_findings"] = response
            research_data["sources"] = [
                result["results"].get("results", [{}])[0].get("url", "N/A")
                for result in search_results
                if result["results"].get("results")
            ]

            return research_data

        except json.JSONDecodeError as e:
            self._log(f"⚠️  JSON parsing failed: {e}")
            return {
                "market_size": "Data not available",
                "competitors": [],
                "trends": [],
                "pain_points": [],
                "opportunities": [],
                "sources": [],
                "raw_findings": response
            }

    def _format_search_results(self, search_results: List[Dict[str, Any]]) -> str:
        """
        Format Tavily search results for LLM consumption

        Args:
            search_results: Raw Tavily results

        Returns:
            Formatted string
        """
        formatted = []

        for item in search_results:
            query = item["query"]
            results = item["results"]

            formatted.append(f"\n## Query: {query}")
            formatted.append("=" * 80)

            # Add AI-generated answer if available
            if "answer" in results and results["answer"]:
                formatted.append(f"\n**Summary Answer:**\n{results['answer']}\n")

            # Add top results
            for i, result in enumerate(results.get("results", [])[:3], 1):
                title = result.get("title", "N/A")
                content = result.get("content", "")[:300]  # Limit content length
                url = result.get("url", "N/A")

                formatted.append(f"\n{i}. **{title}**")
                formatted.append(f"   {content}...")
                formatted.append(f"   Source: {url}")

            formatted.append("")

        return "\n".join(formatted)

    def validate_output(self, output: Dict[str, Any]) -> Tuple[bool, float, List[str]]:
        """
        Validate research completeness and quality

        Checks:
        - Market size specificity
        - Number of competitors
        - Pain points depth
        - Trend identification
        - Data quality

        Args:
            output: Research output to validate

        Returns:
            (is_valid, confidence_score, improvement_suggestions)
        """
        suggestions = []
        score = 1.0

        # Check market size
        market_size = output.get("market_size", "")
        if not market_size or market_size == "Data not available":
            suggestions.append("Find specific market size data with numbers ($XXM, XX% growth, etc.)")
            score -= 0.25
        elif len(market_size) < 50:
            suggestions.append("Expand market size analysis with more detail and sources")
            score -= 0.1

        # Check competitors
        competitors = output.get("competitors", [])
        if len(competitors) < 2:
            suggestions.append("Identify at least 3 key competitors with details")
            score -= 0.2
        elif len(competitors) < 3:
            suggestions.append("Add more competitor analysis (aim for 3-5)")
            score -= 0.1

        # Check competitor quality
        for comp in competitors:
            if not comp.get("strengths") or not comp.get("weaknesses"):
                suggestions.append(f"Add detailed strengths/weaknesses for competitor: {comp.get('name', 'Unknown')}")
                score -= 0.05

        # Check pain points
        pain_points = output.get("pain_points", [])
        if len(pain_points) < 3:
            suggestions.append("Research more customer pain points (at least 5)")
            score -= 0.2
        elif len(pain_points) < 5:
            suggestions.append("Add more pain points for comprehensive coverage")
            score -= 0.1

        # Check trends
        trends = output.get("trends", [])
        if len(trends) < 2:
            suggestions.append("Identify more market trends (at least 3)")
            score -= 0.1

        # Check opportunities
        opportunities = output.get("opportunities", [])
        if len(opportunities) < 2:
            suggestions.append("Identify more market opportunities (at least 3)")
            score -= 0.1

        # Ensure score stays in valid range
        score = max(0.0, min(1.0, score))

        is_valid = score >= self.get_min_confidence()

        return is_valid, score, suggestions

    def get_min_confidence(self) -> float:
        """Minimum acceptable confidence for research quality"""
        from app.config import settings
        return settings.MIN_ICP_CONFIDENCE  # 0.7
