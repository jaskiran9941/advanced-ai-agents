"""
orchestrator.py — Level 6
===========================
The orchestrator is a manager, not a doer.

Responsibilities:
  1. ROUTE  — read the ticket, decide which specialists are needed
  2. DISPATCH — call each specialist sequentially, passing relevant context
  3. SYNTHESIZE — combine specialist outputs into one coherent response

It makes 2 Claude calls per conversation:
  Call 1: routing decision (returns JSON)
  Call 2: synthesis (returns final customer-facing text)

It never calls tools directly — that's the specialists' job.

The wall this exposes:
  The orchestrator has NO constraints on what specialists can do.
  Billing can issue any refund. Technical can promise any replacement.
  There are no refund limits, no confidence checks, no escalation policy.
  Ask for a $10,000 refund — it will try to process it.
"""

import os
import json
import anthropic
from agents import billing, shipping, technical

ROUTING_SYSTEM = """You are a customer support team manager at Acme Shop.

Read the customer's ticket and decide which specialist agents are needed.
Available specialists:
  - billing:   refunds, returns, billing disputes, order status
  - shipping:  delivery tracking, delays, carrier issues, ETAs
  - technical: product defects, warranty claims, replacements, troubleshooting

Return ONLY a JSON object:
{
  "specialists": ["billing", "shipping"],  (list, only those needed)
  "billing_context": "...",   (what specifically billing needs to handle, or omit if not needed)
  "shipping_context": "...",  (what specifically shipping needs to handle, or omit if not needed)
  "technical_context": "..."  (what specifically technical needs to handle, or omit if not needed)
}

Be precise in context — tell each specialist exactly what part of the ticket is theirs."""

SYNTHESIS_SYSTEM = """You are a customer support team manager at Acme Shop.

You have received responses from one or more specialist agents.
Write a single, coherent, friendly response to the customer that:
- Combines all specialist findings naturally (no "our billing team says..." — just say it directly)
- Is specific: include order IDs, amounts, timelines
- Addresses every part of the original ticket
- Reads as one unified message, not a list of separate answers"""


def route(ticket: str, client: anthropic.Anthropic, on_step=None) -> dict:
    """Call 1: decide which specialists are needed."""
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        system=ROUTING_SYSTEM,
        messages=[{"role": "user", "content": ticket}],
    )
    raw = response.content[0].text.strip()

    if on_step:
        on_step("routing", {
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
            "raw": raw,
        })

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Fallback: send to all specialists
        return {"specialists": ["billing", "shipping", "technical"]}


def synthesize(ticket: str, specialist_outputs: dict, client: anthropic.Anthropic, on_step=None) -> str:
    """Call 2: combine specialist outputs into one customer response."""
    parts = [f"Original customer ticket:\n{ticket}\n"]
    for name, output in specialist_outputs.items():
        parts.append(f"{name.upper()} SPECIALIST RESPONSE:\n{output}")
    combined = "\n\n---\n\n".join(parts)

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=SYNTHESIS_SYSTEM,
        messages=[{"role": "user", "content": combined}],
    )

    if on_step:
        on_step("synthesis", {
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
            "specialist_outputs": specialist_outputs,   # what each specialist returned
        })

    return response.content[0].text


SPECIALIST_MAP = {
    "billing": billing,
    "shipping": shipping,
    "technical": technical,
}


def run(ticket: str, customer_history: str = "", on_step=None) -> str:
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"), max_retries=5)

    # Prepend customer history to the ticket so routing is aware of context
    full_ticket = f"{customer_history}\n\nCustomer message: {ticket}".strip() if customer_history else ticket

    # ── Step 1: Route ─────────────────────────────────────────────────────
    routing = route(full_ticket, client, on_step=on_step)
    specialists_needed = routing.get("specialists", [])

    if on_step:
        on_step("route_decision", {"specialists": specialists_needed})

    # ── Step 2: Dispatch to each specialist ───────────────────────────────
    specialist_outputs = {}
    for name in specialists_needed:
        module = SPECIALIST_MAP.get(name)
        if not module:
            continue

        context = routing.get(f"{name}_context", "")

        if on_step:
            on_step("specialist_start", {
                "agent": name,
                "ticket": ticket,           # original customer message
                "context": context,         # what orchestrator told this specialist
            })

        result = module.run(ticket, context=context, on_step=on_step)
        specialist_outputs[name] = result

        if on_step:
            on_step("specialist_done", {"agent": name, "result": result})

    # ── Step 3: Synthesize ────────────────────────────────────────────────
    if len(specialist_outputs) == 1:
        # Only one specialist — no need to synthesize, return directly
        only_result = list(specialist_outputs.values())[0]
        if on_step:
            on_step("synthesis_skipped", {"reason": "single specialist"})
        return only_result

    return synthesize(ticket, specialist_outputs, client, on_step=on_step)
