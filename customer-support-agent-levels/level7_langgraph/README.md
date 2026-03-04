# Level 7 — LangGraph Orchestration

## What this level adds over L6

Same multi-agent team (Billing, Shipping, Technical) — but rebuilt in LangGraph with two genuine improvements:

### 1. Shared typed state (replaces prose string passing)

In L6, the orchestrator passed context strings to specialists and read prose strings back. The synthesizer could reinterpret hard facts.

In L7, every agent reads from and writes to a single `SupportState` TypedDict:

```python
state["refund_amount"]       = 149.00    # float — not "the refund is $149"
state["return_processed"]    = True      # bool — not "the return was processed"
state["replacement_in_stock"] = False    # bool — synthesis cannot soften this
```

The synthesizer receives these structured values alongside the prose responses, so it can't hallucinate: "we'll arrange a replacement" when `replacement_in_stock = False`.

### 2. Human-in-the-loop approval (native LangGraph feature)

When `refund_amount > $200`, the graph pauses at the `human_approval` node via `interrupt_before`. The UI shows an approval gate. You approve or reject. The graph resumes from that exact checkpoint.

On rejection: `billing_replan` node runs — Billing offers store credit or a partial refund up to $200.

```
billing node
     ↓
 refund > $200?
     ↓ yes
 [GRAPH PAUSES]  ← interrupt_before=["human_approval"]
     ↓ human approves
 synthesizer
     ↓ human rejects
 billing_replan → synthesizer
```

## Architecture

```
router
  ↓
billing ──→ [human_approval] ──approved──→ synthesizer
  ↓               ↓ rejected                    ↑
shipping     billing_replan ──────────────────────
  ↓
technical ────────────────────────────────────────↑
```

## Run it

```bash
pip install langgraph
streamlit run level7_langgraph/app.py
```

## What to try

1. `"Return my damaged keyboard from ORD-1004"` ($149 → auto-approved, no gate)
2. `"I want a full refund plus $500 compensation"` → triggers approval gate
3. Approve → synthesis includes confirmed refund
4. Reject → billing replans, offers store credit or partial refund up to $200
5. `"I demand $10,000"` → gate fires immediately

## The wall

**Framework hides internals.** When something breaks in L6, the traceback points to your code. When something breaks in L7, it points to LangGraph internals. The `StateGraph`, `MemorySaver`, `interrupt_before` — these are powerful but opaque. Debugging a LangGraph error requires understanding the framework's execution model, not just your own logic.

Also: LangGraph's sequential node execution means specialists still run one at a time. True parallelism requires async nodes — a more advanced pattern.

## Files

| File | What it does |
|------|-------------|
| `app.py` | Streamlit UI with approval gate, shared state viewer |
| `graph.py` | LangGraph definition: nodes, edges, conditional routing, interrupt |
| `state.py` | `SupportState` TypedDict — the shared state schema |
| `agents/billing.py` | Billing node — writes `refund_amount`, `approval_required` to state |
| `agents/shipping.py` | Shipping node |
| `agents/technical.py` | Technical node — writes `replacement_in_stock` (bool) to state |
| `tools.py` | Same 6 tools as L6 |
| `knowledge.py` | ChromaDB, reuses L3's chroma_db |
| `memory.py` | SQLite, reads/writes shared/memory.sqlite |

## L6 vs L7 comparison

| | L6 (raw) | L7 (LangGraph) |
|---|---|---|
| Agent communication | Prose strings via orchestrator | Typed state object |
| `refund_amount` | String in prose | `float` in state |
| `replacement_in_stock` | Text that can be softened | `bool` in state |
| Human approval | Not possible cleanly | `interrupt_before` native |
| Replan on rejection | Custom Python needed | Conditional edge to replan node |
| Debugging | Your code | LangGraph internals |
