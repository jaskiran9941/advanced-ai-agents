"""
agents/billing.py — Level 7
============================
Billing specialist node for the LangGraph.

Key difference from L6:
  - Receives and returns SupportState (typed dict), not a prose string
  - Writes refund_amount (float) and return_processed (bool) to state
  - Sets approval_required = True if refund_amount > APPROVAL_THRESHOLD
  - Graph reads approval_required to decide: continue or pause for human
"""

import os
import sys
import anthropic

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from level7_langgraph.state import SupportState, APPROVAL_THRESHOLD

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
        "description": "Fetch customer profile. Use customer_id from order result.",
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
                "reason":   {"type": "string"},
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
                "subject":  {"type": "string"},
                "body":     {"type": "string"},
            },
            "required": ["to_email", "subject", "body"],
        },
    },
]

BILLING_SYSTEM = """You are the Billing specialist at Acme Shop support.
Your domain: refunds, returns, billing disputes.

IMPORTANT: When you process a return or refund, you MUST include this exact
line in your response so the system can extract it:
  REFUND_AMOUNT: <number>

For example: REFUND_AMOUNT: 149.00

If no refund is being processed, write: REFUND_AMOUNT: 0

Be specific with amounts and timelines."""

BILLING_SYSTEM_REJECTED = """You are the Billing specialist at Acme Shop support.

A human reviewer has REJECTED the large refund request. You must offer an alternative:
  - Store credit for the full amount, OR
  - A partial refund up to $200 to their original payment method

Be empathetic but clear about the limitation."""


def _extract_refund_amount(text: str) -> float:
    """Parse 'REFUND_AMOUNT: 149.00' from billing agent response."""
    import re
    match = re.search(r"REFUND_AMOUNT:\s*([\d.]+)", text)
    return float(match.group(1)) if match else 0.0


def _run_loop(system: str, messages: list, on_step=None) -> str:
    from level7_langgraph.tools import execute_tool
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"), max_retries=5)

    while True:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            system=system,
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


def run(state: SupportState, on_step=None) -> dict:
    """LangGraph node: billing agent. Returns state updates."""
    context = state.get("billing_context", "")
    ticket  = state["ticket"]
    msg     = f"{context}\n\nCustomer ticket: {ticket}".strip() if context else ticket

    result = _run_loop(BILLING_SYSTEM, [{"role": "user", "content": msg}], on_step)
    refund = _extract_refund_amount(result)

    updates = {
        "billing_result":    result,
        "refund_amount":     refund,
        "return_processed":  "return" in result.lower() and refund > 0,
        "approval_required": refund > APPROVAL_THRESHOLD,
        "approval_reason":   f"Refund of ${refund:.2f} exceeds the ${APPROVAL_THRESHOLD:.0f} auto-approval limit." if refund > APPROVAL_THRESHOLD else "",
    }
    return updates


def run_after_rejection(state: SupportState, on_step=None) -> dict:
    """Re-run billing with rejection context to offer alternative."""
    rejection = state.get("rejection_reason", "No reason given.")
    original  = state.get("billing_result", "")
    ticket    = state["ticket"]

    msg = (
        f"Original ticket: {ticket}\n\n"
        f"Your original response was:\n{original}\n\n"
        f"A human reviewer rejected the refund. Reason: {rejection}\n\n"
        f"Please offer an alternative: store credit or partial refund up to $200."
    )

    result = _run_loop(BILLING_SYSTEM_REJECTED, [{"role": "user", "content": msg}], on_step)
    return {
        "billing_result":    result,
        "refund_amount":     min(state.get("refund_amount", 0), 200.0),
        "approval_required": False,
    }
