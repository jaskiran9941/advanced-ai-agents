"""Tool registry for managing AI agent tools."""

from typing import Callable, Dict, Any, List, Optional
from dataclasses import dataclass
import structlog

logger = structlog.get_logger()


@dataclass
class Tool:
    """Tool definition for AI agent."""

    name: str
    description: str
    parameters: Dict[str, Any]  # JSON Schema
    function: Callable


class ToolRegistry:
    """Registry for managing and filtering tools."""

    def __init__(self, allowlist: Optional[List[str]] = None, blocklist: Optional[List[str]] = None):
        """Initialize tool registry.

        Args:
            allowlist: List of allowed tool names (None = allow all)
            blocklist: List of blocked tool names
        """
        self._tools: Dict[str, Tool] = {}
        self.allowlist = allowlist
        self.blocklist = blocklist or []

    def register(self, tool: Tool) -> None:
        """Register a tool.

        Args:
            tool: Tool to register
        """
        self._tools[tool.name] = tool
        logger.info("Registered tool", tool_name=tool.name)

    def get_tool(self, name: str) -> Optional[Tool]:
        """Get tool by name.

        Args:
            name: Tool name

        Returns:
            Tool or None if not found
        """
        return self._tools.get(name)

    def get_all_tools(self) -> List[Tool]:
        """Get all registered tools.

        Returns:
            List of all tools
        """
        return list(self._tools.values())

    def get_filtered_tools(self) -> List[Tool]:
        """Get tools filtered by allowlist/blocklist.

        Returns:
            List of filtered tools
        """
        tools = self.get_all_tools()

        # Apply blocklist
        if self.blocklist:
            tools = [t for t in tools if t.name not in self.blocklist]

        # Apply allowlist
        if self.allowlist:
            tools = [t for t in tools if t.name in self.allowlist]

        logger.info("Filtered tools", count=len(tools), total=len(self._tools))
        return tools

    def execute_tool(self, name: str, **kwargs: Any) -> Any:
        """Execute a tool by name.

        Args:
            name: Tool name
            **kwargs: Tool arguments

        Returns:
            Tool execution result

        Raises:
            ValueError: If tool not found or blocked
        """
        tool = self.get_tool(name)
        if not tool:
            raise ValueError(f"Tool not found: {name}")

        # Check if tool is allowed
        if self.blocklist and name in self.blocklist:
            raise ValueError(f"Tool is blocked: {name}")

        if self.allowlist and name not in self.allowlist:
            raise ValueError(f"Tool not in allowlist: {name}")

        logger.info("Executing tool", tool_name=name, kwargs=kwargs)
        result = tool.function(**kwargs)
        logger.info("Tool execution completed", tool_name=name)
        return result

    def to_langchain_tools(self) -> List[Any]:
        """Convert registered tools to LangChain tool format.

        Returns:
            List of LangChain tools
        """
        from langchain.tools import StructuredTool

        filtered_tools = self.get_filtered_tools()
        langchain_tools = []

        for tool in filtered_tools:
            langchain_tool = StructuredTool.from_function(
                func=tool.function,
                name=tool.name,
                description=tool.description,
                args_schema=None,  # We'll use the function signature
            )
            langchain_tools.append(langchain_tool)

        logger.info("Converted to LangChain tools", count=len(langchain_tools))
        return langchain_tools
