"""
graph.py — Level 7
==================
The LangGraph workflow. This is what replaces orchestrator.py from L6.

Nodes:     router, billing, shipping, technical, human_approval,
           billing_replan, synthesizer
Edges:     conditional — graph routes based on state values, not hardcoded order

Key concepts:
  1. Shared state  — every node reads/writes SupportState (TypedDict)
  2. Conditional edges — after billing, check approval_required:
       True  → interrupt graph, wait for human decision
       False → continue to next specialist or synthesizer
  3. interrupt_before — LangGraph pauses execution at human_approval node
       The graph is serialised to a MemorySaver checkpoint.
       app.py reads the paused state, shows the approval UI, then resumes.
  4. After rejection  → billing_replan node offers alternative
     After approval   → continue normally to synthesizer

Comparison with L6:
  L6: orchestrator calls specialists sequentially, passes strings manually
  L7: graph executes nodes, all state flows automatically, human gate is native
"""

import os
import json
import anthropic
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.runnables import RunnableConfig

from state import SupportState, APPROVAL_THRESHOLD
from agents import billing, shipping, technical

# ── Routing node ───────────────────────────────────────────────────────────────
ROUTING_SYSTEM = """You are a support team manager. Read the customer ticket and decide
which specialists are needed: billing, shipping, technical (or any combination).

Return ONLY JSON:
{
  "specialists": ["billing"],
  "billing_context": "...",
  "shipping_context": "...",
  "technical_context": "..."
}"""

def router_node(state: SupportState, config: RunnableConfig) -> dict:
    on_step = config.get("configurable", {}).get("on_step")
    client  = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"), max_retries=5)

    full_ticket = state["ticket"]
    if state.get("customer_history"):
        full_ticket = f"{state['customer_history']}\n\nCustomer: {full_ticket}"

    response = client.messages.create(
        model="claude-sonnet-4-6", max_tokens=512,
        system=ROUTING_SYSTEM,
        messages=[{"role": "user", "content": full_ticket}],
    )
    raw = response.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"): raw = raw[4:]
        raw = raw.strip()

    if on_step:
        on_step("routing", {"input_tokens": response.usage.input_tokens,
                            "output_tokens": response.usage.output_tokens, "raw": raw})
    try:
        routing = json.loads(raw)
    except Exception:
        routing = {"specialists": ["billing", "shipping", "technical"]}

    if on_step:
        on_step("route_decision", {"specialists": routing.get("specialists", [])})

    return {
        "specialists":        routing.get("specialists", []),
        "billing_context":    routing.get("billing_context", ""),
        "shipping_context":   routing.get("shipping_context", ""),
        "technical_context":  routing.get("technical_context", ""),
        "approval_required":  False,
        "human_decision":     None,
        "billing_result":     "",
        "shipping_result":    "",
        "technical_result":   "",
        "refund_amount":      0.0,
        "return_processed":   False,
        "replacement_in_stock": False,
        "replacement_product_id": "",
        "final_response":     "",
    }

# ── Specialist nodes ───────────────────────────────────────────────────────────
def billing_node(state: SupportState, config: RunnableConfig) -> dict:
    on_step = config.get("configurable", {}).get("on_step")
    if "billing" not in state.get("specialists", []):
        return {}
    if on_step: on_step("specialist_start", {"agent": "billing",
        "ticket": state["ticket"], "context": state.get("billing_context", "")})
    result = billing.run(state, on_step=on_step)
    if on_step: on_step("specialist_done", {"agent": "billing", "result": result.get("billing_result", "")})
    return result

def shipping_node(state: SupportState, config: RunnableConfig) -> dict:
    on_step = config.get("configurable", {}).get("on_step")
    if "shipping" not in state.get("specialists", []):
        return {}
    if on_step: on_step("specialist_start", {"agent": "shipping",
        "ticket": state["ticket"], "context": state.get("shipping_context", "")})
    result = shipping.run(state, on_step=on_step)
    if on_step: on_step("specialist_done", {"agent": "shipping", "result": result.get("shipping_result", "")})
    return result

def technical_node(state: SupportState, config: RunnableConfig) -> dict:
    on_step = config.get("configurable", {}).get("on_step")
    if "technical" not in state.get("specialists", []):
        return {}
    if on_step: on_step("specialist_start", {"agent": "technical",
        "ticket": state["ticket"], "context": state.get("technical_context", "")})
    result = technical.run(state, on_step=on_step)
    if on_step: on_step("specialist_done", {"agent": "technical", "result": result.get("technical_result", "")})
    return result

