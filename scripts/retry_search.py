#!/usr/bin/env python3
"""Retry the search-typing step human-style: click, then type char by char."""
import sys
import asyncio

sys.path.insert(0, r"D:\Samllm")
sys.path.insert(0, r"D:\Samllm\sam_engine")

from web_browser import WebBrowser
import human_click_test  # noqa: F401  (applies Chrome-channel patch)


async def main():
    wb = WebBrowser()
    page = await wb._get_page()
    await wb.visit("http://localhost:3000")
    sel = "main input[placeholder*='Search products']"
    loc = page.locator(sel)
    print("matches:", await loc.count())
    first = loc.first
    await first.click(delay=100)
    await first.press_sequentially("iPhone 15", delay=60)
    print("value:", await first.input_value())
    await first.press("Enter")
    await page.wait_for_timeout(4000)
    body = await page.text_content("body") or ""
    print("results shown:", ("Loot Deals" in body) or ("iPhone" in body))
    print("url:", page.url)
    await wb._browser.close()


if __name__ == "__main__":
    asyncio.run(main())
