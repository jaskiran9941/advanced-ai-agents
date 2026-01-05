"""
Personalization Agent (Simplified)

Adapts summaries to user preferences and context.
"""

from .base_agent import BaseAgent
from core.message_protocol import AgentMessage, AgentResponse
from tools.summarization_tools import generate_summary, adapt_summary_depth
from typing import Dict, List


class PersonalizationAgent(BaseAgent):
    """
    Personalizes content presentation.

    Simplified: Adapts summary style based on user preferences.
    """

    def __init__(self, api_key: str, shared_state, verify_ssl: bool = False):
        super().__init__(api_key, shared_state, agent_name="personalization", verify_ssl=verify_ssl)

    def _define_tools(self) -> List[Dict]:
        """Define personalization tools."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "create_summary",
                    "description": "Generate summary with chosen style",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "episode_title": {"type": "string"},
                            "episode_description": {"type": "string"},
                            "style": {
                                "type": "string",
                                "enum": ["brief", "detailed", "technical"],
                                "description": "Summary style"
                            }
                        },
                        "required": ["episode_title", "episode_description", "style"]
                    }
                }
            }
        ]

    def _execute_tool(self, tool_name: str, tool_args: Dict) -> Dict:
        """Execute personalization tools."""
        if tool_name == "create_summary":
            return generate_summary(
                client=self.client,
                episode_title=tool_args.get("episode_title", ""),
                episode_description=tool_args.get("episode_description", ""),
                style=tool_args.get("style", "detailed")
            )

        return {"success": False, "error": f"Unknown tool: {tool_name}"}

    def execute(self, message: AgentMessage) -> AgentResponse:
        """
        Personalize content.

        Args:
            message: Contains episode to summarize

        Returns:
            AgentResponse with personalized summary
        """
        user_id = message.context.get("user_id")
        episode = message.input_data.get("episode", {})

        # Get user preferences
        user_context = self.shared_state.get_user_context(user_id)
        preferred_style = user_context["preferences"].get("preferred_length", "detailed")

        goal = f"Generate a {preferred_style} summary for: {episode.get('title', 'episode')}"

        result = self._run_agentic_loop(
            user_id=user_id,
            goal=goal,
            max_iterations=2
        )

        return message.create_response(
            from_agent=self.agent_name,
            output_data=result
        )
