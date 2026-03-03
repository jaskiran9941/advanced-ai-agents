"""
Level 2: Multi-Tool
===================
Adds: process_return, check_inventory, send_confirmation_email, get_customer_profile

What works:  Full end-to-end support flow in one conversation.
             Claude chains 3-5 tools without being told the order.
             Watch the internals panel — implicit planning made visible.

The wall:    Ask any policy question: "Can I return after 45 days?" or "What's the warranty?"
             Claude has no access to Acme's actual policy docs — it improvises an answer
             from training data. It might be plausible, but it's a guess. It's not Acme's
             real policy. That's the hallucination risk L3 fixes.

Run:  streamlit run level2_multi_tool/app.py
"""

import os, sys
import streamlit as st
from dotenv import load_dotenv

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from agent import run_agent

st.set_page_config(page_title="Acme Shop Support — Level 2", layout="wide")

col_chat, col_internals = st.columns([3, 2])

with col_chat:
    st.title("Acme Shop Customer Support")
    st.caption("Level 2 — Multi-Tool (implicit planning)")

with col_internals:
    st.title("Agent Internals")
    st.caption("Watch implicit planning — and notice policy answers are guesses")

# ── Session state ──────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "steps" not in st.session_state:
    st.session_state.steps = []
if "total_loops" not in st.session_state:
    st.session_state.total_loops = 0

# ── Internals renderer ─────────────────────────────────────────────────────────
def render_internals():
    with col_internals:
        if not st.session_state.steps:
            st.info("No activity yet. Try: \"I want to return order ORD-1001\"")
            return

        # Summary bar at the top
        tool_calls = [s for s in st.session_state.steps if s[0] == "tool_call"]
        llm_calls  = [s for s in st.session_state.steps if s[0] == "llm_call"]
        total_in   = sum(s[1]["input_tokens"]  for s in llm_calls)
        total_out  = sum(s[1]["output_tokens"] for s in llm_calls)

        st.markdown(
            f"**This turn:** {len(llm_calls)} LLM call(s) · "
            f"{len(tool_calls)} tool call(s) · "
            f"{total_in + total_out} tokens total"
        )
        st.divider()

        for event_type, data in st.session_state.steps:

            if event_type == "llm_call":
                icon = "🟡" if data["stop_reason"] == "tool_use" else "🟢"
                st.markdown(
                    f"{icon} **LLM call #{data['loop']}** — `{data['stop_reason']}`  \n"
                    f"Tokens: {data['input_tokens']} in / {data['output_tokens']} out"
                )

            elif event_type == "tool_call":
                st.markdown(f"🔧 **`{data['tool']}`** called with:")
                st.json(data["input"])

            elif event_type == "tool_result":
                import ast
                try:
                    parsed = ast.literal_eval(data["result"])
                    preview = parsed
                except Exception:
                    preview = data["result"][:300]
                st.markdown(f"📦 **`{data['tool']}`** returned:")
                st.json(preview)

            elif event_type == "final":
                st.success(f"✅ Done in {data['loops']} loop(s)")

            st.divider()

# ── Render existing chat ───────────────────────────────────────────────────────
with col_chat:
    for msg in st.session_state.messages:
        if isinstance(msg["content"], list):
            continue
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

render_internals()

# ── Suggested prompts ──────────────────────────────────────────────────────────
with col_chat:
    st.caption("Try the tool chain — then ask a policy question to hit the wall:")
    cols = st.columns(2)
    suggestions = [
        "I want to return order ORD-1001",
        "My order ORD-1004 arrived damaged, can I get a replacement?",
        "Can I return my headphones after 45 days?",   # the wall — Claude will guess
        "What's the warranty if my keyboard stops working?",  # the wall — Claude will guess
    ]
    for i, s in enumerate(suggestions):
        if cols[i % 2].button(s, key=f"sug_{i}"):
            st.session_state["prefill"] = s
            st.rerun()

# ── Chat input ─────────────────────────────────────────────────────────────────
with col_chat:
    prefill = st.session_state.pop("prefill", "")
    user_input = st.chat_input("Ask about your order...") or prefill

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with col_chat:
        with st.chat_message("user"):
            st.markdown(user_input)

    st.session_state.steps = []
    loop_tracker = {"count": 0}

    def on_step(event_type, data):
        st.session_state.steps.append((event_type, data))
        if event_type == "llm_call":
            loop_tracker["count"] = data["loop"]

    reply = run_agent(st.session_state.messages, on_step=on_step)
    st.session_state.steps.append(("final", {"loops": loop_tracker["count"]}))

    st.session_state.messages.append({"role": "assistant", "content": reply})
    with col_chat:
        with st.chat_message("assistant"):
            st.markdown(reply)

    render_internals()
