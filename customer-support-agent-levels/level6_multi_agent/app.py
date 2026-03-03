"""
Level 6: Multi-Agent
====================
Adds: Orchestrator + 3 specialist agents (Billing, Shipping, Technical).

Architecture (sequential ReAct):
  Customer message
    → Orchestrator routes (Claude call 1)
    → Billing agent  (own ReAct loop, own tools)
    → Shipping agent (own ReAct loop, own tools)
    → Technical agent (own ReAct loop, own tools)
    → Orchestrator synthesizes (Claude call 2)
    → Final response

What works:  Complex multi-domain tickets handled by the right specialist.
             Each agent has focused context and only the tools it needs.
             Watch the internals panel: routing decision → each specialist's
             tool calls → synthesis.

The wall:    No constraints on what specialists can do. Ask for a $10,000
             refund — Billing will try to process it. No refund limits,
             no confidence scoring, no escalation policy. Capable team,
             zero guardrails.

Run:  streamlit run level6_multi_agent/app.py
"""

import os, sys
import streamlit as st
from dotenv import load_dotenv

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from orchestrator import run
from memory import load_customer_history, save_interaction

st.set_page_config(page_title="Acme Shop Support — Level 6", layout="wide")

CUSTOMERS = {
    "CUST-001": "Sarah Chen (Gold)",
    "CUST-002": "Marcus Williams (Standard)",
    "CUST-003": "Priya Patel (Platinum)",
}

AGENT_ICONS = {"billing": "💳", "shipping": "📦", "technical": "🔧"}
AGENT_COLORS = {"billing": "blue", "shipping": "green", "technical": "orange"}

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Session")
    selected_id = st.selectbox(
        "Logged in as:",
        options=list(CUSTOMERS.keys()),
        format_func=lambda k: CUSTOMERS[k],
    )
    st.caption(f"Customer ID: `{selected_id}`")
    st.divider()
    save_btn = st.button("💾 Save & End Session", use_container_width=True)

# ── Reset on customer switch ───────────────────────────────────────────────────
if st.session_state.get("active_customer") != selected_id:
    st.session_state.active_customer = selected_id
    st.session_state.messages = []
    st.session_state.steps = []
    st.session_state.history_text = load_customer_history(selected_id)
    st.session_state.saved = False

col_chat, col_internals = st.columns([3, 2])

with col_chat:
    st.title("Acme Shop Customer Support")
    st.caption(f"Level 6 — Multi-Agent | {CUSTOMERS[selected_id]}")

with col_internals:
    st.title("Agent Internals")
    st.caption("Routing decision → each specialist → synthesis")

