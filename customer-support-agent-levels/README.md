# Customer Support Agent — 10 Levels of Agentic Software

A single Customer Support Bot for "Acme Shop" (fictional electronics retailer), built 10 times. Each level adds exactly one capability and hits a natural wall — solved only in the next level.

**Stack:** Python · Streamlit · Anthropic SDK (`claude-sonnet-4-6`) · ChromaDB · SQLite
**UI pattern:** Two-column layout — left: chat, right: Agent Internals (every tool call + decision visible)

---

## The Wall-Solution Chain

| Level | What it adds | The real wall |
|-------|-------------|---------------|
| [L0: Raw LLM](./level0_raw_llm/) | Just Claude + a system prompt | Confabulates order data — no live data access |
| [L1: Single Tool](./level1_single_tool/) | `get_order_status` tool + agent loop | Can look up orders but can't act on them |
| [L2: Multi-Tool](./level2_multi_tool/) | 4 more tools: return, inventory, email, profile | Policy answers are guesses from training data |
| [L3: Knowledge/RAG](./level3_knowledge/) | ChromaDB policy docs + `search_policies` tool | Knows policy accurately, knows nothing about the customer |
| [L4: Learning/Memory](./level4_learning/) | SQLite interaction history across sessions | Capable but uncontrolled — no auth, no refund limits, no guardrails |
| L5: Reflection | Self-critique loop after each response | — |
| L6: Multi-Agent | Orchestrator + specialist agents | — |
| L7: Guardrails | Refund limits, confidence scoring, escalation | — |
| L8: Eval/Observability | Tracer, metrics dashboard, cost tracking | — |
| L9: Goal Decomposition | Planner with sub-goal tracking + replan | — |

---

## Shared Mock Data

All levels use `shared/data.py` — a Python dict, no database needed:

- **5 orders:** ORD-1001 (delivered), ORD-1002 (in transit), ORD-1003 (delayed), ORD-1004 (damaged), ORD-1005 (cancelled)
- **3 customers:** Sarah Chen (Gold · CUST-001), Marcus Williams (Standard · CUST-002), Priya Patel (Platinum · CUST-003)
- **10 inventory items:** mix of in-stock and out-of-stock
- **5 policy docs:** Return Policy, Shipping, Refunds, Warranty, Account & Billing

---

## Setup

```bash
pip install -r requirements.txt
# Add ANTHROPIC_API_KEY=sk-ant-... to a .env file in this folder
```

Run any level:
```bash
streamlit run level0_raw_llm/app.py
streamlit run level1_single_tool/app.py
# etc.
```

---

## Learning Pattern (same at every level)

1. **Read** the new file(s) before running
2. **Run** it — be a real customer
3. **Break** it intentionally
4. **Understand** why it fails
5. **Move** to the next level and see exactly what changed
