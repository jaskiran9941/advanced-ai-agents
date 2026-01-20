"""
Tool Executor Framework

Generic framework for registering and executing agent tools.
Provides a centralized registry for all available tools.
"""

from typing import Dict, Any, Callable, Optional
import logging

logger = logging.getLogger(__name__)


class ToolExecutor:
    """
    Registry and executor for agent tools

    Allows agents to register and execute various tools like:
    - Web search (Tavily)
    - Web scraping
    - Calculators
    - Database queries
    - API calls
    """

    def __init__(self):
        """Initialize empty tool registry"""
        self.tools: Dict[str, Callable] = {}
        self.tool_metadata: Dict[str, Dict[str, Any]] = {}

    def register_tool(
        self,
        name: str,
        tool_callable: Callable,
        description: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ):
        """
        Register a new tool

        Args:
            name: Unique tool identifier (e.g., "web_search", "calculator")
            tool_callable: Function or method to execute
            description: Human-readable description of what the tool does
            parameters: Dictionary describing expected parameters
        """
        if name in self.tools:
            logger.warning(f"Tool '{name}' already registered. Overwriting...")

        self.tools[name] = tool_callable
        self.tool_metadata[name] = {
            "description": description or "No description provided",
            "parameters": parameters or {},
            "callable": tool_callable.__name__
        }

        logger.info(f"Registered tool: {name}")

    def execute(self, tool_name: str, **kwargs) -> Any:
        """
        Execute a registered tool

        Args:
            tool_name: Name of the tool to execute
            **kwargs: Arguments to pass to the tool

        Returns:
            Tool execution result

        Raises:
            ValueError: If tool not found
            Exception: Any exception raised by the tool
        """
        if tool_name not in self.tools:
            available_tools = ", ".join(self.tools.keys())
            raise ValueError(
                f"Tool '{tool_name}' not registered. "
                f"Available tools: {available_tools}"
            )

        try:
            logger.info(f"Executing tool: {tool_name}")
            result = self.tools[tool_name](**kwargs)
            logger.info(f"Tool {tool_name} executed successfully")
            return result

        except Exception as e:
            logger.error(f"Tool {tool_name} execution failed: {str(e)}")
            raise

    def list_tools(self) -> Dict[str, Dict[str, Any]]:
        """
        List all registered tools with their metadata

        Returns:
            Dictionary mapping tool names to their metadata
        """
        return self.tool_metadata.copy()

    def has_tool(self, tool_name: str) -> bool:
        """
        Check if a tool is registered

        Args:
            tool_name: Name of the tool

        Returns:
            True if tool exists, False otherwise
        """
        return tool_name in self.tools

    def unregister_tool(self, tool_name: str):
        """
        Remove a tool from the registry

        Args:
            tool_name: Name of the tool to remove
        """
        if tool_name in self.tools:
            del self.tools[tool_name]
            del self.tool_metadata[tool_name]
            logger.info(f"Unregistered tool: {tool_name}")
        else:
            logger.warning(f"Attempted to unregister non-existent tool: {tool_name}")


# Global tool executor instance for easy access
_global_executor = None


def get_global_tool_executor() -> ToolExecutor:
    """
    Get the global tool executor instance (singleton pattern)

    Returns:
        Global ToolExecutor instance
    """
    global _global_executor
    if _global_executor is None:
        _global_executor = ToolExecutor()
    return _global_executor
