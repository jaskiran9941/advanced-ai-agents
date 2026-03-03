"""
Level 4: Learning / Memory
===========================
Adds: memory.py — SQLite customer interaction history.

Flow:
  Session start → load this customer's past interactions from SQLite
               → inject as text into the system prompt
  Session end  → click "Save & End Session"
               → Claude extracts structured fields from the conversation
               → saves one row to SQLite
  Next session → pick the same customer → agent greets them with their history

What works:  "I see you've had a delivery issue before — let me prioritise this."
             The agent knows the customer across sessions, not just within them.

The wall:    Try a complex multi-part ticket:
             "My order arrived damaged, the replacement was also wrong,
              AND my account email is broken."
             One agent, one context window — it handles all three but loses
             track of sub-problems as the conversation gets longer.
             That single-agent overload is what L5 (reflection) starts to fix.

Run:  streamlit run level4_learning/app.py
"""

import os, sys
import streamlit as st
from dotenv import load_dotenv

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from agent import run_agent
from memory import load_customer_history, save_interaction

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Acme Shop Support — Level 4", layout="wide")

col_chat, col_internals = st.columns([3, 2])

# ── Sidebar: customer selector ─────────────────────────────────────────────────
CUSTOMERS = {
    "CUST-001": "Sarah Chen (Gold)",
    "CUST-002": "Marcus Williams (Standard)",
    "CUST-003": "Priya Patel (Platinum)",
}

with st.sidebar:
    st.header("Session")
    selected_id = st.selectbox(
        "Logged in as:",
        options=list(CUSTOMERS.keys()),
        format_func=lambda k: CUSTOMERS[k],
    )

    st.caption(f"Customer ID: `{selected_id}`")
    st.divider()
    st.caption("After your conversation, click below to save it to memory.")
    save_btn = st.button("💾 Save & End Session", use_container_width=True)

# ── Reset state when customer changes ─────────────────────────────────────────
if st.session_state.get("active_customer") != selected_id:
    st.session_state.active_customer = selected_id
    st.session_state.messages = []
    st.session_state.steps = []
    st.session_state.history_text = load_customer_history(selected_id)
    st.session_state.saved = False

# ── Headers ────────────────────────────────────────────────────────────────────
with col_chat:
    st.title("Acme Shop Customer Support")
    st.caption(f"Level 4 — Memory | {CUSTOMERS[selected_id]}")

with col_internals:
    st.title("Agent Internals")
    st.caption("Memory injected at session start + tool calls this turn")

# ── Internals renderer ─────────────────────────────────────────────────────────
def render_internals():
    with col_internals:

        # Always show what memory was loaded
        with st.expander("📂 Memory loaded at session start", expanded=True):
            history = st.session_state.get("history_text", "")
            if history:
                st.markdown(history)
            else:
                st.info("No past interactions found for this customer.")

        if not st.session_state.steps:
            return

        st.divider()
        tool_calls = [s for s in st.session_state.steps if s[0] == "tool_call"]
        llm_calls  = [s for s in st.session_state.steps if s[0] == "llm_call"]
        total_tokens = sum(s[1]["input_tokens"] + s[1]["output_tokens"] for s in llm_calls)

        st.markdown(
            f"**This turn:** {len(llm_calls)} LLM call(s) · "
            f"{len(tool_calls)} tool call(s) · {total_tokens} tokens"
        )

        for event_type, data in st.session_state.steps:
            if event_type == "llm_call":
                icon = "🟡" if data["stop_reason"] == "tool_use" else "🟢"
                st.markdown(
                    f"{icon} **LLM call #{data['loop']}** — `{data['stop_reason']}`  \n"
                    f"Tokens: {data['input_tokens']} in / {data['output_tokens']} out"
                )
            elif event_type == "tool_call":
                icon = "🔍" if data["tool"] == "search_policies" else "🔧"
                st.markdown(f"{icon} **`{data['tool']}`**")
                st.json(data["input"])
            elif event_type == "tool_result":
                import ast
                try:
                    parsed = ast.literal_eval(data["result"])
                    st.markdown(f"📦 **`{data['tool']}`** returned:")
                    st.json(parsed)
                except Exception:
                    st.text(data["result"][:300])
            elif event_type == "final":
                st.success(f"✅ Done in {data['loops']} loop(s)")
            st.divider()

# ── Handle Save & End Session ──────────────────────────────────────────────────
if save_btn:
    if not st.session_state.messages:
        st.sidebar.warning("Nothing to save — have a conversation first.")
    elif st.session_state.get("saved"):
        st.sidebar.info("Already saved.")
    else:
        with st.sidebar:
            with st.spinner("Extracting structured memory..."):
                saved_row = save_interaction(selected_id, st.session_state.messages)
        st.session_state.saved = True
        # Refresh the history text so it shows on next render
        st.session_state.history_text = load_customer_history(selected_id)
        with st.sidebar:
            st.success("Saved!")
            st.json(saved_row)

# ── Render chat history ────────────────────────────────────────────────────────
with col_chat:
    for msg in st.session_state.messages:
        if isinstance(msg["content"], list):
            continue
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

render_internals()

# ── Suggested prompts ──────────────────────────────────────────────────────────
with col_chat:
    st.caption("Try a conversation, save it, switch customers, come back — agent remembers:")
    cols = st.columns(2)
    suggestions = [
        "I want to return my damaged keyboard from ORD-1004",
        "Where is my order ORD-1002?",
        "My order arrived damaged, the replacement was wrong, AND my account email is broken",  # the wall
        "Can I return after 45 days?",
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

    try:
        reply = run_agent(
            st.session_state.messages,
            customer_history=st.session_state.get("history_text", ""),
            on_step=on_step,
        )
    except Exception as e:
        if "overloaded" in str(e).lower() or "529" in str(e):
            reply = "⚠️ The AI API is temporarily overloaded. Please try again in a few seconds."
        else:
            reply = f"⚠️ Unexpected error: {e}"
        st.session_state.messages.pop()

    st.session_state.steps.append(("final", {"loops": loop_tracker["count"]}))
    st.session_state.messages.append({"role": "assistant", "content": reply})

    with col_chat:
        with st.chat_message("assistant"):
            st.markdown(reply)

    render_internals()
