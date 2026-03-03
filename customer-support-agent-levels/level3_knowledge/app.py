"""
Level 3: Knowledge / RAG
========================
Adds: knowledge.py — ChromaDB with Acme Shop policy docs.
      New tool: search_policies(query)

What works:  Policy questions are answered from retrieved docs, not training guesses.
             "Can I return a laptop after 45 days?" → agent fetches the return policy,
             reads the 30-day window, answers accurately.

The wall:    Policy questions: grounded. But ask anything personal:
             "I've complained about late deliveries 3 times — what are you doing about it?"
             → agent has zero memory of past interactions. Knows the rules, not the customer.

First run:   ChromaDB downloads the embedding model (~90MB). Subsequent runs: instant.

Run:  streamlit run level3_knowledge/app.py
"""

import os, sys
import streamlit as st
from dotenv import load_dotenv

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from agent import run_agent

st.set_page_config(page_title="Acme Shop Support — Level 3", layout="wide")

col_chat, col_internals = st.columns([3, 2])

with col_chat:
    st.title("Acme Shop Customer Support")
    st.caption("Level 3 — Knowledge / RAG (`search_policies`)")

with col_internals:
    st.title("Agent Internals")
    st.caption("Watch policy retrieval vs. order lookups side by side")

# ── Session state ──────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "steps" not in st.session_state:
    st.session_state.steps = []

# ── Internals renderer ─────────────────────────────────────────────────────────
def render_internals():
    with col_internals:
        if not st.session_state.steps:
            st.info("No activity yet. Try a policy question to see RAG in action.")
            return

        tool_calls = [s for s in st.session_state.steps if s[0] == "tool_call"]
        llm_calls  = [s for s in st.session_state.steps if s[0] == "llm_call"]
        total_tokens = sum(s[1]["input_tokens"] + s[1]["output_tokens"] for s in llm_calls)

        st.markdown(
            f"**This turn:** {len(llm_calls)} LLM call(s) · "
            f"{len(tool_calls)} tool call(s) · {total_tokens} tokens"
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
                # Highlight policy search differently from order lookups
                if data["tool"] == "search_policies":
                    st.markdown(f"🔍 **`search_policies`** — RAG lookup")
                    st.code(data["input"].get("query", ""), language=None)
                else:
                    st.markdown(f"🔧 **`{data['tool']}`** called with:")
                    st.json(data["input"])

            elif event_type == "tool_result":
                if data["tool"] == "search_policies":
                    import ast
                    try:
                        hits = ast.literal_eval(data["result"])
                        for hit in hits:
                            st.markdown(
                                f"📄 **{hit['title']}** "
                                f"(relevance: {hit['relevance_score']})\n\n"
                                f"> {hit['content'][:200]}..."
                            )
                    except Exception:
                        st.text(data["result"][:300])
                else:
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
    st.caption("Policy questions (RAG) vs. personal history (the wall):")
    cols = st.columns(2)
    suggestions = [
        "Can I return a laptop after 45 days?",
        "What's the warranty on my damaged keyboard from ORD-1004?",
        "I've complained about late deliveries 3 times — what are you doing?",
        "Does free shipping apply to my order ORD-1002?",
    ]
    for i, s in enumerate(suggestions):
        if cols[i % 2].button(s, key=f"sug_{i}"):
            st.session_state["prefill"] = s
            st.rerun()

# ── Chat input ─────────────────────────────────────────────────────────────────
with col_chat:
    prefill = st.session_state.pop("prefill", "")
    user_input = st.chat_input("Ask a policy question or about your order...") or prefill

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
