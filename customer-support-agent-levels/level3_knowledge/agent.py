"""
agent.py — Level 3
==================
Same loop as Levels 1 and 2. Nothing changes here.
The only difference is the system prompt now tells Claude
to search policies instead of relying on training knowledge.
"""

import os
import anthropic
from tools import TOOL_SCHEMAS, execute_tool

SYSTEM_PROMPT = """You are a customer support agent for Acme Shop, a fictional electronics retailer.

You have tools to look up orders, customer profiles, inventory, process returns,
send confirmation emails, and — new this level — search official policy documents.

Important:
- For ANY question about policy (returns, refunds, shipping timelines, warranty, billing),
  call search_policies FIRST. Never answer policy questions from memory — always retrieve
  the actual policy text and base your answer on that.
- For order-specific questions, use get_order_status.
- Chain tools as needed: look up the order, check policy eligibility, then act.
- Always send a confirmation email after completing an action."""


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
            return next(b.text for b in response.content if b.type == "text")

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
