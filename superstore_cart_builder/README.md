# Superstore grocery cart-builder prototype (v1 test)

Uses [browser-use](https://github.com/browser-use/browser-use) to search
Superstore.ca for 4 hardcoded test items and either add the matching
product to the basket or flag it as unavailable. **Stops before checkout —
no payment or order actions are ever taken.**

## Test items (`items.py`)

| Item | Brand | Match rule |
|---|---|---|
| Toilet paper | Charmin Ultra Strong | Specific — no substitutes |
| Dishwasher tablets | Finish Powerball | Specific — no substitutes |
| Kitchen towel | none | Generic — any reasonable product |
| Paper towel | none | Generic — any reasonable product |

## Execution model

- One `browser-use` `Agent` run per item (`run_item` in `cart_builder.py`),
  not one combined task for all four.
- Each item's task prompt (`prompts.py`) tells the agent to retry once with
  a reworded search query on an empty/failed search before giving up and
  flagging the item.
- Headed (visible) browser by default for this first pass; pass
  `--headless` to run without a visible window.
- The prompt hard-bans checkout/payment/order actions, and `cart_builder.py`
  additionally audits the agent's visited-URL history after each run and
  overrides the result to an error if a checkout/payment page was ever
  visited, regardless of what the agent claims.

## Setup

```bash
cd superstore_cart_builder
pip install -r requirements.txt
playwright install chromium
cp .env.example .env   # fill in ANTHROPIC_API_KEY or OPENAI_API_KEY
python cart_builder.py
```

## Known limitation: not runnable in this sandbox

This code was written and committed from a Claude Code remote sandbox that
cannot actually execute it end-to-end, for two independent reasons:

1. **No route to the live site.** Outbound network from this container goes
   through an org-policy proxy that only allow-lists a small set of
   infrastructure hosts (PyPI, npm, the Anthropic API, etc.) — a CONNECT to
   `realcanadiansuperstore.ca` is rejected with a 403 at the proxy.
2. **No LLM key available to drive a separate agent loop.** `browser-use`
   needs its own `ANTHROPIC_API_KEY`/`OPENAI_API_KEY` to reason over each
   page; this session has neither exposed as an environment variable.

Because of that, no live run was performed and no per-item results are
reported here — doing so would mean fabricating them. Run it from an
environment with real internet access and an LLM key to get an actual
per-item summary in the form:

```
- Toilet paper: Added "Charmin Ultra Strong 12-pack" to basket
- Dishwasher tablets: Added "Finish Powerball Ultimate" to basket
- Kitchen towel: Added "No Name Kitchen Towel 6-pack" to basket
- Paper towel: Not found after retry, flagged for manual review
```

## Out of scope for this prototype

Notion integration, Hermes scheduling, reminders integration, price
optimization.
