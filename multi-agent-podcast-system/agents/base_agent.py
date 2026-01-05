"""
Base Agent (Simplified for Learning)

Abstract base class that all specialized agents inherit from.
"""

from abc import ABC, abstractmethod
from openai import OpenAI
import httpx
from typing import Dict, List
from core.shared_state import SharedStateManager
from core.message_protocol import AgentMessage, AgentResponse
import time


class BaseAgent(ABC):
    """
    Abstract base agent - all specialized agents inherit this.

    Provides:
    - OpenAI client for tool calling
    - Shared state access
    - Standard execute() interface
    - Learning feedback capability
    """

    def __init__(self, api_key: str, shared_state: SharedStateManager, agent_name: str, verify_ssl: bool = False):
        """
        Initialize base agent.

        Args:
            api_key: OpenAI API key
            shared_state: SharedStateManager instance
            agent_name: Name of this agent (e.g., 'discovery', 'curator')
            verify_ssl: Whether to verify SSL certificates (default False for local testing)
        """
        # Create HTTP client with SSL verification option
        http_client = httpx.Client(verify=verify_ssl) if not verify_ssl else None

        self.client = OpenAI(api_key=api_key, http_client=http_client)
        self.shared_state = shared_state
        self.agent_name = agent_name
        self.tools = self._define_tools()

    @abstractmethod
    def _define_tools(self) -> List[Dict]:
        """
        Define OpenAI function calling tools for this agent.

        Each agent must implement this to define its specialized tools.

        Returns:
            List of tool definitions in OpenAI format
        """
        pass

    @abstractmethod
    def execute(self, message: AgentMessage) -> AgentResponse:
        """
        Main execution method - handle incoming message and return response.

        Each agent implements its own logic here.

        Args:
            message: AgentMessage with task details

        Returns:
            AgentResponse with results
        """
        pass

    def _execute_tool(self, tool_name: str, tool_args: Dict) -> Dict:
        """
        Execute a tool (to be implemented by subclasses).

        Args:
            tool_name: Name of the tool
            tool_args: Arguments for the tool

        Returns:
            Tool execution result
        """
        raise NotImplementedError(f"Tool execution not implemented for {tool_name}")

    def _run_agentic_loop(self, user_id: str, goal: str, max_iterations: int = 5) -> Dict:
        """
        Run simplified agentic loop (perceive → reason → act → adapt).

        This is the core pattern from app_real.py, simplified.

        Args:
            user_id: User this is for
            goal: What the agent should achieve
            max_iterations: Max decision cycles

        Returns:
            Final result dict
        """
        messages = [{
            "role": "user",
            "content": f"Goal: {goal}\n\nThink step-by-step and use the available tools to achieve this goal."
        }]

        for iteration in range(max_iterations):
            # AI decides what to do
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=messages,
                tools=self.tools,
                tool_choice="auto"
            )

            choice = response.choices[0]
            message = choice.message
            finish_reason = choice.finish_reason

            # AI's reasoning
            if message.content:
                reasoning = message.content
            else:
                reasoning = "(No reasoning provided)"

            # AI chose to use a tool
            if message.tool_calls:
                for tool_call in message.tool_calls:
                    tool_name = tool_call.function.name
                    import json
                    tool_args = json.loads(tool_call.function.arguments)

                    # Execute tool
                    start_time = time.time()
                    result = self._execute_tool(tool_name, tool_args)
                    execution_time = int((time.time() - start_time) * 1000)

                    # Record decision
                    self.shared_state.record_agent_decision(
                        agent_name=self.agent_name,
                        user_id=user_id,
                        decision_type=tool_name,
                        input_data=tool_args,
                        output_data=result,
                        reasoning=reasoning,
                        execution_time_ms=execution_time
                    )

                    # Update conversation
                    messages.append({
                        "role": "assistant",
                        "content": message.content,
                        "tool_calls": [{
                            "id": tool_call.id,
                            "type": "function",
                            "function": {
                                "name": tool_name,
                                "arguments": tool_call.function.arguments
                            }
                        }]
                    })

                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(result)
                    })

            # AI is done
            elif finish_reason == "stop":
                return {
                    "success": True,
                    "result": message.content,
                    "iterations": iteration + 1
                }

        # Reached max iterations
        return {
            "success": False,
            "error": "Max iterations reached",
            "iterations": max_iterations
        }

    def learn_from_feedback(self, feedback: Dict):
        """
        Optional: Learn from user feedback.

        Subclasses can override to implement learning.

        Args:
            feedback: {decision_id, success_value, notes}
        """
        pass  # Default: no learning
