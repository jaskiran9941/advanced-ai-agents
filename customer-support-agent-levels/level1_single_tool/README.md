# Level 1 — Single Tool

## What this level adds

One tool: `get_order_status(order_id)` — looks up a real order from `shared/data.py`.

More importantly: an explicit **agent loop**. The code runs Claude, checks `stop_reason`, executes the tool if needed, sends the result back, and loops until Claude is done. You write this loop yourself so you can see exactly how it works.

## What works

> "Where is my order ORD-1002?"

Claude calls the tool, gets real data, answers accurately. The Agent Internals panel shows every step:
- 🟡 LLM call #1 — `stop_reason: tool_use`
- 🔧 `get_order_status` called with `{"order_id": "ORD-1002"}`
- 📦 Tool result returned
- 🟢 LLM call #2 — `stop_reason: end_turn`

## Run it

```bash
streamlit run level1_single_tool/app.py
```

## What to try

1. `"Where is ORD-1002?"` — watch the loop run in the internals panel
2. `"Where is ORD-9999?"` — tool returns "not found", Claude handles it gracefully
3. `"I want to return ORD-1001"` — **hits the wall**

## The wall

**Can look, can't act.** Claude can tell you the order status, but it has no tool to process a return, check if a replacement is in stock, or send a confirmation. It sees the problem — it just can't do anything about it.

## Key concepts

**Tool schema** — the JSON description Claude reads to know a tool exists and what arguments to pass. Lives in `tools.py` as `TOOL_SCHEMAS`.

**`stop_reason`** — the signal Claude sends back:
- `"tool_use"` → Claude wants data, keep looping
- `"end_turn"` → Claude is done, return the text

**The loop** — Claude never runs your Python. It asks you to run it, then you send the result back. The loop in `agent.py` is that back-and-forth made explicit.

## Files

| File | What it does |
|------|-------------|
| `app.py` | Streamlit UI, renders each loop step in the internals panel |
| `agent.py` | The annotated agent loop — the core of this level |
| `tools.py` | Tool schema + `get_order_status` function + dispatcher |
