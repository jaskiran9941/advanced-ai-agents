"""
agent.py — Level 5
==================
Adds a reflection loop around the standard agent turn.

Architecture:
  1. run_agent_turn()  — the same tool-use loop as L1-L4.
                         Produces a draft response.
  2. critique()        — a second Claude call that reads the customer's
                         original message + the draft, then returns:
                           { "complete": true/false, "issues": "..." }
  3. run_agent()       — orchestrates the loop:
                         draft → critique → if gaps: regenerate with feedback
                         → critique again → repeat up to MAX_ATTEMPTS times.

Why a cap?
  Without MAX_ATTEMPTS, a stubborn critic + a flawed draft = infinite loop.
  Production systems always cap reflection passes and track the cost.
  We cap at 3 — enough to show multi-pass correction, cheap enough to demo.

Cost reality:
  Best case (draft is complete):   1 agent call + 1 critique call
  Worst case (needs 3 attempts):   3 agent calls + 3 critique calls
  Every reflection pass costs real tokens. That's the wall this level shows.
"""

import os
import json
import anthropic
from tools import TOOL_SCHEMAS, execute_tool

MAX_ATTEMPTS = 3

SUPPORT_SYSTEM_PROMPT = """You are a customer support agent for Acme Shop, a fictional electronics retailer.

You have tools to look up orders, customer profiles, inventory, process returns,
send confirmation emails, and search official policy documents.

Guidelines:
- For policy questions, always call search_policies first.
- Chain tools as needed. Send a confirmation email after any completed action.
- Be specific: use the customer's name, order IDs, product names, timelines."""

CRITIC_PROMPT = """You are a quality reviewer for customer support responses.

Your job: check whether the agent's response fully addressed the customer's message.

Look for:
- Unresolved issues (customer mentioned X, agent ignored X)
- Vague promises without specifics (said "we'll handle it" but didn't)
- Missing follow-through (started a return but forgot the confirmation email)
- Multiple questions where only some were answered

Return ONLY a JSON object:
{
  "complete": true or false,
  "issues": "describe any gaps concisely, or empty string if complete"
}

Be strict. If anything is missing or vague, mark complete as false."""


def build_system_prompt(customer_history: str) -> str:
    prompt = SUPPORT_SYSTEM_PROMPT
    if customer_history:
        prompt += f"\n\n{customer_history}\n\nUse this history to personalise your response."
    return prompt


def run_agent_turn(messages: list, system_prompt: str, client: anthropic.Anthropic, on_step=None) -> str:
    """
    Standard tool-use loop. Returns the final text response (the draft).
    """
    loop_count = 0
    # Work on a copy so the caller's messages list isn't mutated mid-reflection
    local_messages = list(messages)

    while True:
        loop_count += 1

        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            system=system_prompt,
            tools=TOOL_SCHEMAS,
            messages=local_messages,
        )

        if on_step:
            on_step("llm_call", {
                "loop": loop_count,
                "stop_reason": response.stop_reason,
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
            })

        if response.stop_reason == "end_turn":
            draft = next(b.text for b in response.content if b.type == "text")
            # Append to local_messages so future reflection passes have context
            local_messages.append({"role": "assistant", "content": draft})
            # Also update the caller's messages list with all the tool turns
            messages.clear()
            messages.extend(local_messages)
            return draft

        if response.stop_reason == "tool_use":
            local_messages.append({"role": "assistant", "content": response.content})
            tool_results = []

            for block in response.content:
                if block.type != "tool_use":
                    continue
                if on_step:
                    on_step("tool_call", {"tool": block.name, "input": block.input})
                result = execute_tool(block.name, block.input)
                if on_step:
                    on_step("tool_result", {"tool": block.name, "result": result})
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result,
                })

            local_messages.append({"role": "user", "content": tool_results})
            continue

        return f"[Unexpected stop_reason: {response.stop_reason}]"


def critique(customer_message: str, draft: str, client: anthropic.Anthropic, on_step=None) -> dict:
    """
    Run the critic. Returns {"complete": bool, "issues": str}.
    """
    critic_input = f"Customer message:\n{customer_message}\n\nAgent response:\n{draft}"

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=256,
        system=CRITIC_PROMPT,
        messages=[{"role": "user", "content": critic_input}],
    )

    raw = response.content[0].text.strip()

    if on_step:
        on_step("critique", {
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
            "raw": raw,
        })

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # If Claude didn't return clean JSON, treat as incomplete
        return {"complete": False, "issues": raw[:200]}


def run_agent(messages: list, customer_history: str = "", on_step=None) -> str:
    """
    Reflection loop:
      attempt 1: draft → critique
      attempt 2: if gaps, add critique as context, regenerate → critique again
      attempt 3: same
      after MAX_ATTEMPTS: return whatever we have
    """
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"), max_retries=5)
    system_prompt = build_system_prompt(customer_history)

    # The original customer message — needed by the critic
    customer_message = next(
        (m["content"] for m in reversed(messages)
         if isinstance(m["content"], str) and m["role"] == "user"),
        ""
    )

    draft = None

    for attempt in range(1, MAX_ATTEMPTS + 1):

        if on_step:
            on_step("attempt_start", {"attempt": attempt, "max": MAX_ATTEMPTS})

        # ── Step 1: produce a draft ───────────────────────────────────────
        draft = run_agent_turn(messages, system_prompt, client, on_step=on_step)

        # ── Step 2: critique the draft ────────────────────────────────────
        verdict = critique(customer_message, draft, client, on_step=on_step)

        if verdict.get("complete", False):
            if on_step:
                on_step("reflection_done", {"attempt": attempt, "result": "complete"})
            return draft

        # ── Step 3: gaps found — inject critique and loop ─────────────────
        issues = verdict.get("issues", "Response was incomplete.")

        if on_step:
            on_step("reflection_retry", {"attempt": attempt, "issues": issues})

        if attempt < MAX_ATTEMPTS:
            # Tell the agent what it missed so it can fix it
            messages.append({
                "role": "user",
                "content": (
                    f"[Quality review found gaps in your response]: {issues}\n\n"
                    f"Please provide a complete response that addresses everything."
                ),
            })

    # Exhausted all attempts — return the last draft
    if on_step:
        on_step("reflection_done", {"attempt": MAX_ATTEMPTS, "result": "max_attempts_reached"})
    return draft
