# Level 5 — Reflection

## What this level adds

A self-critique loop around every agent response. After producing a draft, a second Claude call reviews it for completeness. If gaps are found, the agent regenerates with the critique as context — up to **3 attempts**.

This is how production systems like Claude's extended thinking and OpenAI's o1 work internally: iterate until a quality threshold is met, with a hard cap to prevent infinite loops.

## Architecture

```
for attempt in 1..3:
    draft = run_agent_turn()       # standard tool-use loop
    verdict = critique(draft)      # second Claude call
    if verdict.complete:
        return draft               # done
    else:
        messages.append(critique_feedback)
        # loop again with feedback as context

return draft  # return best effort after 3 attempts
```

## What works

Multi-part questions get caught before they reach the customer. Try:

> "I need a refund for ORD-1001 AND want to know if I can return after 45 days AND check if the headphones are in stock"

Watch the internals panel:
- **Attempt 1:** Agent drafts a response
- **Critique:** ⚠️ Gaps found — "missed the inventory check"
- **Attempt 2:** Regenerates with critique feedback
- **Critique:** ✅ Complete — no gaps found
- **Done** on attempt 2

## Run it

```bash
streamlit run level5_reflection/app.py
```

## What to try

1. Any multi-part question from the suggestion buttons — see the critique fire
2. A simple single question — critique should pass on attempt 1 (no extra cost)
3. Notice the token count in the summary bar — reflection has a real cost

## The wall

**Cost and latency scale with reflection passes.** Every attempt is at minimum 2 Claude calls (1 agent + 1 critic). Worst case: 6 calls per customer message. That's 3-6× the cost of L1-L4.

More fundamentally: it's still **one agent** handling everything. Billing logic, shipping tracking, technical issues, policy lookups — all in one context window, all in one loop. Reflection makes it more thorough, not more efficient. Routing complex tickets to specialists would be faster and cheaper.

That's what L6 (multi-agent) addresses.

## Cost reality

| Scenario | Agent calls | Critic calls | Total calls |
|----------|-------------|--------------|-------------|
| Simple question, passes immediately | 1 | 1 | 2 |
| 2-part question, passes on attempt 2 | 2 | 2 | 4 |
| Complex ticket, hits max attempts | 3 | 3 | 6 |

## Key concept

**Reflection is a quality vs. cost tradeoff** — not a free improvement. Every pass costs tokens and latency. By L8 (eval/observability), you'll have the tooling to measure whether the quality gain justifies the extra cost per ticket.

## Files

| File | What it does |
|------|-------------|
| `app.py` | Streamlit UI — shows each attempt, critique verdict, retry reason |
| `agent.py` | `run_agent_turn()` + `critique()` + `run_agent()` reflection loop |
| `tools.py` | Same 6 tools as L3/L4 |
| `knowledge.py` | Same as L4, reuses L3's chroma_db |
| `memory.py` | Same as L4 — structured SQLite history |
