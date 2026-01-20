"""
Tavily Search Tool

Provides web search capabilities using the Tavily API for real-time market research,
competitor analysis, and trend discovery.
"""

import os
from typing import Dict, Any, List, Optional
from tavily import TavilyClient


class TavilySearch:
    """
    Web search tool using Tavily API

    Features:
    - Advanced search depth for comprehensive results
    - Structured result format with summaries
    - Source attribution for citations
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Tavily search client

        Args:
            api_key: Tavily API key (defaults to TAVILY_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("TAVILY_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Tavily API key not found. Set TAVILY_API_KEY environment variable "
                "or pass api_key parameter. Get your key at https://tavily.com/"
            )

        self.client = TavilyClient(api_key=self.api_key)

    def search(
        self,
        query: str,
        max_results: int = 5,
        search_depth: str = "advanced",
        include_answer: bool = True,
        include_raw_content: bool = False,
        include_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Search the web using Tavily API

        Args:
            query: Search query string
            max_results: Maximum number of results to return (default: 5)
            search_depth: "basic" or "advanced" (default: "advanced")
            include_answer: Include AI-generated answer summary (default: True)
            include_raw_content: Include full page content (default: False)
            include_domains: Only search within these domains
            exclude_domains: Exclude these domains from results

        Returns:
            Dictionary containing:
                - query: The original search query
                - answer: AI-generated summary (if include_answer=True)
                - results: List of search results with title, content, url, score
                - response_time: Time taken for the search
        """
        try:
            response = self.client.search(
                query=query,
                search_depth=search_depth,
                max_results=max_results,
                include_answer=include_answer,
                include_raw_content=include_raw_content,
                include_domains=include_domains,
                exclude_domains=exclude_domains
            )

            return response

        except Exception as e:
            # Return error in structured format
            return {
                "query": query,
                "error": str(e),
                "results": [],
                "answer": f"Search failed: {str(e)}"
            }

    def multi_search(self, queries: List[str], max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Execute multiple searches in sequence

        Args:
            queries: List of search query strings
            max_results: Maximum results per query

        Returns:
            List of search result dictionaries
        """
        results = []
        for query in queries:
            result = self.search(query, max_results=max_results)
            results.append(result)

        return results

    def format_results_for_llm(self, search_results: Dict[str, Any], max_content_length: int = 200) -> str:
        """
        Format search results into a clean text format for LLM consumption

        Args:
            search_results: Raw Tavily search results
            max_content_length: Maximum length of content snippets

        Returns:
            Formatted string suitable for LLM context
        """
        formatted = []

        # Add query
        formatted.append(f"## Search Query: {search_results.get('query', 'N/A')}")
        formatted.append("")

        # Add AI-generated answer if available
        if "answer" in search_results and search_results["answer"]:
            formatted.append("### Summary Answer:")
            formatted.append(search_results["answer"])
            formatted.append("")

        # Add individual results
        if "results" in search_results:
            formatted.append("### Search Results:")
            for i, result in enumerate(search_results["results"], 1):
                formatted.append(f"\n{i}. **{result.get('title', 'N/A')}**")

                content = result.get('content', '')
                if len(content) > max_content_length:
                    content = content[:max_content_length] + "..."
                formatted.append(f"   {content}")

                formatted.append(f"   Source: {result.get('url', 'N/A')}")

                if 'score' in result:
                    formatted.append(f"   Relevance: {result['score']:.2f}")

        # Add error if present
        if "error" in search_results:
            formatted.append(f"\n⚠️ Error: {search_results['error']}")

        return "\n".join(formatted)
