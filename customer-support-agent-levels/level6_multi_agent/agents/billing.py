"""
agents/billing.py — Level 6
============================
Billing specialist agent. Handles: refunds, returns, billing disputes.
Owns tools: get_order_status, get_customer_profile, process_return,
            send_confirmation_email.

Does NOT have: check_inventory, search_policies — not its domain.
"""

import os
import anthropic
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from level6_multi_agent.tools import execute_tool

BILLING_TOOLS = [
    {
        "name": "get_order_status",
        "description": "Look up a customer order by order ID.",
        "input_schema": {
            "type": "object",
            "properties": {"order_id": {"type": "string"}},
            "required": ["order_id"],
        },
    },
    {
        "name": "get_customer_profile",
        "description": "Fetch customer profile (name, email, tier). Use customer_id from order.",
        "input_schema": {
            "type": "object",
            "properties": {"customer_id": {"type": "string"}},
            "required": ["customer_id"],
        },
    },
    {
        "name": "process_return",
        "description": "Initiate a return for a delivered or damaged order.",
        "input_schema": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string"},
                "reason": {"type": "string"},
            },
            "required": ["order_id", "reason"],
        },
    },
    {
        "name": "send_confirmation_email",
        "description": "Send confirmation email to customer.",
        "input_schema": {
            "type": "object",
            "properties": {
                "to_email": {"type": "string"},
                "subject": {"type": "string"},
                "body": {"type": "string"},
            },
            "required": ["to_email", "subject", "body"],
        },
    },
]

BILLING_SYSTEM = """You are the Billing specialist at Acme Shop support.
Your domain: refunds, returns, billing disputes, order status lookups.
You handle ONLY billing-related issues. Be specific with amounts and timelines.
Always get the customer profile before sending a confirmation email."""


def run(ticket: str, context: str = "", on_step=None) -> str:
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"), max_retries=5)
    messages = [{"role": "user", "content": f"{context}\n\nCustomer ticket: {ticket}".strip()}]

    while True:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            system=BILLING_SYSTEM,
            tools=BILLING_TOOLS,
            messages=messages,
        )

        if on_step:
            on_step("agent_call", {
                "agent": "billing",
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
                    on_step("tool_call", {"agent": "billing", "tool": block.name, "input": block.input})
                result = execute_tool(block.name, block.input)
                if on_step:
                    on_step("tool_result", {"agent": "billing", "tool": block.name, "result": result})
                tool_results.append({"type": "tool_result", "tool_use_id": block.id, "content": result})
            messages.append({"role": "user", "content": tool_results})
