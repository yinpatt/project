from items import CartItem

SUPERSTORE_URL = "https://www.realcanadiansuperstore.ca"

SAFETY_RULES_TEMPLATE = """
Hard safety rules, apply to every step of this task, no exceptions:
- Never click "Checkout", "Proceed to checkout", "Place order", "Pay now", or any equivalent control.
- Never enter or submit payment information of any kind.
- Never complete or confirm an order.
- Adding a product to the basket/cart is the ONLY allowed cart action. Stop there.
- If a store-location or postal code prompt appears, use the postal code {postal_code} and proceed with the default/first store offered.
- If a login prompt appears, do not log in; continue as a guest/anonymous shopper if possible. If the site hard-blocks guest browsing, stop and report that as the failure reason.
""".strip()


def build_task_prompt(item: CartItem, postal_code: str) -> str:
    if item.specific:
        matching_rules = f"""
This is a SPECIFIC-BRAND request. The only acceptable product is one whose title contains the brand "{item.brand}" (case-insensitive; reasonable variation in pack size/count is fine).
Do NOT substitute a different brand or a store-brand/generic equivalent, even if it looks similar or is on sale.
If your first search for "{item.brand} {item.category}" returns no exact brand match, reword the query once (for example, search for just "{item.brand}", or try "{item.category} {item.brand}") and search again.
If, after that one retry, you still cannot find an exact "{item.brand}" match, STOP. Do not add anything to the basket. Report the item as unavailable.
""".strip()
    else:
        matching_rules = f"""
This is a GENERIC request with no brand preference for "{item.category}". Any reasonable, normal-sized {item.category} product is acceptable (store brand or name brand).
Search for "{item.category}" on the site. If the first search returns nothing usable, reword the query once (try a close synonym or simpler phrasing) and search again.
If, after that one retry, nothing reasonable is found, STOP. Do not add anything to the basket. Report the item as unavailable.
""".strip()

    brand_suffix = f" (brand: {item.brand})" if item.brand else ""

    return f"""
You are shopping on {SUPERSTORE_URL}.

Goal: find "{item.category}"{brand_suffix} and add exactly one matching product to the basket, following the rules below. Then STOP — do not continue shopping and do not proceed toward checkout.

{matching_rules}

{SAFETY_RULES_TEMPLATE.format(postal_code=postal_code)}

When you are done (whether you added an item or are flagging it as unavailable), your FINAL message must be exactly one line in this format, with no other text before or after it:
RESULT: <ADDED|NOT_FOUND> | <exact product title added, or "none"> | <one short sentence note>

Examples of a valid final line:
RESULT: ADDED | Charmin Ultra Strong Toilet Paper, 12 Mega Rolls | Exact brand match found on first search.
RESULT: NOT_FOUND | none | No Charmin Ultra Strong listing after reworded retry; flagging for manual review.
""".strip()
