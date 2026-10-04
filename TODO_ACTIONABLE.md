# VGAS Shopping-AI — Actionable TODO

Created: 2026-10-04
Status: [ ] pending | [~] in progress | [x] done | [!] blocked

---

## COMPLETED (verified in code today)

- [x] **B** DadGPT.bat one-click launcher — 5/5 PASS
- [x] **B** Boot preload scheduled task `DadGPT_BootPreload` — Ready
- [x] **C** Dead keys removed from `keys.txt` — 19 removed, 39 LIVE intact, 0 lost
- [x] Fake-work items 1-9, 10-17 — all genuinely fixed in code (payment verify, UPI, monetization, webhook, admin, Kotlin, React)

---

## PENDING — 3 real bugs

### BUG 1: Home shows "No live products returned"  [ ] ~30 min
**Root cause:** `/search/loot-deals` and `/search/trending` scrape many queries at once, exceed the 45s client budget, so Home shows the honest empty state.

**Fix:** Add Redis cache layer so results persist between requests.
- [ ] Wire `loot-deals` results into Redis with 10-min TTL
- [ ] Wire `trending` results into Redis with 10-min TTL
- [ ] Serve stale-while-revalidate pattern (return cached immediately, refresh in background)
- [ ] Verify: second page load is instant

**Files:** `backend/app/api/v1/search.py`, `backend/app/core/redis_cache.py`

---

### BUG 2: Scrapes return `price: 0.0`  [ ] ~45 min
**Root cause:** Store page markup changed, CSS selectors no longer find the price element.

**Fix:** Update per-store CSS selectors.
- [ ] Read current scraper code in `backend/app/scrapers/`
- [ ] Test selectors against live store pages
- [ ] Update broken selectors (Amazon + ~6 other stores)
- [ ] Verify: real prices returned, not 0.0

**Files:** `backend/app/scrapers/__init__.py` and per-store modules

---

### BUG 3: Stripe checkout is dead code  [ ] BLOCKED
**Root cause:** No `STRIPE_SECRET_KEY` in environment.

**Fix:** Cannot fix without a real Stripe secret key from the user.
- [ ] User provides `STRIPE_SECRET_KEY`
- [ ] Add to `.env` (never commit)
- [ ] Test checkout flow end-to-end

**Files:** `backend/app/services/stripe_pay.py`, `.env`

---

## NOT STARTED — lower priority

- [ ] VGAS git commit + push (77 uncommitted files — risk of losing work)
- [ ] WhatsApp `!loot` test (needs user's phone QR scan)
- [ ] Payment ledger table (needed for UPI verification)
- [ ] UPI-capable payment gateway integration (Razorpay/Cashfree)

---

## Order to work in

1. **BUG 1** (Redis cache) — biggest user-visible impact, ~30 min
2. **BUG 2** (price selectors) — ~45 min
3. **BUG 3** (Stripe) — blocked on user
4. Git commit + push — protect the work
