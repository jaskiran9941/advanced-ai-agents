# Level 2 — Multi-Tool

## What this level adds

4 new tools on top of L1:

| Tool | What it does |
|------|-------------|
| `get_customer_profile` | Fetches name, email, tier from a customer ID |
| `check_inventory` | Returns stock count for a product |
| `process_return` | Marks an order as `return_requested` in memory |
| `send_confirmation_email` | Mock email send — logs confirmation, no real email |

## What works

End-to-end support flows. Ask:

> "I want to return my damaged keyboard from ORD-1004"

Watch Claude chain 4 tools without being told the order:
1. `get_order_status` → gets order details + `customer_id`
2. `get_customer_profile` → uses `customer_id` from step 1 to get email
3. `process_return` → initiates the return
4. `send_confirmation_email` → sends to the email from step 2

Claude figured out that sequence on its own. You never told it the order.

## Run it

```bash
streamlit run level2_multi_tool/app.py
```

## What to try

1. `"I want to return order ORD-1001"` — full 4-tool chain, watch the internals
2. `"My order ORD-1004 arrived damaged, can I get a replacement?"` — adds `check_inventory`
3. `"Can I return my headphones after 45 days?"` — **hits the wall**
4. `"What's the warranty if my keyboard stops working?"` — **hits the wall**

## The wall

**Policy answers are guesses.** Claude has no access to Acme's actual policy documents. When you ask a policy question, it improvises an answer from training data — what a generic electronics retailer *might* say. It could be right, it could be wrong, and you can't tell which.

This is a hallucination risk in production. If Claude says "yes you can return after 45 days" but the real policy is 30 days, a customer just got a wrong promise.

## Key concepts

**Implicit planning** — Claude sequences multiple tools in the right order without explicit instructions. It infers dependencies: "I need the email before I can send the confirmation, and the email is in the customer profile, and the customer ID is in the order."

**The agent loop is unchanged** — adding 4 tools didn't change a single line of `agent.py`. Tools are data the loop reads, not code the loop runs differently.

## Files

| File | What it does |
|------|-------------|
| `app.py` | Streamlit UI with token summary bar + suggestion buttons |
| `agent.py` | Same annotated loop as L1 |
| `tools.py` | 5 tool schemas + execution functions + dispatcher |
