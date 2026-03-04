"""
Level 7: LangGraph Orchestration
==================================
Rebuilds L6 in LangGraph. Adds genuine value over L6:
  1. Shared typed state  — agents write floats/booleans, not prose
  2. Human-in-the-loop  — graph pauses when refund > $200, waits for approval
  3. Conditional routing — graph decides next node from state, not hardcoded order
  4. Replan on rejection — billing offers alternative after human rejects

The wall: framework adds real power but hides internals. When something
breaks, the error is inside LangGraph, not your code.

Run:  streamlit run level7_langgraph/app.py
"""

import os, sys, re, json, ast
import streamlit as st
from dotenv import load_dotenv

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from graph import graph
from state import APPROVAL_THRESHOLD, SupportState
from memory import load_customer_history, save_interaction

st.set_page_config(page_title="Acme Shop Support — Level 7", layout="wide")

CUSTOMERS = {
    "CUST-001": "Sarah Chen (Gold)",
    "CUST-002": "Marcus Williams (Standard)",
    "CUST-003": "Priya Patel (Platinum)",
}
AGENT_ICONS  = {"billing": "💳", "shipping": "📦", "technical": "🔧"}
AGENT_COLORS = {"billing": "#ee5a24", "shipping": "#0abde3", "technical": "#10ac84"}
TOOL_ICONS   = {
    "get_order_status": "📋", "get_customer_profile": "👤",
    "process_return": "↩️", "send_confirmation_email": "📧",
    "check_inventory": "📦", "search_policies": "🔍",
}


def md(text: str):
    safe = re.sub(r'\$(\d)', r'\\$\1', str(text))
    st.markdown(safe)


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Session")
    selected_id = st.selectbox(
        "Logged in as:",
        options=list(CUSTOMERS.keys()),
        format_func=lambda k: CUSTOMERS[k],
    )
    st.caption(f"Customer ID: `{selected_id}`")
    st.caption(f"Auto-approval limit: **${APPROVAL_THRESHOLD:.0f}**")
    st.divider()
    save_btn = st.button("💾 Save & End Session", use_container_width=True)

# ── Reset on customer switch ───────────────────────────────────────────────────
if st.session_state.get("active_customer") != selected_id:
    st.session_state.active_customer   = selected_id
    st.session_state.messages          = []
    st.session_state.turns             = []
    st.session_state.history_text      = load_customer_history(selected_id)
    st.session_state.saved             = False
    st.session_state.pending_approval  = None   # paused graph state
    st.session_state.thread_id         = f"{selected_id}-{id(selected_id)}"

col_chat, col_internals = st.columns([3, 2])

with col_chat:
    st.title("Acme Shop Customer Support")
    st.caption(f"Level 7 — LangGraph + Human-in-the-loop | {CUSTOMERS[selected_id]}")

with col_internals:
    st.title("Agent Internals")
    st.caption(f"Shared state · Conditional routing · Human approval gate (>${APPROVAL_THRESHOLD:.0f})")


# ── Internals helpers (reused from L6) ────────────────────────────────────────
def render_turn_steps(steps):
    agent_calls   = [s for s in steps if s[0] == "agent_call"]
    routing_calls = [s for s in steps if s[0] in ("routing", "synthesis")]
    total_tokens  = (
        sum(s[1]["input_tokens"] + s[1]["output_tokens"] for s in agent_calls) +
        sum(s[1]["input_tokens"] + s[1]["output_tokens"] for s in routing_calls)
    )
    specialists_called = list({s[1]["agent"] for s in agent_calls})
    st.caption(f"{len(specialists_called)} specialist(s): {', '.join(specialists_called) or 'none'} · {total_tokens} tokens")

    for event_type, data in steps:
        if event_type == "routing":
            st.markdown(f"🧭 **Router** — {data['input_tokens']}+{data['output_tokens']} tokens")
            try: st.json(json.loads(data["raw"]))
            except: st.code(data["raw"])
        elif event_type == "route_decision":
            st.success(f"→ Routing to: **{', '.join(data['specialists'])}**")
        elif event_type == "specialist_start":
            icon = AGENT_ICONS.get(data["agent"], "🤖")
            st.markdown(f"#### {icon} {data['agent'].title()} Agent")
        elif event_type == "agent_call":
            icon = "🟡" if data["stop_reason"] == "tool_use" else "🟢"
            st.markdown(f"{icon} `{data['agent']}` — `{data['stop_reason']}`  \nTokens: {data['input_tokens']} in / {data['output_tokens']} out")
        elif event_type == "tool_call":
            st.markdown(f"{TOOL_ICONS.get(data['tool'], '⚙️')} **`{data['tool']}`**")
            st.json(data["input"])
        elif event_type == "tool_result":
            try: st.json(ast.literal_eval(data["result"]))
            except: st.text(data["result"][:200])
        elif event_type == "specialist_done":
            with st.expander(f"✅ {data['agent'].title()} response"):
                md(data["result"])
        elif event_type == "approval_gate":
            st.warning(f"⏸️ **Graph paused** — awaiting human approval  \n"
                       f"Refund: **${data['amount']:.2f}** (limit: ${APPROVAL_THRESHOLD:.0f})")
        elif event_type == "billing_replan":
            st.info(f"🔄 **Billing replanning** — rejection reason: _{data.get('reason', '')}_")
        elif event_type == "synthesis":
            st.markdown(f"🔄 **Synthesizer** — {data['input_tokens']}+{data['output_tokens']} tokens")
            # Show the structured state facts that went in
            outputs = data.get("specialist_outputs", {})
            if outputs:
                with st.expander("Structured state passed to synthesizer"):
                    st.json(outputs)
        st.divider()


