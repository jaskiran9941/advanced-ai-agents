"""
Curator Agent (Simplified)

Decides what content to summarize based on relevance.
"""

from .base_agent import BaseAgent
from core.message_protocol import AgentMessage, AgentResponse
from tools.analysis_tools import analyze_episode_relevance, detect_novelty
from typing import Dict, List


class ContentCuratorAgent(BaseAgent):
    """
    Curates content by filtering for relevance and novelty.

    Simplified: Basic relevance scoring.
    """

    def __init__(self, api_key: str, shared_state, verify_ssl: bool = False):
        super().__init__(api_key, shared_state, agent_name="curator", verify_ssl=verify_ssl)

    def _define_tools(self) -> List[Dict]:
        """Define curation tools."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "analyze_relevance",
                    "description": "Check if episode matches user interests",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "episode_title": {"type": "string"},
                            "episode_description": {"type": "string"},
                            "user_interests": {
                                "type": "array",
                                "items": {"type": "string"}
                            }
                        },
                        "required": ["episode_title", "user_interests"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "check_novelty",
                    "description": "Check if content is novel vs. user history",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "episode": {"type": "object"},
                            "user_history": {"type": "array"}
                        },
                        "required": ["episode"]
                    }
                }
            }
        ]

    def _execute_tool(self, tool_name: str, tool_args: Dict) -> Dict:
        """Execute curation tools."""
        if tool_name == "analyze_relevance":
            return analyze_episode_relevance(
                episode_title=tool_args.get("episode_title", ""),
                episode_description=tool_args.get("episode_description", ""),
                user_interests=tool_args.get("user_interests", [])
            )

        elif tool_name == "check_novelty":
            episode = tool_args.get("episode", {})
            history = tool_args.get("user_history", [])
            return detect_novelty(episode, history)

        return {"success": False, "error": f"Unknown tool: {tool_name}"}

    def execute(self, message: AgentMessage) -> AgentResponse:
        """
        Curate episodes.

        Args:
            message: Contains episodes to analyze

        Returns:
            AgentResponse with curated episode list
        """
        user_id = message.context.get("user_id")
        episodes = message.input_data.get("episodes", [])

        # Get user context for filtering
        user_context = self.shared_state.get_user_context(user_id)
        interests = user_context["preferences"].get("recent_topics", [])

        goal = f"Analyze {len(episodes)} episodes and filter for relevance to user interests: {interests}"

        result = self._run_agentic_loop(
            user_id=user_id,
            goal=goal,
            max_iterations=3
        )

        return message.create_response(
            from_agent=self.agent_name,
            output_data=result
        )
