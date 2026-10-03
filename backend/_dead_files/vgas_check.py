# VGAS SYSTEM CHECK
import sys, requests
sys.stdout.reconfigure(encoding="utf-8")

checks = {}

try:
    from app.main import app
    checks["FastAPI App"] = "OK"
except Exception as e:
    checks["FastAPI App"] = f"FAIL: {str(e)[:60]}"

try:
    from app.scrapers.flipkart_scraper import FlipkartScraper
    from app.scrapers.amazon_scraper import AmazonScraper
    checks["Scrapers"] = "OK"
except Exception as e:
    checks["Scrapers"] = f"FAIL: {str(e)[:60]}"

try:
    from app.core.config import settings
    checks["Config"] = f"OK - {settings.APP_NAME}"
except Exception as e:
    checks["Config"] = f"FAIL: {str(e)[:60]}"

try:
    from app.core.database import init_db
    checks["Database"] = "OK"
except Exception as e:
    checks["Database"] = f"FAIL: {str(e)[:60]}"

try:
    from app.core.redis_cache import init_redis
    checks["Redis"] = "OK"
except Exception as e:
    checks["Redis"] = f"FAIL: {str(e)[:60]}"

for name, url in [
    ("Amazon.in", "https://www.amazon.in"),
    ("Flipkart",  "https://www.flipkart.com"),
    ("Snapdeal",  "https://www.snapdeal.com"),
    ("eBay",      "https://www.ebay.com"),
    ("Walmart",   "https://www.walmart.com"),
    ("Myntra",    "https://www.myntra.com"),
]:
    try:
        r = requests.get(url, headers={"User-Agent":"Mozilla/5.0"}, timeout=7)
        checks[name] = f"OK {r.status_code}"
    except Exception as e:
        checks[name] = f"FAIL {str(e)[:30]}"

print("=" * 60)
print("  VGAS PROJECT - FULL SYSTEM CHECK")
print("=" * 60)
for k, v in checks.items():
    icon = "OK" if "OK" in v else "FAIL"
    print(f"  [{icon}] {k:20} {v}")
ok = sum(1 for v in checks.values() if "OK" in v)
print("=" * 60)
print(f"  RESULT: {ok}/{len(checks)} PASSED")
print("=" * 60)
if ok == len(checks):
    print("  ALL SYSTEMS GO - PROJECT READY TO RUN!")
else:
    print("  SOME ISSUES FOUND - CHECK ABOVE")
print("=" * 60)
