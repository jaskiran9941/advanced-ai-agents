# Level 3 — Knowledge / RAG

## What this level adds

`knowledge.py` — a ChromaDB vector store loaded with Acme Shop's 5 policy documents. One new tool: `search_policies(query)`.

Instead of guessing policy from training data, Claude now retrieves the actual document and bases its answer on that.

## What works

> "Can I return a laptop after 45 days?"

L2 would guess. L3 calls `search_policies("return policy timeframe")`, retrieves the Return Policy doc, reads the actual 30-day window, and answers accurately — citing the real policy.

The Agent Internals panel distinguishes policy lookups (🔍) from order lookups (🔧) and shows each retrieved doc with its relevance score.

## Run it

```bash
streamlit run level3_knowledge/app.py
```

**First run only:** ChromaDB downloads the `all-MiniLM-L6-v2` embedding model (~90MB). Subsequent runs are instant — the model and embeddings are cached to disk.

## What to try

1. `"Can I return a laptop after 45 days?"` — see the exact policy doc retrieved
2. `"What's the warranty on my damaged keyboard from ORD-1004?"` — chains `get_order_status` + `search_policies`
3. `"Does free shipping apply to my order ORD-1002?"` — policy + order data together
4. `"I've complained about late deliveries 3 times — what are you doing?"` — **hits the wall**

## The wall

**Knows policy accurately, knows nothing about you.** The ChromaDB database persists between sessions — policy knowledge never forgets. But there is no record of past customer interactions. Ask about your 3 complaints and the agent responds as if it's your first contact ever.

The distinction: L2's forgetting was about *policy* (hallucination). L3's forgetting is about *the individual customer* (no persistent interaction history).

## How RAG works (what the internals panel shows)

1. Your query is converted to a vector (list of ~384 numbers) by the embedding model
2. ChromaDB finds the policy doc vectors closest to your query vector
3. The matching doc text is returned to Claude as tool output
4. Claude answers from that text, not from training data

This is why it beats keyword search: "return after 45 days" matches "30-day return window" even though none of those exact words overlap — they're *semantically* close.

## Files

| File | What it does |
|------|-------------|
| `app.py` | Streamlit UI — policy results render differently from order results |
| `agent.py` | Same loop, updated system prompt: "always call search_policies for policy questions" |
| `tools.py` | 6 tools: all of L2 + `search_policies` |
| `knowledge.py` | ChromaDB setup, lazy-load collection, `search_policies()` function |
