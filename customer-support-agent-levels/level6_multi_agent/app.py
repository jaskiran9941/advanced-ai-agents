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
    Sequential trace diagram — each step is a numbered node connected
    top-to-bottom in execution order. Makes the sequence unambiguous.
    """
    nodes  = []
    edges  = []
    step_n = 0

    def node_id(n):
        return f"s{n}"

    def add_node(label, shape, fill, font="white"):
        nonlocal step_n
        step_n += 1
        nid = node_id(step_n)
        nodes.append(
            f'    {nid} [label="{step_n}. {label}" shape={shape} '
            f'style="filled,rounded" fillcolor="{fill}" fontcolor="{font}"];'
        )
        return nid

    prev = None

    def connect(a, b, label="", color="#666", style="solid"):
        edge = f'    {a} -> {b} [color="{color}" style={style}'
        if label:
            edge += f' label="  {label}  "'
        edge += "];"
        edges.append(edge)

    # ── Walk the steps in order ──────────────────────────────────────────
    prev = add_node("Customer sends ticket", "oval", "#4a9eff")

    for event_type, data in steps:

        if event_type == "routing":
            cur = add_node(
                f"Orchestrator\\nDecides routing\\n({data['input_tokens']}+{data['output_tokens']} tokens)",
                "diamond", "#f9a825", "white"
            )
            connect(prev, cur, "ticket", "#4a9eff")
            prev = cur

        elif event_type == "route_decision":
            specs = ", ".join(data["specialists"])
            cur = add_node(f"Route to:\\n{specs}", "note", "#ffeaa7", "#2d3436")
            connect(prev, cur, "", "#f9a825")
            prev = cur

        elif event_type == "specialist_start":
            agent = data["agent"]
            color = AGENT_COLORS.get(agent, "#888")
            icon  = AGENT_ICONS.get(agent, "🤖")
            cur = add_node(f"{icon} {agent.title()} Agent\\nstarts", "box", color)
            connect(prev, cur, "dispatch", color)
            prev = cur

        elif event_type == "tool_call":
            agent = data["agent"]
            tool  = data["tool"]
            color = AGENT_COLORS.get(agent, "#888")
            icon  = TOOL_ICONS.get(tool, "⚙️")
            # Truncate input for label
            inp   = str(data["input"])[:40] + ("…" if len(str(data["input"])) > 40 else "")
            cur   = add_node(f"{icon} {tool}\\n{inp}", "component", "#f5f6fa", "#2d3436")
            connect(prev, cur, "call", color)
            prev = cur

        elif event_type == "tool_result":
            agent  = data["agent"]
            color  = AGENT_COLORS.get(agent, "#888")
            result = str(data["result"])[:45] + ("…" if len(str(data["result"])) > 45 else "")
            cur    = add_node(f"↩ result\\n{result}", "note", "#dfe6e9", "#2d3436")
            connect(prev, cur, "result", "#aaa", "dashed")
            prev = cur

        elif event_type == "specialist_done":
            agent = data["agent"]
            color = AGENT_COLORS.get(agent, "#888")
            icon  = AGENT_ICONS.get(agent, "🤖")
            cur   = add_node(f"{icon} {agent.title()} done\\nreturns prose to orchestrator", "box", color)
            connect(prev, cur, "", color)
            prev = cur

        elif event_type == "synthesis":
            cur = add_node(
                f"Synthesis\\nCombines all responses\\n({data['input_tokens']}+{data['output_tokens']} tokens)",
                "box", "#6c5ce7"
            )
            connect(prev, cur, "all outputs", "#6c5ce7")
            prev = cur

        elif event_type == "synthesis_skipped":
            cur = add_node("Synthesis skipped\\n(single specialist)", "note", "#dfe6e9", "#2d3436")
            connect(prev, cur, "", "#aaa")
            prev = cur

    # Final
    final = add_node("Response sent to Customer", "oval", "#4a9eff")
    connect(prev, final, "response", "#4a9eff")

    lines = [
        "digraph G {",
        '    rankdir=TB;',
        '    splines=polyline;',
        '    node [fontname="Helvetica" fontsize=10 margin="0.15,0.1" width=2.2];',
        '    edge [fontname="Helvetica" fontsize=9];',
        "",
    ] + nodes + [""] + edges + ["}"]

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


# ── Handoff inspector ─────────────────────────────────────────────────────────
def render_handoffs(query: str, steps: list):
    """
    Sequential list of every handoff in the turn — what was passed and what
    came back at each boundary. This is where gaps become visible:
    - What context did the orchestrator actually give each specialist?
    - What did each tool receive and return?
    - What did each specialist return to the synthesizer?
    - What got lost or invented between steps?
    """
    st.caption("Every handoff in sequence — expand any to see full content")

    handoffs = []

    # 1. Customer → Orchestrator
    handoffs.append({
        "from": "👤 Customer",
        "to":   "🧭 Orchestrator",
        "label": "Original ticket",
        "content": query,
        "gap_hint": None,
    })

    # 2. Routing result
    routing_event = next((s[1] for s in steps if s[0] == "routing"), None)
    if routing_event:
        try:
            routing_data = json.loads(routing_event["raw"])
        except Exception:
            routing_data = routing_event["raw"]
        handoffs.append({
            "from": "🧭 Orchestrator",
            "to":   "🧭 Orchestrator (routing decision)",
            "label": "Routing JSON returned",
            "content": routing_data,
            "gap_hint": "⚠️ Gap check: Does the context given to each specialist include enough to act? Or is it missing key info from the original ticket?",
        })

    # 3. Per-specialist: context passed in + tool calls + result back
    current_agent = None
    for event_type, data in steps:

        if event_type == "specialist_start":
            current_agent = data["agent"]
            icon = AGENT_ICONS.get(current_agent, "🤖")
            handoffs.append({
                "from": "🧭 Orchestrator",
                "to":   f"{icon} {current_agent.title()} Agent",
                "label": f"Context passed to {current_agent}",
                "content": {
                    "ticket":  data.get("ticket", ""),
                    "context": data.get("context", "(none — only raw ticket sent)"),
                },
                "gap_hint": "⚠️ Gap check: Does this agent know what OTHER specialists are doing or have done? No — it only sees what's here.",
            })

        elif event_type == "tool_call":
            icon = TOOL_ICONS.get(data["tool"], "⚙️")
            handoffs.append({
                "from": f"{AGENT_ICONS.get(data['agent'], '🤖')} {data['agent'].title()} Agent",
                "to":   f"{icon} {data['tool']}",
                "label": "Tool input",
                "content": data["input"],
                "gap_hint": None,
            })

        elif event_type == "tool_result":
            icon = TOOL_ICONS.get(data["tool"], "⚙️")
            try:
                result = ast.literal_eval(data["result"])
            except Exception:
                result = data["result"]
            handoffs.append({
                "from": f"{icon} {data['tool']}",
                "to":   f"{AGENT_ICONS.get(data['agent'], '🤖')} {data['agent'].title()} Agent",
                "label": "Tool result",
                "content": result,
                "gap_hint": None,
            })

        elif event_type == "specialist_done":
            icon = AGENT_ICONS.get(data["agent"], "🤖")
            handoffs.append({
                "from": f"{icon} {data['agent'].title()} Agent",
                "to":   "🧭 Orchestrator",
                "label": f"{data['agent'].title()} response (prose string)",
                "content": data["result"],
                "gap_hint": "⚠️ Gap check: This is a prose string. The synthesizer reads it as text — hard facts (amounts, booleans, stock levels) can be softened or misread in the next step.",
            })

        elif event_type == "synthesis":
            specialist_outputs = data.get("specialist_outputs", {})
            handoffs.append({
                "from": "🧭 Orchestrator",
                "to":   "🔄 Synthesis",
                "label": "All specialist outputs passed to synthesis",
                "content": specialist_outputs,
                "gap_hint": "⚠️ Gap check: The synthesizer gets prose strings, not structured data. It can hallucinate actions, soften refusals, or invent promises based on optimistic language patterns.",
            })

    # 4. Final
    handoffs.append({
        "from": "🔄 Synthesis" if any(s[0] == "synthesis" for s in steps) else "🤖 Specialist",
        "to":   "👤 Customer",
        "label": "Final response sent",
        "content": "(see chat panel)",
        "gap_hint": None,
    })

    # ── Render each handoff ──────────────────────────────────────────────
    for i, h in enumerate(handoffs):
        has_gap = h["gap_hint"] is not None
        label_prefix = "⚠️ " if has_gap else f"{i+1}."
        header = f"{label_prefix} {h['from']} → {h['to']}  |  _{h['label']}_"

        with st.expander(header, expanded=False):
            if has_gap:
                st.warning(h["gap_hint"])
            if isinstance(h["content"], (dict, list)):
                st.json(h["content"])
            else:
                st.markdown(f"```\n{str(h['content'])[:800]}\n```")


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
                tab_steps, tab_diagram, tab_handoffs = st.tabs(["📋 Steps", "🗺️ Flow Diagram", "🔗 Handoffs"])

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

                with tab_handoffs:
                    render_handoffs(turn["query"], turn["steps"])


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
