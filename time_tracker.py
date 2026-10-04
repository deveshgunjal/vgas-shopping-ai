"""
VGAS Work Time Tracker
Run: python time_tracker.py
Shows: TODO list + elapsed time + remaining time + progress bar
"""
import time, sys, os
from datetime import datetime, timedelta

START_TIME = time.time()

# Task definitions: (id, name, est_minutes, status)
TASKS = [
    ("BUG1", "Redis cache for loot-deals/trending", 30, "pending"),
    ("BUG2", "Fix price selectors (6 stores)", 45, "pending"),
    ("BUG3", "Stripe checkout (BLOCKED)", 0, "blocked"),
    ("GIT",  "Git commit + push (77 files)", 10, "pending"),
]

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def render():
    clear()
    elapsed = time.time() - START_TIME
    elapsed_min = elapsed / 60

    total_est = sum(t[2] for t in TASKS if t[2] > 0)
    done_est = sum(t[2] for t in TASKS if t[3] == "done")
    remaining = max(0, total_est - done_est)

    bar_len = 40
    filled = int(bar_len * done_est / total_est) if total_est > 0 else 0
    bar = "█" * filled + "░" * (bar_len - filled)

    print("=" * 70)
    print("  VGAS SHOPPING-AI — WORK TRACKER")
    print("=" * 70)
    print(f"  Started:     {datetime.fromtimestamp(START_TIME).strftime('%H:%M:%S')}")
    print(f"  Elapsed:     {elapsed_min:.1f} min")
    print(f"  Est total:   {total_est} min")
    print(f"  Remaining:   {remaining} min")
    print(f"  Progress:    [{bar}] {done_est*100//total_est if total_est else 0}%")
    print("=" * 70)
    print()
    print(f"  {'ID':<6} {'STATUS':<10} {'EST':>5}  {'TASK'}")
    print(f"  {'-'*6} {'-'*10} {'-'*5}  {'-'*40}")
    for tid, name, est, status in TASKS:
        s = {"pending": "[ ]", "doing":  "[~]", "done":  "[x]", "blocked": "[!]"}[status]
        print(f"  {tid:<6} {s:<10} {est:>4}m  {name}")
    print()
    print("=" * 70)
    print("  Press Ctrl+C to exit")
    print("=" * 70)

if __name__ == "__main__":
    try:
        while True:
            render()
            time.sleep(5)
    except KeyboardInterrupt:
        print("\n\nTracker stopped.")
        elapsed = time.time() - START_TIME
        print(f"Total elapsed: {elapsed/60:.1f} min")
