# Level 4 — Learning / Memory

## What this level adds

`memory.py` — SQLite-backed customer interaction history that persists across sessions.

**At session end:** Click "Save & End Session" → Claude reads the conversation and extracts structured fields → one row saved to `memory.sqlite`.

**At session start:** The app loads that customer's past rows and injects them as text into the system prompt → agent knows the customer before they say a word.

## Memory schema (one row per session)

| Field | Example |
|-------|---------|
| `customer_id` | `CUST-001` |
| `timestamp` | `2026-03-03T00:11:00` |
| `issue_type` | `damaged_item` |
| `resolution` | `return_processed` |
| `sentiment` | `frustrated` |
| `orders_mentioned` | `ORD-1004` |
| `summary` | `Customer received a damaged keyboard, return initiated, confirmation sent.` |

Structured fields chosen over free-text because they're predictable token cost, queryable via SQL, and easy to inject cleanly into a prompt.

## What works

1. Pick **Sarah Chen**, have a conversation about her damaged order
2. Click **Save & End Session**
3. Switch to Marcus Williams, have a different conversation, save
4. Switch back to **Sarah Chen**
5. The agent greets her with her history — "I see you've had a damaged item issue before"

## Run it

```bash
streamlit run level4_learning/app.py
```

## What to try

1. Have a conversation, save it, come back as the same customer — see memory load in the internals panel
2. `"My order arrived damaged, the replacement was also wrong, AND my account email is broken"` — agent handles it
3. Log in as **Marcus Williams**, ask about **ORD-1001** (Sarah's order) — **hits the wall**

## The real wall

**The agent acts with no safety checks.**

- **No authorization:** Log in as Marcus, ask about ORD-1001. The agent processes Sarah's order, promises her a refund, sends email to sarah.chen@example.com — because Marcus asked. There's no ownership check.
- **No refund limits:** Ask for a $10,000 refund. The agent will attempt to process it.
- **No escalation policy:** The agent makes binding promises (replacements, refunds, timelines) with no approval workflow and no confidence scoring on edge cases.

Memory is working. Capability is working. **Control is missing entirely.**

This is why L5 (reflection) and L7 (guardrails) exist — not to make the agent smarter, but to make it safer.

## How memory injection works

The agent loop itself is unchanged from L1-L3. Memory is a **prompt engineering pattern**:

```python
# In agent.py
system_prompt = base_prompt + "\n\n" + customer_history_text
```

Claude doesn't know history came from a database. It just sees text that says "this customer had 3 delivery issues." The database is invisible to the loop.

## Files

| File | What it does |
|------|-------------|
| `app.py` | Streamlit UI with sidebar customer selector + Save & End Session button |
| `agent.py` | Same loop as L1-L3, now accepts `customer_history` string |
| `memory.py` | SQLite init, `load_customer_history()`, `save_interaction()` with Claude extraction |
| `tools.py` | Same 6 tools as L3 |
| `knowledge.py` | Same as L3, reuses L3's chroma_db |

## Note on `memory.sqlite`

The database file is gitignored — it's runtime data, not source code. It's created automatically on first use. Every developer who clones the repo starts with a clean memory.
