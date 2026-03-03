"""
agents/shipping.py — Level 6
==============================
Shipping specialist agent. Handles: tracking, delays, carrier issues, delivery ETAs.
Owns tools: get_order_status, search_policies (shipping/refund policies).
"""

import os
import anthropic
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from level6_multi_agent.tools import execute_tool

SHIPPING_TOOLS = [
    {
        "name": "get_order_status",
        "description": "Look up order tracking, carrier, and delivery status.",
        "input_schema": {
            "type": "object",
            "properties": {"order_id": {"type": "string"}},
            "required": ["order_id"],
        },
    },
    {
        "name": "search_policies",
        "description": "Search Acme Shop shipping and delivery policy documents.",
        "input_schema": {
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"],
        },
    },
]

SHIPPING_SYSTEM = """You are the Shipping specialist at Acme Shop support.
Your domain: delivery tracking, shipping delays, carrier issues, ETAs, shipping policies.
Be specific: always cite tracking numbers, carrier names, and estimated dates."""


def run(ticket: str, context: str = "", on_step=None) -> str:
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"), max_retries=5)
    messages = [{"role": "user", "content": f"{context}\n\nCustomer ticket: {ticket}".strip()}]

    while True:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            system=SHIPPING_SYSTEM,
            tools=SHIPPING_TOOLS,
            messages=messages,
        )

        if on_step:
            on_step("agent_call", {
                "agent": "shipping",
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
                    on_step("tool_call", {"agent": "shipping", "tool": block.name, "input": block.input})
                result = execute_tool(block.name, block.input)
                if on_step:
                    on_step("tool_result", {"agent": "shipping", "tool": block.name, "result": result})
                tool_results.append({"type": "tool_result", "tool_use_id": block.id, "content": result})
            messages.append({"role": "user", "content": tool_results})