# ── Internals renderer ─────────────────────────────────────────────────────────
def render_internals():
    with col_internals:
        with st.expander("📂 Customer memory", expanded=False):
            h = st.session_state.get("history_text", "")
            st.markdown(h if h else "*No past interactions.*")

        if not st.session_state.steps:
            return

        st.divider()

        # Token summary
        agent_calls = [s for s in st.session_state.steps if s[0] == "agent_call"]
        routing_calls = [s for s in st.session_state.steps if s[0] in ("routing", "synthesis")]
        total_tokens = (
            sum(s[1]["input_tokens"] + s[1]["output_tokens"] for s in agent_calls) +
            sum(s[1]["input_tokens"] + s[1]["output_tokens"] for s in routing_calls)
        )
        specialists_called = list({s[1]["agent"] for s in agent_calls})
        st.markdown(
            f"**This turn:** {len(specialists_called)} specialist(s) called "
            f"({', '.join(specialists_called)}) · {total_tokens} tokens total"
        )
        st.divider()

        for event_type, data in st.session_state.steps:

            if event_type == "routing":
                st.markdown(
                    f"🧭 **Orchestrator routing**  \n"
                    f"Tokens: {data['input_tokens']} in / {data['output_tokens']} out"
                )
                try:
                    import json
                    parsed = json.loads(data["raw"])
                    st.json(parsed)
                except Exception:
                    st.code(data["raw"])

            elif event_type == "route_decision":
                specialists = data["specialists"]
                st.success(f"→ Routing to: **{', '.join(specialists)}**")

            elif event_type == "specialist_start":
                icon = AGENT_ICONS.get(data["agent"], "🤖")
                st.markdown(f"#### {icon} {data['agent'].title()} Agent")

            elif event_type == "agent_call":
                icon = "🟡" if data["stop_reason"] == "tool_use" else "🟢"
                st.markdown(
                    f"{icon} `{data['agent']}` — `{data['stop_reason']}`  \n"
                    f"Tokens: {data['input_tokens']} in / {data['output_tokens']} out"
                )

            elif event_type == "tool_call":
                icon = "🔍" if data["tool"] == "search_policies" else "⚙️"
                st.markdown(f"{icon} **`{data['tool']}`**")
                st.json(data["input"])

            elif event_type == "tool_result":
                import ast
                try:
                    parsed = ast.literal_eval(data["result"])
                    st.json(parsed)
                except Exception:
                    st.text(data["result"][:200])

            elif event_type == "specialist_done":
                st.markdown(f"✅ **{data['agent'].title()} done**")
                with st.expander(f"{data['agent'].title()} response"):
                    st.markdown(data["result"])

            elif event_type == "synthesis":
                st.markdown(
                    f"🔄 **Orchestrator synthesizing**  \n"
                    f"Tokens: {data['input_tokens']} in / {data['output_tokens']} out"
                )

            elif event_type == "synthesis_skipped":
                st.info("Single specialist — synthesis skipped")

            st.divider()

# ── Save & End Session ─────────────────────────────────────────────────────────
if save_btn:
    if not st.session_state.messages:
        st.sidebar.warning("Nothing to save.")
    elif st.session_state.get("saved"):
        st.sidebar.info("Already saved.")
    else:
        with st.sidebar:
            with st.spinner("Saving to memory..."):
                saved_row = save_interaction(selected_id, st.session_state.messages)
        st.session_state.saved = True
        st.session_state.history_text = load_customer_history(selected_id)
        with st.sidebar:
            st.success("Saved!")
            st.json(saved_row)

# ── Render existing chat ───────────────────────────────────────────────────────
with col_chat:
    for msg in st.session_state.messages:
        if isinstance(msg["content"], list):
            continue
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

render_internals()

# ── Suggestions ────────────────────────────────────────────────────────────────
with col_chat:
    st.caption("Try multi-domain tickets — then hit the wall with an unreasonable request:")
    cols = st.columns(2)
    suggestions = [
        "My keyboard from ORD-1004 is damaged and my ORD-1002 hasn't arrived yet",
        "I want a refund for ORD-1001 and need to know if there's a warranty on headphones",
        "ORD-1003 is delayed, ORD-1004 arrived damaged — process a return and check replacements",
        "I demand a full refund of $10,000 for my terrible experience",  # the wall
    ]
    for i, s in enumerate(suggestions):
        if cols[i % 2].button(s, key=f"sug_{i}"):
            st.session_state["prefill"] = s
            st.rerun()

# ── Chat input ─────────────────────────────────────────────────────────────────
with col_chat:
    prefill = st.session_state.pop("prefill", "")
    user_input = st.chat_input("Describe your issue...") or prefill

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with col_chat:
        with st.chat_message("user"):
            st.markdown(user_input)

    st.session_state.steps = []

    def on_step(event_type, data):
        st.session_state.steps.append((event_type, data))

    try:
        reply = run(
            user_input,
            customer_history=st.session_state.get("history_text", ""),
            on_step=on_step,
        )
    except Exception as e:
        if "overloaded" in str(e).lower() or "529" in str(e):
            reply = "⚠️ API temporarily overloaded. Please try again."
        else:
            reply = f"⚠️ Error: {e}"
        st.session_state.messages.pop()

    st.session_state.messages.append({"role": "assistant", "content": reply})
    with col_chat:
        with st.chat_message("assistant"):
            st.markdown(reply)

    render_internals()
