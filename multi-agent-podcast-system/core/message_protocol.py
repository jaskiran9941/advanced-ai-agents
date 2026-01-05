"""
Agent Message Protocol

Standardized format for inter-agent communication.
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, Any, Optional
from datetime import datetime
import uuid


@dataclass
class AgentMessage:
    """
    Standard message format for communication between agents.

    Example:
        message = AgentMessage(
            from_agent="orchestrator",
            to_agent="discovery",
            task_type="find_podcasts",
            context={"user_id": "user_123", "topics": ["AI"]},
            input_data={"search_query": "AI podcasts", "limit": 5}
        )
    """

    # Required fields
    from_agent: str  # Sender: 'orchestrator', 'discovery', 'curator', etc.
    to_agent: str   # Recipient: which agent should handle this
    task_type: str  # What to do: 'find_podcasts', 'analyze_relevance', 'generate_summary'
    context: Dict[str, Any]  # Shared context: {user_id, user_goal, constraints}
    input_data: Dict[str, Any]  # Task-specific input data

    # Auto-generated fields
    message_id: str = field(default_factory=lambda: f"msg_{uuid.uuid4().hex[:12]}")
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    # Optional fields
    parent_task_id: Optional[str] = None  # Link to orchestrator task
    priority: int = 5  # 1-10, higher = more urgent
    expected_output_type: Optional[str] = None  # What format to return
    metadata: Dict[str, Any] = field(default_factory=dict)  # Additional info

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'AgentMessage':
        """Create AgentMessage from dictionary."""
        return cls(**data)

    def create_response(self, from_agent: str, output_data: Dict) -> 'AgentResponse':
        """
        Create a response message to this message.

        Args:
            from_agent: Agent sending the response
            output_data: Result of the task

        Returns:
            AgentResponse object
        """
        return AgentResponse(
            request_message_id=self.message_id,
            from_agent=from_agent,
            to_agent=self.from_agent,  # Send back to sender
            output_data=output_data,
            parent_task_id=self.parent_task_id
        )


@dataclass
class AgentResponse:
    """
    Standard response format from an agent.

    Example:
        response = AgentResponse(
            request_message_id="msg_abc123",
            from_agent="discovery",
            to_agent="orchestrator",
            output_data={"podcasts": [...], "count": 5},
            success=True,
            execution_time_ms=1234
        )
    """

    # Required fields
    request_message_id: str  # Which message this responds to
    from_agent: str  # Who is responding
    to_agent: str  # Who should receive this
    output_data: Dict[str, Any]  # The result

    # Status fields
    success: bool = True
    error_message: Optional[str] = None
    execution_time_ms: Optional[int] = None

    # Auto-generated
    response_id: str = field(default_factory=lambda: f"resp_{uuid.uuid4().hex[:12]}")
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    # Optional
    parent_task_id: Optional[str] = None
    confidence_score: Optional[float] = None  # 0-1, how confident in the result
    reasoning: Optional[str] = None  # AI's explanation
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'AgentResponse':
        """Create from dictionary."""
        return cls(**data)


@dataclass
class TaskContext:
    """
    Shared context passed between agents during a workflow.

    Contains everything agents need to know about the current task.
    """

    user_id: str
    user_goal: str  # Original user request
    parent_task_id: str

    # User context
    user_preferences: Dict[str, Any] = field(default_factory=dict)
    learned_preferences: Dict[str, Any] = field(default_factory=dict)

    # Task state
    agent_sequence: list = field(default_factory=list)  # Which agents have run
    intermediate_results: Dict[str, Any] = field(default_factory=dict)  # Results from each agent

    # Constraints
    max_execution_time_seconds: int = 30
    cost_budget_dollars: float = 0.50

    # Metadata
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_agent_result(self, agent_name: str, result: Dict):
        """Record result from an agent."""
        self.agent_sequence.append(agent_name)
        self.intermediate_results[agent_name] = {
            "result": result,
            "timestamp": datetime.now().isoformat()
        }

    def get_agent_result(self, agent_name: str) -> Optional[Dict]:
        """Get result from a previous agent."""
        return self.intermediate_results.get(agent_name, {}).get("result")

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'TaskContext':
        """Create from dictionary."""
        return cls(**data)


# Convenience functions for creating messages

def create_discovery_message(user_id: str, topics: List[str], task_id: str,
                             limit: int = 5) -> AgentMessage:
    """Create a message for PodcastDiscoveryAgent."""
    return AgentMessage(
        from_agent="orchestrator",
        to_agent="discovery",
        task_type="discover_podcasts",
        context={
            "user_id": user_id,
            "topics": topics
        },
        input_data={
            "search_topics": topics,
            "max_results": limit
        },
        parent_task_id=task_id
    )


def create_curator_message(user_id: str, episodes: List[Dict],
                           task_id: str) -> AgentMessage:
    """Create a message for ContentCuratorAgent."""
    return AgentMessage(
        from_agent="orchestrator",
        to_agent="curator",
        task_type="curate_content",
        context={
            "user_id": user_id
        },
        input_data={
            "episodes": episodes
        },
        parent_task_id=task_id
    )


def create_personalization_message(user_id: str, episode: Dict,
                                   user_context: Dict, task_id: str) -> AgentMessage:
    """Create a message for PersonalizationAgent."""
    return AgentMessage(
        from_agent="orchestrator",
        to_agent="personalization",
        task_type="personalize_summary",
        context={
            "user_id": user_id,
            "user_state": user_context.get("current_state", "normal")
        },
        input_data={
            "episode": episode,
            "user_context": user_context
        },
        parent_task_id=task_id
    )


def create_delivery_message(user_id: str, summaries: List[Dict],
                            task_id: str) -> AgentMessage:
    """Create a message for DeliveryAgent."""
    return AgentMessage(
        from_agent="orchestrator",
        to_agent="delivery",
        task_type="schedule_delivery",
        context={
            "user_id": user_id
        },
        input_data={
            "summaries": summaries
        },
        parent_task_id=task_id
    )