def render_internals():
    with col_internals:
        with st.expander("📂 Customer memory", expanded=False):
            h = st.session_state.get("history_text", "")
            st.markdown(h if h else "*No past interactions.*")

        # Show shared state panel if approval is pending
        pending = st.session_state.get("pending_approval")
        if pending:
            with st.expander("🔍 Shared state at pause point", expanded=True):
                display_state = {k: v for k, v in pending.items()
                                 if k in ("refund_amount", "return_processed", "approval_required",
                                          "approval_reason", "replacement_in_stock", "specialists")}
                st.json(display_state)

        turns = st.session_state.get("turns", [])
        if not turns:
            st.info("Send a message to see agent internals here.")
            return

        for i, turn in enumerate(reversed(turns)):
            label = turn["query"][:55] + ("…" if len(turn["query"]) > 55 else "")
            with st.expander(f"{'🟢' if i == 0 else '⚪'} Q: {label}", expanded=(i == 0)):
                tab_steps, tab_state = st.tabs(["📋 Steps", "📊 State"])
                with tab_steps:
                    render_turn_steps(turn["steps"])
                with tab_state:
                    if turn.get("final_state"):
                        st.caption("Shared state after this turn completed:")
                        # Show only interesting fields
                        display = {k: v for k, v in turn["final_state"].items()
                                   if v not in (None, "", [], False, 0, 0.0)
                                   and k not in ("ticket", "customer_history", "billing_result",
                                                 "shipping_result", "technical_result", "final_response")}
                        st.json(display)
                    else:
                        st.info("State not yet available.")


# ── Human approval UI ──────────────────────────────────────────────────────────
def render_approval_gate():
    pending = st.session_state.get("pending_approval")
    if not pending:
        return

    refund = pending.get("refund_amount", 0)
    reason = pending.get("approval_reason", "")

    with col_chat:
        with st.container(border=True):
            st.warning(f"⏸️ **Graph paused — Human approval required**")
            st.markdown(f"**Refund amount:** ${refund:.2f}  \n**Reason:** {reason}")
            st.markdown("The billing agent wants to process this refund. Approve or reject below.")

            col_a, col_r = st.columns(2)
            approve_btn = col_a.button("✅ Approve refund", use_container_width=True, type="primary")
            reject_btn  = col_r.button("❌ Reject — offer alternative", use_container_width=True)

            if approve_btn or reject_btn:
                decision = "approved" if approve_btn else "rejected"
                rejection_reason = ""
                if reject_btn:
                    rejection_reason = f"Refund of ${refund:.2f} exceeds policy limit. Offer store credit or partial refund up to $200."

                # Resume the graph with human decision
                thread_id = st.session_state.get("thread_id", "default")
                current_turn = st.session_state.turns[-1] if st.session_state.turns else {"query": "", "steps": []}

                def on_step(event_type, data):
                    current_turn["steps"].append((event_type, data))

                config = {"configurable": {"thread_id": thread_id, "on_step": on_step}}

                # Update state with human decision, then resume
                graph.update_state(config, {"human_decision": decision, "rejection_reason": rejection_reason})

                final_state = None
                for event in graph.stream(None, config=config, stream_mode="values"):
                    final_state = event

                st.session_state.pending_approval = None
                if final_state:
                    reply = final_state.get("final_response", "")
                    current_turn["final_state"] = dict(final_state)
                    if reply:
                        st.session_state.messages.append({"role": "assistant", "content": reply})
                st.rerun()


