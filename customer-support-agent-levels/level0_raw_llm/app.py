"""
Level 0: Raw LLM
================
Just Claude with a system prompt. No tools. No memory. No data access.

What works:  General questions about policies (from training data).
The wall:    Ask "Where is order #12345?" — Claude will make something up.
             That's confabulation. It has no live data, so it fills the gap with
             plausible-sounding fiction. This is the core problem tools solve.

Run:  streamlit run level0_raw_llm/app.py
"""

import os
import anthropic
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = """You are a customer support agent for Acme Shop, a fictional electronics retailer.

You help customers with questions about their orders, returns, shipping, warranties, and account issues.

Be friendly, concise, and professional. If you don't know something specific to the customer's
account or order, be honest — do not make up order details, tracking numbers, or account information."""

st.set_page_config(page_title="Acme Shop Support — Level 0", layout="wide")

col_chat, col_internals = st.columns([3, 2])

with col_chat:
    st.title("Acme Shop Customer Support")
    st.caption("Level 0 — Raw LLM (no tools, no data)")

with col_internals:
    st.title("Agent Internals")
    st.caption("What the agent is doing under the hood")
    internals_log = st.empty()

# ── Session state ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "internals" not in st.session_state:
    st.session_state.internals = []

# ── Render existing chat history ──────────────────────────────────────────────
with col_chat:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# ── Render internals panel ────────────────────────────────────────────────────
def render_internals():
    with col_internals:
        if not st.session_state.internals:
            internals_log.info("No activity yet. Send a message to see what happens inside.")
        else:
            internals_log.empty()
            with col_internals:
                for entry in st.session_state.internals:
                    st.markdown(entry)

render_internals()

# ── Chat input ────────────────────────────────────────────────────────────────
with col_chat:
    user_input = st.chat_input("Ask me about your order, returns, or anything else...")

if user_input:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with col_chat:
        with st.chat_message("user"):
            st.markdown(user_input)

    # Log to internals
    st.session_state.internals.append(f"**User message received**\n\n> {user_input}")
    st.session_state.internals.append(
        f"**LLM call** → `claude-sonnet-4-6`\n\n"
        f"- System prompt: Acme Shop support agent\n"
        f"- Messages in context: {len(st.session_state.messages)}\n"
        f"- Tools: **none**\n"
        f"- Strategy: single call, no loop needed"
    )

    # Call Claude
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"), max_retries=5)
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=st.session_state.messages,
    )

    reply = response.content[0].text
    usage = response.usage

    # Log response details
    st.session_state.internals.append(
        f"**LLM response received**\n\n"
        f"- Stop reason: `{response.stop_reason}`\n"
        f"- Input tokens: {usage.input_tokens}\n"
        f"- Output tokens: {usage.output_tokens}\n"
        f"- No tool calls (none available)\n\n"
        f"---\n"
        f"*Notice: if you asked about a specific order, Claude answered from training data — "
        f"not your actual order system. That's the wall.*"
    )

    # Add assistant message
    st.session_state.messages.append({"role": "assistant", "content": reply})
    with col_chat:
        with st.chat_message("assistant"):
            st.markdown(reply)

    render_internals()
