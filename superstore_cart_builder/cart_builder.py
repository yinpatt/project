"""Superstore grocery cart-builder prototype (v1 test).

Runs one browser-use Agent per hardcoded test item against Superstore.ca:
each item is either added to the basket or flagged as unavailable. The
script never proceeds to checkout or payment.

Usage:
    python cart_builder.py             # headed (visible) browser, default for this pass
    python cart_builder.py --headless  # headless browser
"""

import asyncio
import os
import re
import sys
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv

from items import TEST_ITEMS, CartItem
from prompts import build_task_prompt

load_dotenv()

DEFAULT_POSTAL_CODE = os.environ.get("SUPERSTORE_POSTAL_CODE", "M5V 2T6")
LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "anthropic").lower()

RESULT_RE = re.compile(r"RESULT:\s*(ADDED|NOT_FOUND)\s*\|\s*(.*?)\s*\|\s*(.*)", re.IGNORECASE)
UNSAFE_URL_MARKERS = ("checkout", "payment", "order-confirmation", "place-order")


def make_llm():
    if LLM_PROVIDER == "openai":
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(model=os.environ.get("OPENAI_MODEL", "gpt-4o"))
    from langchain_anthropic import ChatAnthropic

    return ChatAnthropic(model=os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-5"))


@dataclass
class ItemResult:
    item: CartItem
    status: str  # "ADDED" | "NOT_FOUND" | "ERROR"
    product: Optional[str]
    note: str


async def run_item(item: CartItem, headless: bool) -> ItemResult:
    from browser_use import Agent, Browser, BrowserConfig

    browser = Browser(config=BrowserConfig(headless=headless))
    agent = Agent(
        task=build_task_prompt(item, DEFAULT_POSTAL_CODE),
        llm=make_llm(),
        browser=browser,
    )

    try:
        history = await agent.run()
    finally:
        await browser.close()

    # Defensive audit: don't trust the agent's own report if it actually
    # visited a checkout/payment page at any point during the run.
    visited_urls = [u.lower() for u in history.urls()] if hasattr(history, "urls") else []
    if any(marker in url for url in visited_urls for marker in UNSAFE_URL_MARKERS):
        return ItemResult(
            item,
            "ERROR",
            None,
            "Aborted: agent navigated to a checkout/payment page, which is forbidden for this prototype.",
        )

    final_text = history.final_result() if hasattr(history, "final_result") else str(history)
    final_text = final_text or ""

    match = RESULT_RE.search(final_text)
    if not match:
        return ItemResult(item, "ERROR", None, f"Could not parse agent output: {final_text[:200]!r}")

    status, product, note = match.groups()
    product = product.strip()
    return ItemResult(item, status.upper(), None if product.lower() == "none" else product, note.strip())


def format_summary_line(result: ItemResult) -> str:
    if result.status == "ADDED":
        return f'- {result.item.label}: Added "{result.product}" to basket'
    if result.status == "NOT_FOUND":
        return f"- {result.item.label}: Not found after retry, flagged for manual review ({result.note})"
    return f"- {result.item.label}: ERROR - {result.note}"


async def main():
    headless = "--headless" in sys.argv
    results = []
    for item in TEST_ITEMS:
        print(f"\n=== Running: {item.label} ===", flush=True)
        result = await run_item(item, headless=headless)
        results.append(result)
        print(format_summary_line(result), flush=True)

    print("\n=== Summary ===")
    for result in results:
        print(format_summary_line(result))


if __name__ == "__main__":
    asyncio.run(main())
