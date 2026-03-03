"""
Level 5: Reflection
===================
Adds: A self-critique loop. After every draft response, a second Claude call
checks completeness. If gaps are found, the agent regenerates — up to 3 times.

What works:  Multi-part questions get caught before they reach the customer.
             The internals panel shows every attempt, every critique verdict,
             and exactly what the critic flagged as missing.

The wall:    Every reflection pass costs real LLM calls. A 3-attempt worst case
             is 6 Claude calls for one customer message (3 drafts + 3 critiques).
             This doubles-to-triples latency and cost per turn. And it's still
             one agent — routing to specialists would be more efficient.
             That's what L6 (multi-agent) addresses.

Run:  streamlit run level5_reflection/app.py
"""

import os, sys
import streamlit as st
from dotenv import load_dotenv

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from agent import run_agent, MAX_ATTEMPTS
from memory import load_customer_history, save_interaction

st.set_page_config(page_title="Acme Shop Support — Level 5", layout="wide")

col_chat, col_internals = st.columns([3, 2])

CUSTOMERS = {
    "CUST-001": "Sarah Chen (Gold)",
    "CUST-002": "Marcus Williams (Standard)",
    "CUST-003": "Priya Patel (Platinum)",
}

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
    st.caption("Reflection cap: **3 attempts max** per response.")
    st.caption("After your conversation, save it to memory.")
    save_btn = st.button("💾 Save & End Session", use_container_width=True)

# ── Reset on customer switch ───────────────────────────────────────────────────
if st.session_state.get("active_customer") != selected_id:
    st.session_state.active_customer = selected_id
    st.session_state.messages = []
    st.session_state.steps = []
    st.session_state.history_text = load_customer_history(selected_id)
    st.session_state.saved = False

# ── Headers ────────────────────────────────────────────────────────────────────
with col_chat:
    st.title("Acme Shop Customer Support")
    st.caption(f"Level 5 — Reflection (up to {MAX_ATTEMPTS} passes) | {CUSTOMERS[selected_id]}")

with col_internals:
    st.title("Agent Internals")
    st.caption("Draft → critique → regenerate (if needed) — every pass visible")

# ── Internals renderer ─────────────────────────────────────────────────────────
def render_internals():
    with col_internals:

        with st.expander("📂 Memory loaded at session start", expanded=False):
            history = st.session_state.get("history_text", "")
            st.markdown(history if history else "*No past interactions for this customer.*")

        if not st.session_state.steps:
            return

        st.divider()

        # Token + call summary
        llm_calls      = [s for s in st.session_state.steps if s[0] == "llm_call"]
        critique_calls = [s for s in st.session_state.steps if s[0] == "critique"]
        tool_calls     = [s for s in st.session_state.steps if s[0] == "tool_call"]
        total_tokens   = (
            sum(s[1]["input_tokens"] + s[1]["output_tokens"] for s in llm_calls) +
            sum(s[1]["input_tokens"] + s[1]["output_tokens"] for s in critique_calls)
        )

        st.markdown(
            f"**This turn:** {len(llm_calls)} agent call(s) · "
            f"{len(critique_calls)} critique call(s) · "
            f"{len(tool_calls)} tool call(s) · "
            f"{total_tokens} tokens total"
        )
        st.divider()

        for event_type, data in st.session_state.steps:

            if event_type == "attempt_start":
                st.markdown(f"### Attempt {data['attempt']} of {data['max']}")

            elif event_type == "llm_call":
                icon = "🟡" if data["stop_reason"] == "tool_use" else "🟢"
                st.markdown(
                    f"{icon} **Agent call** — `{data['stop_reason']}`  \n"
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
                    st.text(data["result"][:200])

            elif event_type == "critique":
                import json
                try:
                    verdict = json.loads(data["raw"])
                    complete = verdict.get("complete", False)
                    issues   = verdict.get("issues", "")
                except Exception:
                    complete = False
                    issues   = data["raw"]

                if complete:
                    st.success(f"✅ **Critique:** Complete — no gaps found  \n"
                               f"Tokens: {data['input_tokens']} in / {data['output_tokens']} out")
                else:
                    st.warning(f"⚠️ **Critique:** Gaps found  \n"
                               f"_{issues}_  \n"
                               f"Tokens: {data['input_tokens']} in / {data['output_tokens']} out")

            elif event_type == "reflection_retry":
                st.info(f"🔄 **Regenerating** (attempt {data['attempt']})  \n"
                        f"Critic flagged: _{data['issues']}_")

            elif event_type == "reflection_done":
                result = data["result"]
                if result == "complete":
                    st.success(f"✅ **Done** — passed critique on attempt {data['attempt']}")
                else:
                    st.warning(f"⚠️ **Done** — reached max attempts ({MAX_ATTEMPTS}), returning best draft")

            st.divider()

# ── Save & End Session ─────────────────────────────────────────────────────────
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
        st.session_state.history_text = load_customer_history(selected_id)
        with st.sidebar:
            st.success("Saved!")
            st.json(saved_row)

# ── Render existing chat ───────────────────────────────────────────────────────
with col_chat:
    for msg in st.session_state.messages:
        if isinstance(msg["content"], list):
            continue
        if isinstance(msg["content"], str) and msg["content"].startswith("[Quality review"):
            continue   # hide internal critique-feedback messages
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

render_internals()

# ── Suggestions ────────────────────────────────────────────────────────────────
with col_chat:
    st.caption("Try multi-part questions — watch the critic catch gaps before the response is sent:")
    cols = st.columns(2)
    suggestions = [
        "My order ORD-1004 arrived damaged and I also want to know the warranty policy",
        "I need a refund for ORD-1001 AND want to know if I can return after 45 days AND check if the headphones are in stock",
        "Where is ORD-1002 and what's your shipping policy for delays?",
        "Process a return for ORD-1001 and send me a confirmation",
    ]
    for i, s in enumerate(suggestions):
        if cols[i % 2].button(s, key=f"sug_{i}"):
            st.session_state["prefill"] = s
            st.rerun()

# ── Chat input ─────────────────────────────────────────────────────────────────
with col_chat:
    prefill = st.session_state.pop("prefill", "")
    user_input = st.chat_input("Ask anything — the agent will critique itself before responding...") or prefill

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with col_chat:
        with st.chat_message("user"):
            st.markdown(user_input)

    st.session_state.steps = []

    def on_step(event_type, data):
        st.session_state.steps.append((event_type, data))

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

    st.session_state.messages.append({"role": "assistant", "content": reply})
    with col_chat:
        with st.chat_message("assistant"):
            st.markdown(reply)

    render_internals()
