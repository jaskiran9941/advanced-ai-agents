"""
Discovery Agent (Simplified)

Finds podcasts using iTunes API.
"""

from .base_agent import BaseAgent
from core.message_protocol import AgentMessage, AgentResponse
from tools.podcast_tools import search_itunes_api
from typing import Dict, List


class PodcastDiscoveryAgent(BaseAgent):
    """
    Discovers podcasts based on topics.

    Simplified: Just searches iTunes, no complex strategies.
    """

    def __init__(self, api_key: str, shared_state, verify_ssl: bool = False):
        super().__init__(api_key, shared_state, agent_name="discovery", verify_ssl=verify_ssl)

    def _define_tools(self) -> List[Dict]:
        """Define tools for podcast discovery."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "search_podcasts",
                    "description": "Search iTunes for podcasts by topics",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "topics": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Topics to search for"
                            },
                            "limit": {
                                "type": "number",
                                "description": "Max results (default 5)"
                            }
                        },
                        "required": ["topics"]
                    }
                }
            }
        ]

    def _execute_tool(self, tool_name: str, tool_args: Dict) -> Dict:
        """Execute discovery tools."""
        if tool_name == "search_podcasts":
            topics = tool_args.get("topics", [])
            limit = tool_args.get("limit", 5)
            return search_itunes_api(topics, limit)

        return {"success": False, "error": f"Unknown tool: {tool_name}"}

    def execute(self, message: AgentMessage) -> AgentResponse:
        """
        Handle discovery requests.

        Args:
            message: Contains topics to search for

        Returns:
            AgentResponse with podcast recommendations
        """
        user_id = message.context.get("user_id")
        topics = message.input_data.get("search_topics", [])

        goal = f"Search for podcasts about: {', '.join(topics)}"

        result = self._run_agentic_loop(
            user_id=user_id,
            goal=goal,
            max_iterations=3
        )

        return message.create_response(
            from_agent=self.agent_name,
            output_data=result
        )
