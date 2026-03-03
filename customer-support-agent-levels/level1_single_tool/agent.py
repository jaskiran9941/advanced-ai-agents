"""
agent.py — Level 1
==================
The agent loop. This is the heart of the level.

The pattern:
  1. Send messages to Claude (with tool schemas attached)
  2. Claude responds — either with text (done) or a tool_use block (needs data)
  3. If tool_use: execute the tool, append result, loop back to step 1
  4. If text: we're done, return the reply

stop_reason is the key signal:
  "end_turn"  → Claude finished, return its text
  "tool_use"  → Claude wants to call a tool, keep looping
"""

import os
import anthropic
from tools import TOOL_SCHEMAS, execute_tool

SYSTEM_PROMPT = """You are a customer support agent for Acme Shop, a fictional electronics retailer.

You have access to a tool that can look up real order information. Use it whenever a customer
asks about a specific order — don't guess or make up order details.

Be friendly, concise, and professional. If the customer doesn't provide an order ID when asking
about an order, ask them for it before calling the tool."""


def run_agent(messages: list, on_step=None) -> str:
    """
    Run the agent loop until Claude produces a final text response.

    Args:
        messages:  The full conversation history (list of role/content dicts).
        on_step:   Optional callback(event_type, data) — used by app.py to
                   stream each step into the Agent Internals panel.

    Returns:
        The assistant's final text reply as a string.
    """
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    # We'll keep looping until Claude stops asking for tools
    loop_count = 0

    while True:
        loop_count += 1

        # ── Step 1: Call Claude ───────────────────────────────────────────
        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            tools=TOOL_SCHEMAS,      # <-- this is new vs Level 0
            messages=messages,
        )

        if on_step:
            on_step("llm_call", {
                "loop": loop_count,
                "stop_reason": response.stop_reason,
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
                "content_types": [b.type for b in response.content],
            })

        # ── Step 2: Check why Claude stopped ─────────────────────────────
        if response.stop_reason == "end_turn":
            # Claude is done — extract and return the text
            final_text = next(b.text for b in response.content if b.type == "text")
            return final_text

        if response.stop_reason == "tool_use":
            # Claude wants to call a tool. There may be multiple tool_use
            # blocks in one response, but at Level 1 there's only one tool
            # and Claude typically calls it once.

            # Append Claude's full response to messages so it stays in context
            messages.append({"role": "assistant", "content": response.content})

            # Collect results for all tool calls in this response
            tool_results = []

            for block in response.content:
                if block.type != "tool_use":
                    continue

                tool_name = block.name
                tool_input = block.input

                if on_step:
                    on_step("tool_call", {
                        "tool": tool_name,
                        "input": tool_input,
                    })

                # ── Step 3: Execute the tool ──────────────────────────────
                result = execute_tool(tool_name, tool_input)

                if on_step:
                    on_step("tool_result", {
                        "tool": tool_name,
                        "result": result,
                    })

                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,   # Claude needs this to match result to call
                    "content": result,
                })

            # ── Step 4: Send tool results back and loop ───────────────────
            messages.append({"role": "user", "content": tool_results})
            continue  # back to top — Claude will now answer with the data

        # Unexpected stop reason — bail out
        return f"[Agent stopped unexpectedly: stop_reason={response.stop_reason}]"
