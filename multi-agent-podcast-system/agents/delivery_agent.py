"""
Delivery Agent (Simplified)

Decides when and how to deliver content.
"""

from .base_agent import BaseAgent
from core.message_protocol import AgentMessage, AgentResponse
from tools.scheduling_tools import predict_best_delivery_time, batch_content_optimally
from typing import Dict, List


class DeliveryAgent(BaseAgent):
    """
    Schedules content delivery.

    Simplified: Batches by urgency.
    """

    def __init__(self, api_key: str, shared_state, verify_ssl: bool = False):
        super().__init__(api_key, shared_state, agent_name="delivery", verify_ssl=verify_ssl)

    def _define_tools(self) -> List[Dict]:
        """Define delivery tools."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "find_best_time",
                    "description": "Find optimal delivery time based on user patterns",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_history": {"type": "array"}
                        },
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "batch_summaries",
                    "description": "Group summaries by urgency",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "summaries": {"type": "array"}
                        },
                        "required": ["summaries"]
                    }
                }
            }
        ]

    def _execute_tool(self, tool_name: str, tool_args: Dict) -> Dict:
        """Execute delivery tools."""
        if tool_name == "find_best_time":
            history = tool_args.get("user_history", [])
            return predict_best_delivery_time(history)

        elif tool_name == "batch_summaries":
            summaries = tool_args.get("summaries", [])
            return batch_content_optimally(summaries)

        return {"success": False, "error": f"Unknown tool: {tool_name}"}

    def execute(self, message: AgentMessage) -> AgentResponse:
        """
        Schedule delivery.

        Args:
            message: Contains summaries to deliver

        Returns:
            AgentResponse with delivery plan
        """
        user_id = message.context.get("user_id")
        summaries = message.input_data.get("summaries", [])

        goal = f"Create delivery plan for {len(summaries)} summaries"

        result = self._run_agentic_loop(
            user_id=user_id,
            goal=goal,
            max_iterations=2
        )

        return message.create_response(
            from_agent=self.agent_name,
            output_data=result
        )
