"""
agent.py — Level 4
==================
Same loop as L1-L3. The only change: the system prompt now includes
the customer's interaction history, injected by app.py at session start.

The agent itself doesn't know about SQLite — it just sees history
as text in the system prompt. That's the key design point:
memory is a prompt-engineering problem, not an agent-loop problem.
"""

import os
import anthropic
from tools import TOOL_SCHEMAS, execute_tool


def build_system_prompt(customer_history: str) -> str:
    base = """You are a customer support agent for Acme Shop, a fictional electronics retailer.

You have tools to look up orders, customer profiles, inventory, process returns,
send confirmation emails, and search official policy documents.

Guidelines:
- For policy questions, always call search_policies first — never guess.
- For order questions, use get_order_status.
- Chain tools as needed, send a confirmation email after any completed action.
- Be friendly and specific — use the customer's name, mention order IDs."""

    if customer_history:
        base += f"\n\n{customer_history}\n\nUse this history to personalise your response — acknowledge recurring issues, reference past interactions where relevant."

    return base


def run_agent(messages: list, customer_history: str = "", on_step=None) -> str:
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"), max_retries=5)
    system_prompt = build_system_prompt(customer_history)
    loop_count = 0

    while True:
        loop_count += 1

        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            system=system_prompt,
            tools=TOOL_SCHEMAS,
            messages=messages,
        )

        if on_step:
            on_step("llm_call", {
                "loop": loop_count,
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
