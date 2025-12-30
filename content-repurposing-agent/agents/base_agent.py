"""
Base agent class using Agno AI framework.

This serves as the foundation for all specialized agents in the system.
"""
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
from agno.agent import Agent as AgnoAgent
from config.settings import settings
from utils.logger import setup_logger

class BaseAgent(ABC):
    """
    Base class for all agents in the content repurposing system.

    Each agent can use different LLM providers (Claude, Gemini, GPT)
    and has access to specialized tools.
    """

    def __init__(
        self,
        name: str,
        role: str,
        llm_provider: str = "claude",
        instructions: Optional[str] = None,
        tools: Optional[List] = None,
        **kwargs
    ):
        """
        Initialize base agent.

        Args:
            name: Agent name
            role: Agent role/purpose
            llm_provider: LLM to use ("claude", "gemini", "openai")
            instructions: System instructions for the agent
            tools: List of tools the agent can use
            **kwargs: Additional arguments for Agno Agent
        """
        self.name = name
        self.role = role
        self.llm_provider = llm_provider
        self.logger = setup_logger(f"agent.{name}")

        # Select LLM model based on provider
        self.model = self._get_model(llm_provider)

        # Create Agno agent
        self.agent = AgnoAgent(
            name=name,
            model=self.model,
            instructions=instructions or self._default_instructions(),
            tools=tools or [],
            markdown=True,
            description=role,  # Use role as description
            **kwargs
        )

        self.logger.info(f"Initialized {name} agent with {llm_provider} provider")

    def _get_model(self, provider: str):
        """
        Get the LLM model based on provider.

        Args:
            provider: LLM provider name

        Returns:
            Configured LLM model instance
        """
        # Use mock API key if real one not provided
        if provider == "claude":
            from agno.models.anthropic import Claude
            api_key = settings.llm.anthropic_api_key or "mock-key-for-testing"
            return Claude(
                id="claude-sonnet-4-20250514",
                api_key=api_key
            )
        elif provider == "gemini":
            from agno.models.google import Gemini
            api_key = settings.llm.google_api_key or "mock-key-for-testing"
            return Gemini(
                id="gemini-2.0-flash-exp",
                api_key=api_key
            )
        elif provider == "openai":
            from agno.models.openai import OpenAIChat
            api_key = settings.llm.openai_api_key or "mock-key-for-testing"
            return OpenAIChat(
                id="gpt-4-turbo-preview",
                api_key=api_key
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")

    @abstractmethod
    def _default_instructions(self) -> str:
        """
        Return default system instructions for this agent.
        Must be implemented by subclasses.
        """
        pass

    def _get_mock_response(self, task: str) -> str:
        """
        Generate a mock response when API is unavailable.
        Can be overridden by subclasses for specific mock data.
        """
        return f"[MOCK RESPONSE] This is simulated output for: {task[:100]}..."

    def run(self, task: str, **kwargs) -> Any:
        """
        Execute the agent with a given task.

        Args:
            task: Task description/prompt for the agent
            **kwargs: Additional arguments

        Returns:
            Agent response
        """
        self.logger.info(f"Running {self.name} with task: {task[:100]}...")

        try:
            response = self.agent.run(task, **kwargs)

            # Check if response contains an error (agno catches API errors and puts them in response)
            response_content = response.content if hasattr(response, 'content') else str(response)
            if "Error code: 401" in response_content or "token is missing" in response_content:
                self.logger.warning(f"{self.name} using mock response due to missing API key")
                return self._get_mock_response(task)

            self.logger.info(f"{self.name} completed successfully")
            return response
        except Exception as e:
            # Check if it's an API authentication error
            error_str = str(e)
            if "401" in error_str or "token is missing" in error_str or "authentication" in error_str.lower():
                self.logger.warning(f"{self.name} using mock response due to missing API key")
                return self._get_mock_response(task)
            else:
                self.logger.error(f"{self.name} failed: {str(e)}")
                raise

    async def arun(self, task: str, **kwargs) -> Any:
        """
        Async execution of the agent.

        Args:
            task: Task description/prompt for the agent
            **kwargs: Additional arguments

        Returns:
            Agent response
        """
        self.logger.info(f"Running {self.name} async with task: {task[:100]}...")

        try:
            response = await self.agent.arun(task, **kwargs)
            self.logger.info(f"{self.name} completed successfully")
            return response
        except Exception as e:
            self.logger.error(f"{self.name} failed: {str(e)}")
            raise

    def get_info(self) -> Dict[str, Any]:
        """
        Get agent information.

        Returns:
            Dictionary with agent details
        """
        return {
            "name": self.name,
            "role": self.role,
            "llm_provider": self.llm_provider,
            "model_id": self.model.id if hasattr(self.model, 'id') else "unknown"
        }
