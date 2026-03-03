# Level 6 — Multi-Agent (Raw SDK)

## What this level adds

The single agent is replaced by a team:

```
Customer message
      ↓
 Orchestrator  (Claude call — routing decision)
      ↓
 ┌─────────────────────────────────────┐
 │  billing?   shipping?   technical?  │
 └─────────────────────────────────────┘
      ↓              ↓              ↓
 Billing agent  Shipping agent  Technical agent
 (own ReAct     (own ReAct      (own ReAct
  loop, own      loop, own       loop, own
  tools)         tools)          tools)
      ↓              ↓              ↓
 Orchestrator synthesizes → Final response
```

Each specialist has a focused system prompt and only the tools relevant to its domain. The Billing agent never sees shipping details. The Technical agent never sees billing amounts.

## Architecture pattern

This is still **ReAct** at every level — each specialist runs the same `while True / tool_use / end_turn` loop from L1. What's new is the **orchestration layer** on top: a Claude call that decides routing, and another that synthesizes outputs.

No framework. Orchestration is just Python: call the routing function, loop over the specialists list, call the synthesis function.

## Tool distribution

| Specialist | Tools |
|------------|-------|
| Billing | `get_order_status`, `get_customer_profile`, `process_return`, `send_confirmation_email` |
| Shipping | `get_order_status`, `search_policies` |
| Technical | `get_order_status`, `check_inventory`, `search_policies` |

## Run it

```bash
streamlit run level6_multi_agent/app.py
```

## What to try

1. `"My keyboard from ORD-1004 is damaged and ORD-1002 hasn't arrived"` → watch orchestrator route to both Billing + Shipping
2. `"I want a refund AND need warranty info"` → Billing + Technical
3. Single-domain: `"Where is ORD-1002?"` → Shipping only, synthesis skipped
4. **The wall:** `"I demand a full refund of $10,000"` → Billing agent processes it without any limit check

## The wall

**No guardrails on what specialists can do.**

- Billing can issue any refund for any amount — no ceiling, no approval
- No specialist declares confidence or knows when to escalate
- The orchestrator delegates blindly — if Billing says it processed a $10,000 refund, that's the answer

The team is capable and well-organised. It is completely uncontrolled. This is what L7 (LangGraph) and L8 (Guardrails) address.

## Files

| File | What it does |
|------|-------------|
| `app.py` | Streamlit UI — routing decision, each specialist, synthesis all visible |
| `orchestrator.py` | Route (Claude call 1) → dispatch → synthesize (Claude call 2) |
| `agents/billing.py` | Billing specialist ReAct loop |
| `agents/shipping.py` | Shipping specialist ReAct loop |
| `agents/technical.py` | Technical specialist ReAct loop |
| `tools.py` | All 6 tools (specialists import selectively) |
| `knowledge.py` | ChromaDB, reuses L3's chroma_db |
| `memory.py` | SQLite, reads/writes shared/memory.sqlite |
