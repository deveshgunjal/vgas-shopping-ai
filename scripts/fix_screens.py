#!/usr/bin/env python3
"""
VGAS AI — Fix mislabeled screens using SAM-LLM batch_runner.
Maps results by SCREEN_ID marker (not completion order).
"""
import sys
import time
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, r"D:\Samllm")
sys.path.insert(0, r"D:\Samllm\sam_engine")

from batch_runner import run_batch

PROJECT_ROOT = Path(__file__).parent.parent
SCREENS_DIR = PROJECT_ROOT / "web" / "src" / "screens"

STYLE_RULES = """
STYLING (mandatory):
- Dark glassmorphism inline styles ONLY. No external CSS imports (NEVER write import "./*.css").
- Colors: bg #0f131c, card rgba(15,23,42,0.65), border rgba(255,255,255,0.08),
  primary #6366f1, secondary #22d3ee, tertiary #10b981, gold #f59e0b, red #ef4444,
  text #f8fafc, secondary text #cbd5e1, muted #64748b.
- Cards: borderRadius 16, border 1px solid border color, padding 16-24.
- Prices in JetBrains-monospace style: fontFamily "'JetBrains Mono', monospace", green #10b981 bold.
- First line of file MUST be a valid import or comment. NEVER start file with a bare word.
- Export default with the EXACT component name given. No recharts dependency issues:
  you MAY use recharts (it is installed). If you use recharts, import from "recharts".
- React + axios + react-router-dom imports allowed. Mock data inline. No lorem ipsum.
"""

TASKS = [
    {
        "id": "COMPARE",
        "file": "CompareScreen.jsx",
        "prompt": """SCREEN_ID: COMPARE
Write file CompareScreen.jsx. Export default function CompareScreen().
Route: /compare. Side-by-side comparison of 3 products: iPhone 15 (Rs 1,15,900),
Samsung S24 (Rs 81,999), OnePlus 12 (Rs 62,999).
Required sections in order:
1. Green AI recommendation banner: "Best deal: Amazon at Rs 62,999 (save Rs 1,000)"
2. Three product cards side by side (responsive grid), each with: product title,
   big cyan price, 30-day price history line chart (recharts LineChart), store-wise
   price table (Amazon/Flipkart/Reliance rows, best price row highlighted green),
   and a "View Details" button linking to /product/1.
""" + STYLE_RULES,
    },
    {
        "id": "PRODUCT",
        "file": "ProductDetailScreen.jsx",
        "prompt": """SCREEN_ID: PRODUCT
Write file ProductDetailScreen.jsx. Export default function ProductDetailScreen().
Route: /product/:id. Single product detail for "iPhone 15 Pro Max 256GB".
Required sections in order:
1. Title, star rating 4.5, price Rs 1,34,990 with struck MRP Rs 1,59,900 and red -16% badge.
2. Cyan AI prediction banner: "Expected price drop to Rs 1,29,990 in 5 days".
3. "30-Day Price History" recharts LineChart trending down.
4. "Buy from" store list: Amazon Rs 1,34,990 (BEST PRICE green highlight),
   Flipkart, Myntra, Meesho rows each with a Buy button.
5. "Specifications" collapsible section with 6 spec rows.
""" + STYLE_RULES,
    },
    {
        "id": "ADMIN",
        "file": "AdminDashboardScreen.jsx",
        "prompt": """SCREEN_ID: ADMIN
Write file AdminDashboardScreen.jsx. Export default function AdminDashboardScreen().
Route: /admin. Admin dashboard with sidebar + main content (flex row layout).
Required sections in order:
1. Left sidebar (width 220): VGAS.AI logo, nav items Dashboard, Products, Scrapers,
   Users, Deals, Analytics, Settings (styled divs, active item indigo highlight).
2. Main area: 4 stat cards in a row (Total Products 10Cr+, Active Scrapers 50+,
   Users 500K+, Revenue Rs 2.4Cr) as glass cards.
3. "Price Trends" recharts LineChart (Mon-Sun).
4. "Scraper Performance" recharts BarChart (Amazon 120, Flipkart 95, Myntra 55).
5. "Recent Deals" styled table: columns Product, Store, Price, Discount, Status
   (LIVE green badge / EXPIRED red badge). 4 rows mock data.
""" + STYLE_RULES,
    },
    {
        "id": "PROFILE",
        "file": "ProfileScreen.jsx",
        "prompt": """SCREEN_ID: PROFILE
Write file ProfileScreen.jsx. Export default function ProfileScreen().
Route: /profile. User profile page.
Required sections in order:
1. Gold gradient VIP membership banner: "VGAS VIP - Ad-free + exclusive deals".
2. User card: avatar circle with initial "A", name "Arun Kumar",
   email, phone, Edit button.
3. Stats row of 4 glass cards: Saved Alerts 12, Affiliate Earnings Rs 4,500,
   Wishlist 28, Orders 45.
4. Settings menu list as glass rows with chevron: My Alerts, Payment Methods,
   Affiliate Dashboard, Notification Settings, Language, Help, red Logout row.
""" + STYLE_RULES,
    },
]


def clean_code(text: str) -> str:
    code = text.strip()
    if "```" in code:
        parts = code.split("```")
        for p in parts:
            s = p.strip()
            if s.startswith(("jsx", "js")):
                s = s[3:].strip()
            if s.startswith(("import ", "const ", "export ", "function", "//", "/*", "import{")):
                return s
        # fallback: longest block
        code = max(parts, key=len)
    lines = code.splitlines()
    # drop leading bare-word garbage lines (e.g. stray "jsx")
    while lines and lines[0].strip() in ("jsx", "js", "javascript"):
        lines.pop(0)
    return "\n".join(lines).strip()


def main():
    print("=" * 60)
    print("  VGAS AI — FIX SCREENS (SAM batch_runner, 4 parallel)")
    print(f"  Started: {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 60)

    prompts = [t["prompt"] for t in TASKS]
    by_id = {t["prompt"]: t for t in TASKS}

    start = time.time()
    results = run_batch(prompts, model_choice="auto", batch_size=4)
    elapsed = time.time() - start
    print(f"\n[BATCH] Done in {elapsed:.1f}s — mapping by SCREEN_ID...")

    saved = []
    for task_prompt, result in results:
        task = by_id.get(task_prompt)
        if not task:
            # fallback: detect SCREEN_ID echo in result
            for t in TASKS:
                if t["id"] in (result[:500] if result else ""):
                    task = t
                    break
        if not task:
            print("  [WARN] Unmatched result, skipping save")
            continue
        code = clean_code(result)
        path = SCREENS_DIR / task["file"]
        path.write_text(code, encoding="utf-8")
        saved.append(task["id"])
        print(f"  [SAVED] {task['id']} -> {task['file']} ({len(code)} chars)")

    report = {
        "timestamp": datetime.now().isoformat(),
        "elapsed_seconds": round(elapsed, 1),
        "saved": saved,
    }
    (PROJECT_ROOT / "scripts" / "fix_report.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    print(f"\n[DONE] {saved}")


if __name__ == "__main__":
    main()
