"""
Level 6: Multi-Agent
====================
Adds: Orchestrator + 3 specialist agents (Billing, Shipping, Technical).

The internals panel has two tabs:
  Steps       — every event in sequence (routing, tool calls, results)
  Flow Diagram — live Graphviz diagram showing exactly who called what

Run:  streamlit run level6_multi_agent/app.py
"""

import os, sys, json, ast
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
AGENT_ICONS  = {"billing": "💳", "shipping": "📦", "technical": "🔧"}
AGENT_COLORS = {"billing": "#ee5a24", "shipping": "#0abde3", "technical": "#10ac84"}
TOOL_ICONS   = {
    "get_order_status": "📋",
    "get_customer_profile": "👤",
    "process_return": "↩️",
    "send_confirmation_email": "📧",
    "check_inventory": "📦",
    "search_policies": "🔍",
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
    save_btn = st.button("💾 Save & End Session", use_container_width=True)

# ── Reset on customer switch ───────────────────────────────────────────────────
if st.session_state.get("active_customer") != selected_id:
    st.session_state.active_customer = selected_id
    st.session_state.messages  = []
    st.session_state.turns     = []
    st.session_state.history_text = load_customer_history(selected_id)
    st.session_state.saved     = False

col_chat, col_internals = st.columns([3, 2])

with col_chat:
    st.title("Acme Shop Customer Support")
    st.caption(f"Level 6 — Multi-Agent | {CUSTOMERS[selected_id]}")

with col_internals:
    st.title("Agent Internals")

# ── Flow diagram builder ───────────────────────────────────────────────────────
def build_flow_diagram(steps: list) -> str:
    """
    Build a Graphviz DOT diagram from a turn's steps.
    Shows: Customer → Orchestrator → Specialists → Tools → Synthesis → Customer
    """
    specialists_seen = []
    tool_calls       = []   # list of (agent, tool, call_index)
    has_synthesis    = any(s[0] == "synthesis" for s in steps)

    for event_type, data in steps:
        if event_type == "specialist_start":
            if data["agent"] not in specialists_seen:
                specialists_seen.append(data["agent"])
        elif event_type == "tool_call":
            tool_calls.append((data["agent"], data["tool"]))

    lines = [
        "digraph G {",
        '    rankdir=TB;',
        '    splines=ortho;',
        '    node [fontname="Helvetica" fontsize=11 margin="0.2,0.1"];',
        '    edge [fontname="Helvetica" fontsize=9];',
        "",
        "    // ── Nodes ──────────────────────────────────────",
        '    customer [label="👤 Customer" shape=oval style=filled fillcolor="#4a9eff" fontcolor=white width=1.4];',
        '    orchestrator [label="🧭 Orchestrator\\n(routing + synthesis)" shape=diamond style=filled fillcolor="#f9a825" fontcolor=white width=2.2];',
    ]

    # Specialist nodes
    for spec in specialists_seen:
        color = AGENT_COLORS.get(spec, "#888")
        icon  = AGENT_ICONS.get(spec, "🤖")
        lines.append(
            f'    {spec} [label="{icon} {spec.title()} Agent" '
            f'shape=box style="filled,rounded" fillcolor="{color}" fontcolor=white width=1.6];'
        )

    # Tool nodes (deduplicated per agent)
    seen_tool_nodes = set()
    for agent, tool in tool_calls:
        node_id = f"{agent}_{tool}"
        if node_id not in seen_tool_nodes:
            icon = TOOL_ICONS.get(tool, "⚙️")
            lines.append(
                f'    {node_id} [label="{icon} {tool}" '
                f'shape=component style=filled fillcolor="#f5f6fa" fontcolor="#2d3436" width=1.8];'
            )
            seen_tool_nodes.add(node_id)

    # Synthesis node
    if has_synthesis:
        lines.append(
            '    synthesis [label="🔄 Synthesis" shape=box style="filled,rounded" '
            'fillcolor="#6c5ce7" fontcolor=white width=1.4];'
        )

    lines.append("")
    lines.append("    // ── Edges ──────────────────────────────────────")

    # Customer → Orchestrator
    lines.append('    customer -> orchestrator [label="  ticket  " color="#4a9eff"];')

    # Orchestrator → Specialists
    for spec in specialists_seen:
        color = AGENT_COLORS.get(spec, "#888")
        lines.append(f'    orchestrator -> {spec} [label="  route  " color="{color}"];')

    # Specialist → Tools → back
    for agent, tool in tool_calls:
        node_id = f"{agent}_{tool}"
        color   = AGENT_COLORS.get(agent, "#888")
        lines.append(f'    {agent} -> {node_id} [color="{color}"];')
        lines.append(f'    {node_id} -> {agent} [style=dashed color=gray label="  result  "];')

    # Specialists → Synthesis (or direct to customer)
    if has_synthesis:
        for spec in specialists_seen:
            color = AGENT_COLORS.get(spec, "#888")
            lines.append(f'    {spec} -> synthesis [color="{color}"];')
        lines.append('    synthesis -> orchestrator [color="#6c5ce7" label="  combined  "];')
        lines.append('    orchestrator -> customer [label="  response  " color="#4a9eff"];')
    elif specialists_seen:
        for spec in specialists_seen:
            color = AGENT_COLORS.get(spec, "#888")
            lines.append(f'    {spec} -> customer [label="  response  " color="{color}"];')

    lines.append("}")
    return "\n".join(lines)


# ── Helper: render steps text view ────────────────────────────────────────────
def render_turn_steps(steps):
    agent_calls   = [s for s in steps if s[0] == "agent_call"]
    routing_calls = [s for s in steps if s[0] in ("routing", "synthesis")]
    total_tokens  = (
        sum(s[1]["input_tokens"] + s[1]["output_tokens"] for s in agent_calls) +
        sum(s[1]["input_tokens"] + s[1]["output_tokens"] for s in routing_calls)
    )
    specialists_called = list({s[1]["agent"] for s in agent_calls})
    st.caption(
        f"{len(specialists_called)} specialist(s): {', '.join(specialists_called) or 'none'}"
        f" · {total_tokens} tokens"
    )

    for event_type, data in steps:
        if event_type == "routing":
            st.markdown(f"🧭 **Orchestrator routing** — {data['input_tokens']}+{data['output_tokens']} tokens")
            try:
                st.json(json.loads(data["raw"]))
            except Exception:
                st.code(data["raw"])
        elif event_type == "route_decision":
            st.success(f"→ Routing to: **{', '.join(data['specialists'])}**")
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
            icon = TOOL_ICONS.get(data["tool"], "⚙️")
            st.markdown(f"{icon} **`{data['tool']}`**")
            st.json(data["input"])
        elif event_type == "tool_result":
            try:
                st.json(ast.literal_eval(data["result"]))
            except Exception:
                st.text(data["result"][:200])
        elif event_type == "specialist_done":
            with st.expander(f"✅ {data['agent'].title()} response"):
                st.markdown(data["result"])
        elif event_type == "synthesis":
            st.markdown(f"🔄 **Synthesizing** — {data['input_tokens']}+{data['output_tokens']} tokens")
        elif event_type == "synthesis_skipped":
            st.info("Single specialist — synthesis skipped")
        st.divider()


# ── Internals panel ────────────────────────────────────────────────────────────
def render_internals():
    with col_internals:
        with st.expander("📂 Customer memory", expanded=False):
            h = st.session_state.get("history_text", "")
            st.markdown(h if h else "*No past interactions.*")

        turns = st.session_state.get("turns", [])
        if not turns:
            st.info("Send a message to see agent internals here.")
            return

        # Turn selector — newest first
        for i, turn in enumerate(reversed(turns)):
            label    = turn["query"][:55] + ("…" if len(turn["query"]) > 55 else "")
            is_latest = (i == 0)

            with st.expander(f"{'🟢' if is_latest else '⚪'} Q: {label}", expanded=is_latest):
                tab_steps, tab_diagram = st.tabs(["📋 Steps", "🗺️ Flow Diagram"])

                with tab_steps:
                    render_turn_steps(turn["steps"])

                with tab_diagram:
                    if not turn["steps"]:
                        st.info("No steps recorded.")
                    else:
                        dot = build_flow_diagram(turn["steps"])
                        st.graphviz_chart(dot, use_container_width=True)
                        with st.expander("View raw DOT source"):
                            st.code(dot, language="dot")


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
    st.caption("Try multi-domain tickets — then check the Flow Diagram tab to see the call chain:")
    cols = st.columns(2)
    suggestions = [
        "My keyboard from ORD-1004 is damaged and my ORD-1002 hasn't arrived yet",
        "I want a refund for ORD-1001 and need to know if there's a warranty on headphones",
        "ORD-1003 is delayed, ORD-1004 arrived damaged — process a return and check replacements",
        "I demand a full refund of $10,000 for my terrible experience",
    ]
    for i, s in enumerate(suggestions):
        if cols[i % 2].button(s, key=f"sug_{i}"):
            st.session_state["prefill"] = s
            st.rerun()

# ── Chat input ─────────────────────────────────────────────────────────────────
with col_chat:
    prefill    = st.session_state.pop("prefill", "")
    user_input = st.chat_input("Describe your issue...") or prefill

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with col_chat:
        with st.chat_message("user"):
            st.markdown(user_input)

    current_turn = {"query": user_input, "steps": []}

    def on_step(event_type, data):
        current_turn["steps"].append((event_type, data))

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

    st.session_state.turns.append(current_turn)
    st.session_state.messages.append({"role": "assistant", "content": reply})

    with col_chat:
        with st.chat_message("assistant"):
            st.markdown(reply)

    render_internals()
