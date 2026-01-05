"""
Orchestrator Agent (Simplified)

Coordinates specialized agents to achieve user goals.
"""

from openai import OpenAI
import httpx
from typing import Dict, List
from core.shared_state import SharedStateManager
from core.message_protocol import AgentMessage, create_discovery_message, create_curator_message, create_personalization_message, create_delivery_message
from agents import PodcastDiscoveryAgent, ContentCuratorAgent, PersonalizationAgent, DeliveryAgent


class OrchestratorAgent:
    """
    Coordinates multi-agent workflows.

    Simplified: Pre-defined workflow sequences instead of dynamic routing.
    """

    def __init__(self, api_key: str, db_path: str = "podcast_multiagent.db", verify_ssl: bool = False):
        """
        Initialize orchestrator.

        Args:
            api_key: OpenAI API key
            db_path: Database path
            verify_ssl: Whether to verify SSL certificates (default False for local testing)
        """
        # Create HTTP client with SSL verification option
        http_client = httpx.Client(verify=verify_ssl) if not verify_ssl else None

        self.client = OpenAI(api_key=api_key, http_client=http_client)
        self.shared_state = SharedStateManager(db_path)

        # Initialize all specialist agents
        self.agents = {
            "discovery": PodcastDiscoveryAgent(api_key, self.shared_state, verify_ssl=verify_ssl),
            "curator": ContentCuratorAgent(api_key, self.shared_state, verify_ssl=verify_ssl),
            "personalization": PersonalizationAgent(api_key, self.shared_state, verify_ssl=verify_ssl),
            "delivery": DeliveryAgent(api_key, self.shared_state, verify_ssl=verify_ssl)
        }

    def execute(self, user_id: str, user_goal: str) -> Dict:
        """
        Execute multi-agent workflow.

        Simplified workflow:
        1. Discovery finds podcasts
        2. Curator filters by relevance
        3. Personalization creates summaries
        4. Delivery schedules them

        Args:
            user_id: User identifier
            user_goal: What user wants

        Returns:
            {
                "success": bool,
                "task_id": str,
                "agent_sequence": List[str],
                "final_result": Dict,
                "agent_outputs": Dict  # Output from each agent
            }
        """
        # Create orchestrator task
        task_id = self.shared_state.create_task(
            user_id=user_id,
            user_goal=user_goal,
            intent_classification={
                "workflow": "default",
                "agents": ["discovery", "curator", "personalization", "delivery"]
            }
        )

        self.shared_state.update_task_status(task_id, "in_progress")

        agent_outputs = {}
        agent_sequence = []

        try:
            # Step 1: Discovery
            discovery_result = self._run_discovery(user_id, user_goal, task_id)
            agent_outputs["discovery"] = discovery_result
            agent_sequence.append("discovery")

            # Step 2: Curator (using discovery results)
            curator_result = self._run_curator(user_id, discovery_result, task_id)
            agent_outputs["curator"] = curator_result
            agent_sequence.append("curator")

            # Step 3: Personalization
            personalization_result = self._run_personalization(user_id, curator_result, task_id)
            agent_outputs["personalization"] = personalization_result
            agent_sequence.append("personalization")

            # Step 4: Delivery
            delivery_result = self._run_delivery(user_id, personalization_result, task_id)
            agent_outputs["delivery"] = delivery_result
            agent_sequence.append("delivery")

            # Mark task complete
            self.shared_state.update_task_status(
                task_id,
                status="completed",
                agent_sequence=agent_sequence,
                result=agent_outputs
            )

            return {
                "success": True,
                "task_id": task_id,
                "agent_sequence": agent_sequence,
                "final_result": delivery_result,
                "agent_outputs": agent_outputs
            }

        except Exception as e:
            import traceback
            error_details = f"{type(e).__name__}: {str(e)}"
            full_trace = traceback.format_exc()

            self.shared_state.update_task_status(
                task_id,
                status="failed",
                error=error_details
            )

            print(f"ERROR in orchestrator: {error_details}")
            print(f"Full traceback:\n{full_trace}")

            return {
                "success": False,
                "task_id": task_id,
                "error": error_details,
                "error_trace": full_trace,
                "agent_outputs": agent_outputs
            }

    def _run_discovery(self, user_id: str, user_goal: str, task_id: str) -> Dict:
        """Run discovery agent."""
        # Simple: extract topics from goal using GPT
        topics_prompt = f"Extract 2-3 podcast search topics from: {user_goal}\nReturn as comma-separated list:"

        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": topics_prompt}],
            max_tokens=50
        )

        topics_text = response.choices[0].message.content
        topics = [t.strip() for t in topics_text.split(",")]

        # Create message for discovery agent
        message = create_discovery_message(user_id, topics, task_id, limit=5)

        # Execute
        response = self.agents["discovery"].execute(message)

        return response.output_data

    def _run_curator(self, user_id: str, discovery_result: Dict, task_id: str) -> Dict:
        """Run curator agent (simplified - just pass through for now)."""
        # In simplified version, assume all discovered podcasts are relevant
        return {
            "success": True,
            "curated_podcasts": discovery_result.get("result", "No podcasts found"),
            "relevance_note": "Simplified curator - accepted all discovered podcasts"
        }

    def _run_personalization(self, user_id: str, curator_result: Dict, task_id: str) -> Dict:
        """Run personalization agent (simplified)."""
        # For learning demo, just return formatted result
        return {
            "success": True,
            "personalized_content": curator_result,
            "style": "User preference applied"
        }

    def _run_delivery(self, user_id: str, personalization_result: Dict, task_id: str) -> Dict:
        """Run delivery agent (simplified)."""
        # Simple delivery plan
        return {
            "success": True,
            "delivery_plan": {
                "when": "Now",
                "how": "Display in UI",
                "content": personalization_result
            }
        }


# Simplified version for quick testing
class SimpleOrchestrator:
    """Even simpler orchestrator for testing - just runs discovery."""

    def __init__(self, api_key: str, db_path: str = "podcast_multiagent.db", verify_ssl: bool = False):
        self.shared_state = SharedStateManager(db_path)
        self.discovery_agent = PodcastDiscoveryAgent(api_key, self.shared_state, verify_ssl=verify_ssl)

    def execute(self, user_id: str, topics: List[str]) -> Dict:
        """Just run discovery."""
        task_id = self.shared_state.generate_id("task")

        message = create_discovery_message(user_id, topics, task_id)
        response = self.discovery_agent.execute(message)

        return {
            "success": response.success,
            "result": response.output_data
        }
