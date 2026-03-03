# Level 0 — Raw LLM

## What this level is

Just Claude with a system prompt. No tools. No data access. No memory.

## What's new vs. nothing

A Streamlit chat UI with an Agent Internals panel that shows the raw API call — model, token counts, stop reason. This is the baseline everything else builds on.

## What works

General questions Claude can answer from training data:
- "What's a typical return policy?"
- "How does express shipping usually work?"

## Run it

```bash
streamlit run level0_raw_llm/app.py
```

## What to try

Ask something general first, then ask something specific to Acme Shop:

> "Where is my order ORD-1002?"

Claude will either make something up (confabulation) or admit it doesn't have access. Either way it can't give you the real answer — because it has no real data.

## The wall

**Confabulation.** Claude is a pattern-matcher trained on text. When asked about a specific order, it fills the gap with a plausible-sounding answer. It has no mechanism to say "I don't know this specific fact" — it generates what an answer *should look like*.

This isn't a bug. It's how LLMs work. The fix isn't a better model — it's giving the model access to real data via tools.

## Key concept

LLMs don't "know" your business. They generate text that resembles what a support agent might say. That's useful for tone and language — useless for facts.

## Files

| File | What it does |
|------|-------------|
| `app.py` | Streamlit UI + single Claude API call |
