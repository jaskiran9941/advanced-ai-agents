"""Agent tools package.

This package contains:
- registry.py: Tool registry with allowlist/blocklist filtering
- email_tools.py: Custom Gmail analysis tools (5 tools)
- financial_tools.py: Financial analysis and receipt extraction (3 tools)
- calendar_helpers.py: Calendar helper tools using Composio (2 tools)
- composio_tools.py: Integration with Composio for Google Workspace (150+ tools)

Tool Architecture:
- Custom tools: Domain-specific logic (email analysis, financial data, internal data)
- Composio tools: Third-party integrations (Calendar, Drive, Docs)
- Hybrid approach: Both types work together seamlessly
"""

from .registry import Tool, ToolRegistry
from .email_tools import EmailTools, register_email_tools
from .financial_tools import FinancialTools, register_financial_tools
from .calendar_helpers import CalendarHelpers, register_calendar_helpers
from .composio_tools import get_composio_tools, initiate_composio_connection

__all__ = [
    "Tool",
    "ToolRegistry",
    "EmailTools",
    "register_email_tools",
    "FinancialTools",
    "register_financial_tools",
    "CalendarHelpers",
    "register_calendar_helpers",
    "get_composio_tools",
    "initiate_composio_connection",
]
