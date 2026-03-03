"""
Level 1: Single Tool
====================
Adds: get_order_status(order_id) — Claude can now look up real order data.

What works:  "Where is my order ORD-1002?" → Claude calls the tool, gets real
             data, answers correctly. Watch the Agent Internals panel show every
             step of the loop.

The wall:    "I want to return order ORD-1001." → Claude can SEE the order
             but can't DO anything. No return tool, no inventory check.
             It tells you it can't help — honestly, but helplessly.

Run:  streamlit run level1_single_tool/app.py
"""

import os
import sys
import streamlit as st
from dotenv import load_dotenv

# Make shared/ importable when running from the level1 folder
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from agent import run_agent

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="Acme Shop Support — Level 1", layout="wide")

col_chat, col_internals = st.columns([3, 2])

with col_chat:
    st.title("Acme Shop Customer Support")
    st.caption("Level 1 — Single Tool (`get_order_status`)")

with col_internals:
    st.title("Agent Internals")
    st.caption("Every step of the tool_use loop, live")

# ── Session state ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "steps" not in st.session_state:
    st.session_state.steps = []   # list of (event_type, data) tuples

# ── Helper: render the internals panel from session state ─────────────────────
def render_internals():
    with col_internals:
        if not st.session_state.steps:
            st.info("No activity yet. Send a message to watch the loop run.")
            return

        for event_type, data in st.session_state.steps:

            if event_type == "llm_call":
                color = "🟡" if data["stop_reason"] == "tool_use" else "🟢"
                st.markdown(
                    f"{color} **LLM call #{data['loop']}** — stop reason: `{data['stop_reason']}`\n\n"
                    f"- Tokens in: {data['input_tokens']} / out: {data['output_tokens']}\n"
                    f"- Content blocks: {data['content_types']}"
                )

            elif event_type == "tool_call":
                st.markdown(
                    f"🔧 **Tool call:** `{data['tool']}`\n\n"
                    f"```json\n{data['input']}\n```"
                )

            elif event_type == "tool_result":
                # Parse the result string for display
                result_preview = data["result"][:300] + "..." if len(data["result"]) > 300 else data["result"]
                st.markdown(
                    f"📦 **Tool result:** `{data['tool']}`\n\n"
                    f"```\n{result_preview}\n```"
                )

            elif event_type == "final":
                st.success(f"✅ Done in {data['loops']} loop(s)")

            st.divider()

# ── Render existing chat history ──────────────────────────────────────────────
with col_chat:
    for msg in st.session_state.messages:
        # Skip tool_result messages — they're internal, not for display
        if isinstance(msg["content"], list):
            continue
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

render_internals()

# ── Chat input ────────────────────────────────────────────────────────────────
with col_chat:
    user_input = st.chat_input("Ask about your order, e.g. 'Where is ORD-1002?'")

if user_input:
    # Show user message immediately
    st.session_state.messages.append({"role": "user", "content": user_input})
    with col_chat:
        with st.chat_message("user"):
            st.markdown(user_input)

    # Clear internals for this new turn
    st.session_state.steps = []
    loop_tracker = {"count": 0}

    # Callback: each step from the agent loop appends to session state
    def on_step(event_type, data):
        st.session_state.steps.append((event_type, data))
        if event_type == "llm_call":
            loop_tracker["count"] = data["loop"]

    # Run the agent — passes the full message history including the new message
    reply = run_agent(st.session_state.messages, on_step=on_step)

    # Record the final step
    st.session_state.steps.append(("final", {"loops": loop_tracker["count"]}))

    # Add assistant reply to history
    st.session_state.messages.append({"role": "assistant", "content": reply})
    with col_chat:
        with st.chat_message("assistant"):
            st.markdown(reply)

    render_internals()