# ── Human approval node (graph pauses here) ────────────────────────────────────
def human_approval_node(state: SupportState, config: RunnableConfig) -> dict:
    """
    This node does nothing — it's a pause point.
    LangGraph interrupts BEFORE this node, serialises state to MemorySaver,
    and waits. app.py reads the paused state, shows the approval UI,
    then calls graph.invoke() again with human_decision set.
    """
    return {}

# ── Billing replan node (after rejection) ─────────────────────────────────────
def billing_replan_node(state: SupportState, config: RunnableConfig) -> dict:
    on_step = config.get("configurable", {}).get("on_step")
    if on_step: on_step("billing_replan", {"reason": state.get("rejection_reason", "")})
    return billing.run_after_rejection(state, on_step=on_step)

# ── Synthesis node ─────────────────────────────────────────────────────────────
SYNTHESIS_SYSTEM = """You are a customer support team manager at Acme Shop.
Combine specialist responses into a single friendly, specific reply to the customer.
Do not mention internal specialist names. Be direct — include order IDs, amounts, dates."""

def synthesizer_node(state: SupportState, config: RunnableConfig) -> dict:
    on_step   = config.get("configurable", {}).get("on_step")
    client    = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"), max_retries=5)
    parts     = [f"Customer ticket:\n{state['ticket']}"]
    specialists = state.get("specialists", [])

    # Inject structured state values so synthesis has hard facts, not just prose
    state_summary = []
    if state.get("refund_amount", 0) > 0:
        state_summary.append(f"Refund amount: ${state['refund_amount']:.2f}")
    if state.get("return_processed"):
        state_summary.append("Return: processed successfully")
    if state.get("replacement_in_stock") is not None:
        stock = "IN STOCK" if state.get("replacement_in_stock") else "OUT OF STOCK"
        pid = state.get("replacement_product_id", "")
        state_summary.append(f"Replacement {pid}: {stock}")
    if state.get("human_decision"):
        state_summary.append(f"Refund approval: {state['human_decision'].upper()}")

    if state_summary:
        parts.append("Verified facts (use these exactly, do not reinterpret):\n" + "\n".join(state_summary))

    for name in specialists:
        result = state.get(f"{name}_result", "")
        if result:
            parts.append(f"{name.upper()} SPECIALIST:\n{result}")

    combined  = "\n\n---\n\n".join(parts)
    response  = client.messages.create(
        model="claude-sonnet-4-6", max_tokens=1024,
        system=SYNTHESIS_SYSTEM,
        messages=[{"role": "user", "content": combined}],
    )

    if on_step:
        on_step("synthesis", {"input_tokens": response.usage.input_tokens,
                              "output_tokens": response.usage.output_tokens,
                              "specialist_outputs": {
                                  n: state.get(f"{n}_result", "") for n in specialists
                              }})

    return {"final_response": response.content[0].text}

# ── Conditional edge: after billing ────────────────────────────────────────────
def after_billing(state: SupportState) -> str:
    """Route to human_approval if refund needs sign-off, else continue."""
    if state.get("approval_required") and not state.get("human_decision"):
        return "needs_approval"
    return "continue"

def after_human_approval(state: SupportState) -> str:
    """Route based on human decision."""
    decision = state.get("human_decision", "")
    if decision == "rejected":
        return "rejected"
    return "approved"

# ── Build the graph ────────────────────────────────────────────────────────────
def build_graph():
    builder = StateGraph(SupportState)

    builder.add_node("router",          router_node)
    builder.add_node("billing",         billing_node)
    builder.add_node("shipping",        shipping_node)
    builder.add_node("technical",       technical_node)
    builder.add_node("human_approval",  human_approval_node)
    builder.add_node("billing_replan",  billing_replan_node)
    builder.add_node("synthesizer",     synthesizer_node)

    builder.set_entry_point("router")
    builder.add_edge("router", "billing")
    builder.add_edge("router", "shipping")   # LangGraph runs these after billing sequentially
    builder.add_edge("router", "technical")

    # After billing: check if approval needed
    builder.add_conditional_edges(
        "billing",
        after_billing,
        {"needs_approval": "human_approval", "continue": "synthesizer"},
    )

    # After human decision
    builder.add_conditional_edges(
        "human_approval",
        after_human_approval,
        {"rejected": "billing_replan", "approved": "synthesizer"},
    )

    builder.add_edge("billing_replan", "synthesizer")
    builder.add_edge("shipping",       "synthesizer")
    builder.add_edge("technical",      "synthesizer")
    builder.add_edge("synthesizer",    END)

    # MemorySaver enables checkpointing — required for interrupt_before
    memory = MemorySaver()
    return builder.compile(
        checkpointer=memory,
        interrupt_before=["human_approval"],
    )

graph = build_graph()
