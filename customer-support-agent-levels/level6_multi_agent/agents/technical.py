"""
agents/technical.py — Level 6
================================
Technical specialist agent. Handles: product defects, warranty claims,
replacements, troubleshooting.
Owns tools: get_order_status, check_inventory, search_policies (warranty).
"""

import os
import anthropic
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from level6_multi_agent.tools import execute_tool

TECHNICAL_TOOLS = [
    {
        "name": "get_order_status",
        "description": "Look up order details and any damage/defect notes.",
        "input_schema": {
            "type": "object",
            "properties": {"order_id": {"type": "string"}},
            "required": ["order_id"],
        },
    },
    {
        "name": "check_inventory",
        "description": "Check stock levels for a replacement product.",
        "input_schema": {
            "type": "object",
            "properties": {"product_id": {"type": "string"}},
            "required": ["product_id"],
        },
    },
    {
        "name": "search_policies",
        "description": "Search Acme Shop warranty and return policy documents.",
        "input_schema": {
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"],
        },
    },
]

TECHNICAL_SYSTEM = """You are the Technical specialist at Acme Shop support.
Your domain: product defects, warranty claims, replacements, and technical troubleshooting.
Always check warranty policy before making claims. Check inventory before promising replacements."""


def run(ticket: str, context: str = "", on_step=None) -> str:
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"), max_retries=5)
    messages = [{"role": "user", "content": f"{context}\n\nCustomer ticket: {ticket}".strip()}]

    while True:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            system=TECHNICAL_SYSTEM,
            tools=TECHNICAL_TOOLS,
            messages=messages,
        )

        if on_step:
            on_step("agent_call", {
                "agent": "technical",
                "stop_reason": response.stop_reason,
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
            })

        if response.stop_reason == "end_turn":
            return next(b.text for b in response.content if b.type == "text")

        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})
            tool_results = []
            for block in response.content:
                if block.type != "tool_use":
                    continue
                if on_step:
                    on_step("tool_call", {"agent": "technical", "tool": block.name, "input": block.input})
                result = execute_tool(block.name, block.input)
                if on_step:
                    on_step("tool_result", {"agent": "technical", "tool": block.name, "result": result})
                tool_results.append({"type": "tool_result", "tool_use_id": block.id, "content": result})
            messages.append({"role": "user", "content": tool_results})
