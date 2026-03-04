"""
state.py — Level 7
==================
The shared state TypedDict that flows through the entire LangGraph.

This is what L6 was missing. Instead of the orchestrator passing prose
strings between agents, every agent reads from and writes to this single
object. Hard facts stay hard — a boolean doesn't become "we'll explore options."

Key differences from L6:
  - refund_amount is a float, not a sentence
  - replacement_in_stock is a bool, not "we have stock available"
  - approval_required is a flag the graph reads to decide routing
  - human_decision carries the approval/rejection back into the graph
"""

from typing import TypedDict, Optional


class SupportState(TypedDict):
    # ── Input ──────────────────────────────────────────────────────────────
    ticket:           str             # original customer message
    customer_history: str             # injected memory from SQLite

    # ── Routing ────────────────────────────────────────────────────────────
    specialists:      list[str]       # which agents to call: ["billing", "shipping", ...]
    billing_context:  str
    shipping_context: str
    technical_context: str

    # ── Billing state ──────────────────────────────────────────────────────
    billing_result:   str             # billing agent's prose response
    refund_amount:    float           # extracted from order data — a real number
    return_processed: bool            # did process_return() succeed?

    # ── Human-in-the-loop ──────────────────────────────────────────────────
    approval_required: bool           # True when refund_amount > APPROVAL_THRESHOLD
    approval_reason:   str            # why approval is needed
    human_decision:    Optional[str]  # "approved" | "rejected" | None (pending)
    rejection_reason:  Optional[str]  # human's reason if rejected

    # ── Shipping state ─────────────────────────────────────────────────────
    shipping_result:  str

    # ── Technical state ────────────────────────────────────────────────────
    technical_result:      str
    replacement_in_stock:  bool       # hard boolean — not a prose guess
    replacement_product_id: str

    # ── Output ─────────────────────────────────────────────────────────────
    final_response:   str             # synthesized customer-facing reply


APPROVAL_THRESHOLD = 200.0  # refunds above this require human approval
