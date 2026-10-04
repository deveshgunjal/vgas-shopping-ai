#!/usr/bin/env python3
"""
VGAS AI — Human-like click-through test using SAM-LLM's WebBrowser engine.
Clicks every nav option, searches, opens products, hovers cards.
"""
import sys
import asyncio
import json
from datetime import datetime

sys.path.insert(0, r"D:\Samllm")
sys.path.insert(0, r"D:\Samllm\sam_engine")

from web_browser import WebBrowser


async def _get_browser_chrome(self):
    """Use installed Google Chrome (bundled headless shell version mismatches)."""
    if self._browser and self._browser.is_connected():
        return self._browser
    from playwright.async_api import async_playwright
    self._playwright = await async_playwright().start()
    self._browser = await self._playwright.chromium.launch(
        headless=True, channel="chrome"
    )
    return self._browser


WebBrowser._get_browser = _get_browser_chrome

BASE = "http://localhost:3000"
SHOT = r"C:\Users\nikhi\AppData\Local\Temp\opencode"

results = []


def record(name, ok, detail=""):
    results.append({"step": name, "pass": bool(ok), "detail": detail})
    print(f"  [{'PASS' if ok else 'FAIL'}] {name} {detail}")


async def main():
    print("=" * 60)
    print("  VGAS AI — HUMAN CLICK TEST (SAM-LLM WebBrowser)")
    print(f"  Started: {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 60)

    wb = WebBrowser()
    page = await wb._get_page()

    # 1. Home — hero copy is honest, and the fake "10 Crore+ / 50+ / 500K+"
    #    marketing numbers must be gone.
    r = await wb.visit(BASE)
    body = await page.text_content("body") or ""
    record("open home",
           "Compare Real Prices" in body
           and "10 Crore+" not in body
           and "500K+" not in body
           and "10Cr+" not in body,
           f"status={r.get('status')}")
    await wb.screenshot(f"{SHOT}\\t_home.png")

    # 2. Click Compare nav -> REAL compare page (URL inputs, no static fake products)
    r = await wb.click("nav a[href='/compare']")
    body = await page.text_content("body") or ""
    record("click Compare", "Compare real products" in body and "OnePlus 12" not in body,
           r.get("status", r.get("error", "")))
    await wb.screenshot(f"{SHOT}\\t_compare.png")

    # 3. Click Admin nav -> REAL admin (waits for live API data, not static)
    r = await wb.click("nav a[href='/admin']")
    try:
        await page.wait_for_selector("text=Recent Deals", timeout=25000)
    except Exception:
        pass
    try:
        await page.wait_for_selector("text=unreachable", timeout=1000)
    except Exception:
        pass
    body = await page.text_content("body") or ""
    record("click Admin", "Admin Dashboard" in body and ("Recent Deals" in body or "unreachable" in body),
           r.get("status", r.get("error", "")))
    await wb.screenshot(f"{SHOT}\\t_admin.png")

    # 4. Click Profile nav -> REAL profile (live auth state, no mock "Arun Kumar")
    r = await wb.click("nav a[href='/profile']")
    body = await page.text_content("body") or ""
    record("click Profile", "Arun Kumar" not in body and ("Not logged in" in body or "Logout" in body),
           r.get("status", r.get("error", "")))
    await wb.screenshot(f"{SHOT}\\t_profile.png")

    # 5. Back Home, type in hero search (real keystrokes), press Enter
    r = await wb.click("nav a[href='/']")
    await page.wait_for_timeout(1500)
    hero_input = "main input[placeholder*='Search products']"
    await page.click(hero_input)
    await page.locator(hero_input).press_sequentially("iPhone 15", delay=80)
    val = await page.input_value(hero_input)
    record("type search", val == "iPhone 15", f"value='{val}'")
    await page.press(hero_input, "Enter")
    await page.wait_for_timeout(3000)
    body = await page.text_content("body") or ""
    record("search enter", "Loot Deals" in body or "iPhone" in body, "no crash")
    await wb.screenshot(f"{SHOT}\\t_search.png")

    # 6. Click first product link -> REAL PDP: live-lookup box, NO hardcoded fake.
    #    The live scrape takes 20-120s, so wait for whichever real outcome arrives:
    #    (a) a product card with a link, or (b) the honest empty state.
    #    What must never happen is a sample product standing in for real data.
    try:
        await page.wait_for_function(
            """() => document.querySelector("main a[href^='/product/']") !== null
                   || document.body.innerText.includes("No live products returned")""",
            timeout=60000,
        )
    except Exception:
        pass
    links = await page.query_selector_all("main a[href^='/product/']")
    if links:
        await links[0].click(delay=100)
        await page.wait_for_timeout(2500)
        body = await page.text_content("body") or ""
        record("click View Deal", ("Live product lookup" in body and "iPhone 15 Pro Max" not in body),
               f"url={page.url}")
        await wb.screenshot(f"{SHOT}\\t_pdp.png")
    else:
        body = await page.text_content("body") or ""
        honest = "No live products returned" in body
        record("click View Deal", honest,
               "no live products — honest empty state shown" if honest
               else "no product links AND no honest empty state")

    # 7. Hover a live data element (category chips come from /search/categories)
    await wb.click("nav a[href='/']")
    await page.wait_for_timeout(1500)
    chips = await page.query_selector_all("main section div[style*='min-width: 110px']")
    if chips:
        await chips[0].hover()
        record("hover card", True, "hover ok (live category chip)")
    else:
        record("hover card", False, "no cards")

    # 8. Login button present
    btn = await page.query_selector("button.btn-primary")
    record("login button", btn is not None, "")

    passed = sum(1 for x in results if x["pass"])
    print("=" * 60)
    print(f"  RESULT: {passed}/{len(results)} passed")
    print("=" * 60)
    print(json.dumps(results))

    await wb._browser.close()


if __name__ == "__main__":
    asyncio.run(main())
