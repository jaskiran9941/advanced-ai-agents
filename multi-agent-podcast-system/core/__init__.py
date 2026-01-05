"""Core modules for multi-agent podcast system."""

from .shared_state import SharedStateManager
from .message_protocol import AgentMessage, AgentResponse, TaskContext

__all__ = [
    'SharedStateManager',
    'AgentMessage',
    'AgentResponse',
    'TaskContext'
]
