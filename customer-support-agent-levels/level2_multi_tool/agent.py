"""
agent.py — Level 2
==================
Same loop as Level 1 — nothing changes here architecturally.
The only difference: Claude now has 5 tools instead of 1,
so a single customer request can trigger 3-4 tool calls in sequence.

That chain is *implicit* — you never tell Claude the order.
Claude figures out: get order → get customer → check stock → process return → send email.
Watch the Agent Internals panel to see it plan on its own.
"""

import os
import anthropic
from tools import TOOL_SCHEMAS, execute_tool

SYSTEM_PROMPT = """You are a customer support agent for Acme Shop, a fictional electronics retailer.

You have tools to look up orders, customer profiles, inventory, process returns, and send confirmation emails.

Guidelines:
- Always look up the order first before taking any action on it.
- When processing a return, check inventory for a replacement if the customer wants one.
- Always get the customer profile (for their email) before sending a confirmation.
- Send a confirmation email as the final step of any completed action.
- Be friendly, concise, and specific — mention order IDs, product names, and timelines."""


def run_agent(messages: list, on_step=None) -> str:
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    loop_count = 0

    while True:
        loop_count += 1

        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            tools=TOOL_SCHEMAS,
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

        if response.stop_reason == "end_turn":
            final_text = next(b.text for b in response.content if b.type == "text")
            return final_text

        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})

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

            messages.append({"role": "user", "content": tool_results})
            continue

        return f"[Agent stopped unexpectedly: stop_reason={response.stop_reason}]"
