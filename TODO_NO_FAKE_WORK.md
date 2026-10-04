# VGAS Shopping-AI — "No Fake Work" TODO

Status: [x] done & verified | [~] in progress | [ ] pending | [!] blocked

## STEP 1 — Live click test  [x] 9/9 PASS
Real Playwright clicks + real keystrokes (`press_sequentially`).
Test accepts exactly two honest outcomes for the product step: a real product
card, or the honest empty state. A sample product is never a pass condition.

## STEP 2 — Real backend API  [x]
- `/api/v1/search/?query=iPhone 15` -> **5 REAL Amazon products, live prices**
  (`time=4.04s`, `stores_count=1`)
- `/api/v1/products/by-url?url=<amazon>` -> **live product name + affiliate URL
  with `tag=vgas-vikasg-21`**, `from_cache=false`
- `/api/v1/search/categories`, `/search/stores`, `/admin/stats`,
  `/admin/products`, `/admin/users`, `/admin/revenue`, `/health/status` — 200
- `[x]` Playwright async API is NOT the blocker — it works standalone and in the
  server. Scraping now returns real rows.

## STEP 3 — SAM-LLM Smart Brain  [x] STATUS complete, 3/3 VERIFIED REAL

## STEP 4 — Android APK  [x] BUILD SUCCESSFUL
- `app/build/outputs/apk/debug/app-debug.apk` — **30.66 MB**
- `package=com.aistudio.shoppingai.kxmpzq`, `versionCode=1`, `minSdk=24`,
  `targetSdk=36`, launchable `com.example.MainActivity`
- Signed: `CN=Android Debug, O=Android, C=US`
- Real build fixes applied: removed foojay resolver (network-blocked), added
  `credentials-play-services` version, generated missing `debug.keystore`,
  wrote `local.properties`, `org.gradle.java.installations.auto-download=false`
- Real Kotlin compile fixes: `Alignment.Baseline` -> `CenterVertically`,
  missing `clickable` import, `MainScreen`/`HomeScreen` signature mismatch.

## STEP 5 — WhatsApp bot  [~] runs, QR printed; `!loot` needs user's phone scan

## FAKE-WORK AUDIT — all found items fixed and verified live
| # | Where | Fake | Fix |
|---|-------|------|-----|
| 1 | `ProductDetailScreen.jsx` | hardcoded iPhone 15 Pro Max | live by-id / by-url |
| 2 | `CompareScreen.jsx` | static 3 products | live URL-paste compare |
| 3 | `AdminDashboardScreen.jsx` + `admin.py` | static deals/trend/scraper, Rs 234000 hardcoded revenue | real DB math, single-source plan prices |
| 4 | `ProfileScreen.jsx` | mock "Arun Kumar", fake earnings, `alert("(mock)")`, fake logout | `GET /auth/me` + real `POST /auth/logout` |
| 5 | `HomeScreen.jsx` | `trending` fallback, "10 Crore+/50+/500K+", `rating \|\| "4.2"`, `store \|\| "Amazon"`, `id \|\| 1`, fake "Free Delivery" | all removed; honest empty state |
| 6 | `payment.py` `/verify` | **returned `verified:true` for ANY payment id** | real Stripe `Session.retrieve`; `unverified` otherwise |
| 7 | `payment.py` `/upi` | fake `payment_id`, claimed "payment initiated" | real `upi://pay` intent, `status:"unverified"`, no gateway claim |
| 8 | `monetization.py` | fake ad URLs (`vgas.ai/ads/banner1.png`), `sample_product`, "payout in 5 minutes" | `enabled:false` + explicit reason; cashback = rate estimate only |
| 9 | `webhook.py` `/api/v1/payment/upi` | **any self-reported UTR instantly upgraded the account to Pro/Premium** | HTTP 501, no plan granted, says exactly what integration is required |
| 10 | `admin.py` unit bug | plan prices hardcoded in rupees while `PLANS` stores paise | imports `stripe_pay.PLANS`, `/100` |
| 11 | `ShoppingEntity.kt` `TrackedProduct` | `reviewScore=4.5`, `reviewCount=1250`, `qualityScore=92`, `sellerName="Verified Retailer"`, `couponCode="LOOT500"`, computed cashback | 0 / `""` = "not reported" |
| 12 | `ShoppingUiState` | `totalCommissionEarned=4850`, `affiliateClicksCount=1420`, `conversionRate=3.4%`, `appVersion="v2.5.0 Pro"`, `isBotOnline=true` | all 0/false + `areCommissionStatsLoaded` gate |
| 13 | `ShoppingViewModel.analyzeAndScrapeUrl` | `"Verified genuine discount"`, `rating 4.5`, `quality 90`, `coupon "VGAS-API"`, `category "Electronics"`, fabricated price history | read straight from response; blank/0 when absent |
| 14 | Android `HomeScreen.kt` | stale no-arg screen, "10 Crore+ products", "52 Stores", fake trending chips | rewritten to render real `ShoppingUiState` |
| 15 | Android `ProductDetailScreen.kt` | hardcoded `₹1,34,990`, `4.5 (2,341 reviews)`, 3 fake store price rows | rewritten to render real `TrackedProduct`, "not reported" rows |
| 16 | `HomeScreen.jsx` / `ProductDetailScreen.jsx` | scraper returns `price: 0.0` on parse failure but UI rendered "₹0" | 0/null renders "price unavailable" |
| 17 | `HomeScreen.jsx` | search scrapers put the product **URL in `id`**, so the Details link was `/product/https://…` | detects non-numeric id -> `/product/live?url=…` |

## STILL BLOCKED / HONESTLY EMPTY
- [!] `/search/loot-deals` and `/search/trending` scan many queries at once and
      exceed the 45 s client budget, so Home shows the honest empty state.
      Single-query search works and returns real rows.
- [!] Some scrapes return `price: 0.0` — the store page markup changed or the
      price element was not found. The UI now says "not parsed" instead of
      inventing a price.
- [!] No payment ledger table, no UPI-capable gateway, no `STRIPE_SECRET_KEY`.
      Real plan upgrades therefore only work through Stripe checkout +
      signature-verified webhook.
- [!] WhatsApp `!loot` needs the user to scan the terminal QR.

## KNOWN, INTENTIONAL EMPTY-STATE MESSAGES (not fakes)
`No live products returned` (Home), `No product selected` / `not reported`
(Android PDP), `Not logged in` (Profile), `upi_verification_unavailable`.
