#!/usr/bin/env python3
"""
VGAS AI — Auto Screen Generator
Uses SAM batch_runner to generate 4 React screens in parallel.
"""
import sys
import os
import json
import time
from pathlib import Path
from datetime import datetime

# Add sam_engine to path
_sam_dir = Path(r"D:\Samllm")
sys.path.insert(0, str(_sam_dir))
sys.path.insert(0, str(_sam_dir / "sam_engine"))

from batch_runner import run_batch

PROJECT_ROOT = Path(__file__).parent.parent
WEB_SRC = PROJECT_ROOT / "web" / "src"

# 4 screen generation tasks
TASKS = [
    {
        "name": "CompareScreen",
        "prompt": """Create a React component for a Product Comparison screen for VGAS.AI shopping app.

Requirements:
- Side-by-side comparison of 2-3 products
- Price history line chart (use Chart.js or recharts)
- Store-wise price table with "Best Price" highlight (green border)
- AI recommendation banner: "Best deal: Amazon at ₹X (save ₹Y)"
- Dark glassmorphism theme using CSS variables: --bg: #0f131c, --primary: #6366f1, --secondary: #22d3ee, --tertiary: #10b981
- Use Inter font, JetBrains Mono for prices
- Responsive grid layout
- Import from: react, recharts, axios, react-router-dom
- Export as default component

Write the complete component code. Use mock data for 3 products (iPhone 15, Samsung S24, OnePlus 12) with realistic Indian prices in ₹.""",
    },
    {
        "name": "ProductDetailScreen",
        "prompt": """Create a React component for a Product Detail screen for VGAS.AI shopping app.

Requirements:
- Large product image area with glow effect
- Product title, rating stars, price with discount badge
- Price history chart (30 days)
- Store list with prices (Amazon, Flipkart, Myntra, Meesho) - each with "Buy" button
- AI price prediction banner: "Expected price drop to ₹X in 5 days"
- Delivery info, specs accordion
- Dark glassmorphism theme: --bg: #0f131c, --primary: #6366f1, --secondary: #22d3ee, --tertiary: #10b981, --gold: #f59e0b
- Use Inter font, JetBrains Mono for prices
- Import from: react, recharts, axios, react-router-dom
- Export as default component

Write the complete component code. Use mock data for "iPhone 15 Pro Max 256GB" with realistic Indian prices.""",
    },
    {
        "name": "AdminDashboardScreen",
        "prompt": """Create a React component for an Admin Dashboard for VGAS.AI shopping app.

Requirements:
- Left sidebar navigation (Dashboard, Products, Scrapers, Users, Deals, Analytics, Settings)
- Top stats cards: Total Products (10Cr+), Active Scrapers (50+), Users (500K+), Revenue (₹2.4Cr)
- Charts row: Price trends line chart, Scraper performance bar chart, User growth area chart
- Recent deals table with product name, store, price, discount %, status badge (LIVE/EXPIRED)
- Dark glassmorphism theme: --bg: #0f131c, --primary: #6366f1, --secondary: #22d3ee, --tertiary: #10b981, --gold: #f59e0b, --red: #ef4444
- Use Inter font, JetBrains Mono for numbers
- Import from: react, recharts, axios, react-router-dom
- Export as default component

Write the complete component code with mock data for all charts and tables.""",
    },
    {
        "name": "ProfileScreen",
        "prompt": """Create a React component for a Profile screen for VGAS.AI shopping app.

Requirements:
- User avatar with glow ring, name, email, phone
- Stats row: Saved Alerts (12), Affiliate Earnings (₹4,500), Wishlist (28), Orders (45)
- Menu items: My Alerts, Payment Methods, Affiliate Dashboard, Notification Settings, Language, Help, Logout
- VIP membership banner with gradient
- Dark glassmorphism theme: --bg: #0f131c, --primary: #6366f1, --secondary: #22d3ee, --tertiary: #10b981, --gold: #f59e0b
- Use Inter font, JetBrains Mono for numbers
- Import from: react, axios, react-router-dom
- Export as default component

Write the complete component code with mock data.""",
    },
]


def main():
    print("=" * 60)
    print("  VGAS AI — AUTO SCREEN GENERATOR")
    print(f"  Started: {datetime.now().strftime('%H:%M:%S')}")
    print(f"  Tasks: {len(TASKS)} screens in parallel")
    print("=" * 60)
    print()

    # Run batch generation
    task_prompts = [t["prompt"] for t in TASKS]
    task_names = [t["name"] for t in TASKS]

    print(f"[BATCH] Firing {len(task_prompts)} parallel agents...")
    print()

    start_time = time.time()
    results = run_batch(task_prompts, model_choice="auto", batch_size=4)
    elapsed = time.time() - start_time

    print()
    print(f"[BATCH] Completed in {elapsed:.1f}s")
    print()

    # Save results
    screens_dir = WEB_SRC / "screens"
    screens_dir.mkdir(exist_ok=True)

    saved = []
    for (task, result), name in zip(results, task_names):
        # Clean up the result - extract code if wrapped in markdown
        code = result
        if "```python" in code:
            code = code.split("```python")[1].split("```")[0]
        elif "```" in code:
            code = code.split("```")[1].split("```")[0]

        # Determine file extension
        ext = "jsx" if "react" in task.lower() or "component" in task.lower() else "py"
        filename = f"{name}.{ext}"
        filepath = screens_dir / filename

        filepath.write_text(code.strip(), encoding="utf-8")
        saved.append((name, filepath, len(code)))
        print(f"  [SAVED] {name} -> {filename} ({len(code)} chars)")

    print()
    print(f"[DONE] {len(saved)} screens generated")
    print(f"[TIME] {elapsed:.1f}s elapsed")

    # Save generation report
    report = {
        "timestamp": datetime.now().isoformat(),
        "elapsed_seconds": elapsed,
        "screens": [{"name": n, "file": str(f), "chars": c} for n, f, c in saved],
    }
    report_path = PROJECT_ROOT / "scripts" / "generation_report.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"[REPORT] Saved to {report_path}")


if __name__ == "__main__":
    main()