# ── Save & End Session ─────────────────────────────────────────────────────────
if save_btn:
    if not st.session_state.messages:
        st.sidebar.warning("Nothing to save.")
    elif st.session_state.get("saved"):
        st.sidebar.info("Already saved.")
    else:
        with st.sidebar:
            with st.spinner("Saving..."):
                saved = save_interaction(selected_id, st.session_state.messages)
        st.session_state.saved = True
        st.session_state.history_text = load_customer_history(selected_id)
        with st.sidebar:
            st.success("Saved!")
            st.json(saved)

# ── Render chat ────────────────────────────────────────────────────────────────
with col_chat:
    for msg in st.session_state.messages:
        if isinstance(msg["content"], list):
            continue
        with st.chat_message(msg["role"]):
            md(msg["content"])

render_approval_gate()
render_internals()

# ── Suggestions ────────────────────────────────────────────────────────────────
with col_chat:
    st.caption("Try a large refund to trigger the approval gate — or a normal ticket to compare with L6:")
    cols = st.columns(2)
    suggestions = [
        "I want to return my damaged keyboard from ORD-1004 — it cost $149",
        "My ORD-1002 hasn't arrived and I want a full refund plus $500 compensation",
        "ORD-1003 is delayed, ORD-1004 arrived damaged — return and replacement please",
        "I demand a $10,000 refund for terrible service",
    ]
    for i, s in enumerate(suggestions):
        if cols[i % 2].button(s, key=f"sug_{i}"):
            st.session_state["prefill"] = s
            st.rerun()

# ── Chat input ─────────────────────────────────────────────────────────────────
with col_chat:
    prefill    = st.session_state.pop("prefill", "")
    user_input = st.chat_input("Describe your issue...") or prefill

if user_input and not st.session_state.get("pending_approval"):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with col_chat:
        with st.chat_message("user"):
            md(user_input)

    current_turn = {"query": user_input, "steps": [], "final_state": None}
    thread_id    = st.session_state.get("thread_id", "default")

    def on_step(event_type, data):
        current_turn["steps"].append((event_type, data))

    config = {"configurable": {"thread_id": thread_id, "on_step": on_step}}
    initial_state: SupportState = {
        "ticket":           user_input,
        "customer_history": st.session_state.get("history_text", ""),
        "specialists": [], "billing_context": "", "shipping_context": "", "technical_context": "",
        "billing_result": "", "shipping_result": "", "technical_result": "",
        "refund_amount": 0.0, "return_processed": False,
        "approval_required": False, "approval_reason": "",
        "human_decision": None, "rejection_reason": None,
        "replacement_in_stock": False, "replacement_product_id": "",
        "final_response": "",
    }

    try:
        final_state = None
        for event in graph.stream(initial_state, config=config, stream_mode="values"):
            final_state = event

        if final_state and final_state.get("approval_required") and not final_state.get("human_decision"):
            # Graph paused — waiting for human
            st.session_state.pending_approval = dict(final_state)
            current_turn["steps"].append(("approval_gate", {"amount": final_state.get("refund_amount", 0)}))
            st.session_state.turns.append(current_turn)
            with col_chat:
                st.info("⏸️ Processing paused — approval required. See the gate above.")
        else:
            reply = final_state.get("final_response", "") if final_state else ""
            current_turn["final_state"] = dict(final_state) if final_state else {}
            st.session_state.turns.append(current_turn)
            if reply:
                st.session_state.messages.append({"role": "assistant", "content": reply})
                with col_chat:
                    with st.chat_message("assistant"):
                        md(reply)

    except Exception as e:
        if "overloaded" in str(e).lower() or "529" in str(e):
            reply = "⚠️ API temporarily overloaded. Please try again."
        else:
            reply = f"⚠️ Error: {e}"
        st.session_state.messages.pop()
        with col_chat:
            st.error(reply)

    render_internals()
