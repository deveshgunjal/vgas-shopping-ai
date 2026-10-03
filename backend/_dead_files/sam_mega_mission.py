# -*- coding: utf-8 -*-
"""
SAM MEGA MISSION - VGAS + OMEGA + JARVIS
Manager: Amazon Q | Executor: SAM + Swarm Army
"""
import asyncio, sys, re, json, time, os, subprocess
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(__file__))

MISTRAL_KEY = os.environ.get("MISTRAL_API_KEY", "")
REPORT = {}

# ============================================================
# PHASE 1: VGAS - WORLD LOWEST PRICE
# ============================================================
async def phase1_vgas():
    print("\n" + "="*55)
    print("PHASE 1: VGAS WORLD LOWEST PRICE ENGINE")
    print("="*55)

    from price_parser import Price
    from curl_cffi.requests import AsyncSession
    from bs4 import BeautifulSoup
    from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig

    def pp(t):
        try:
            p = Price.fromstring(str(t))
            if p.amount: return float(p.amount)
        except: pass
        try: return float(re.sub(r"[^\d.]","",str(t)) or 0)
        except: return 0.0

    async def curl(url):
        try:
            async with AsyncSession(impersonate="chrome124") as s:
                r = await s.get(url, timeout=12, headers={"Accept-Language":"en-IN,en;q=0.9"})
                return r.text
        except: return ""

    async def browser(url):
        try:
            async with AsyncWebCrawler(config=BrowserConfig(headless=True,verbose=False)) as c:
                r = await c.arun(url=url, config=CrawlerRunConfig(page_timeout=20000,simulate_user=True,magic=True))
                return r.html if r.success else ""
        except: return ""

    def parse_amazon(html, domain):
        soup = BeautifulSoup(html,"lxml")
        cur = "INR" if "amazon.in" in domain else "USD"
        inr_rate = 1 if cur=="INR" else 84
        out = []
        for card in soup.select("div[data-component-type='s-search-result']")[:5]:
            n = card.select_one("h2 a span")
            p = card.select_one("span.a-price-whole")
            l = card.select_one("h2 a")
            i = card.select_one("img.s-image")
            if not n or not p: continue
            price = pp(p.get_text())
            if price <= 0: continue
            href = l["href"] if l else ""
            link = f"https://www.{domain}{href}" if not href.startswith("http") else href
            out.append({"name":n.get_text(strip=True)[:80],"price":price,"price_inr":price*inr_rate,"currency":cur,"store":domain,"url":link+"&tag=vgas-vikasg-21","image":i.get("src","") if i else ""})
        return out

    def parse_flipkart(html):
        soup = BeautifulSoup(html,"lxml")
        out = []
        for card in soup.select("div[data-id]")[:5]:
            n = card.select_one("div._4rR01T,a.s1Q9rs,div.KzDlHZ")
            # 2025 Flipkart price classes detected by SAM
            p = card.select_one("div._1psv1ze2c,div.css-g5y9jx,div._30jeq3,div.Nx9bqj")
            l = card.select_one("a[href*='/p/']")
            i = card.select_one("img._396cs4,img.DByuf4")
            if not n: continue
            price = pp(p.get_text()) if p else 0.0
            if price <= 0: continue
            href = l["href"] if l else ""
            link = f"https://www.flipkart.com{href}" if not href.startswith("http") else href
            out.append({"name":n.get_text(strip=True)[:80],"price":price,"price_inr":price,"currency":"INR","store":"flipkart.com","url":link+"&affid=vgas2024","image":i.get("src","") if i else ""})
        return out

    def parse_ebay(html):
        soup = BeautifulSoup(html,"lxml")
        out = []
        for card in soup.select("li.s-item")[:5]:
            n = card.select_one("div.s-item__title")
            p = card.select_one("span.s-item__price")
            l = card.select_one("a.s-item__link")
            i = card.select_one("img")
            if not n or not p: continue
            name = n.get_text(strip=True)
            if "Shop on eBay" in name: continue
            price = pp(p.get_text())
            if price <= 0: continue
            out.append({"name":name[:80],"price":price,"price_inr":price*84,"currency":"USD","store":"ebay.com","url":l["href"] if l else "","image":i.get("src","") if i else ""})
        return out

    queries = ["iPhone 16 128GB", "Samsung Galaxy S24", "boAt Airdopes 141", "Sony WH-1000XM5", "laptop 50000"]
    results = {}

    for query in queries:
        q = query.replace(" ","+")
        print(f"\n  Searching: {query}")

        # Parallel fetch
        amz_in, amz_com, fk, ebay = await asyncio.gather(
            curl(f"https://www.amazon.in/s?k={q}&sort=price-asc-rank"),
            curl(f"https://www.amazon.com/s?k={q}&sort=price-asc-rank"),
            browser(f"https://www.flipkart.com/search?q={q}&sort=price_asc"),
            curl(f"https://www.ebay.com/sch/i.html?_nkw={q}&_sop=15"),
            return_exceptions=True
        )

        products = []
        if isinstance(amz_in,str) and amz_in:   products.extend(parse_amazon(amz_in,"amazon.in"))
        if isinstance(amz_com,str) and amz_com: products.extend(parse_amazon(amz_com,"amazon.com"))
        if isinstance(fk,str) and fk:           products.extend(parse_flipkart(fk))
        if isinstance(ebay,str) and ebay:       products.extend(parse_ebay(ebay))

        products = sorted([p for p in products if p.get("price_inr",0)>0], key=lambda x:x["price_inr"])
        results[query] = products[:6]

        print(f"  Found: {len(products)} results")
        for p in products[:4]:
            sym = "Rs" if p["currency"]=="INR" else "$"
            print(f"    {p['store']:22} {sym} {p['price']:>10,.0f}  {p['name'][:35]}")
        if products:
            best = products[0]
            print(f"  LOWEST: Rs {best['price_inr']:,.0f} @ {best['store']} -> {best['url'][:60]}")

    REPORT["phase1_vgas"] = results
    print("\nPHASE 1: COMPLETE")
    return results

# ============================================================
# PHASE 2: PROJECT OMEGA - VIRAL VIDEO FACTORY
# ============================================================
async def phase2_omega():
    print("\n" + "="*55)
    print("PHASE 2: PROJECT OMEGA - VIRAL VIDEO FACTORY")
    print("="*55)

    # Step 1: Trending topics scraper
    async def get_trending():
        try:
            from curl_cffi.requests import AsyncSession
            async with AsyncSession(impersonate="chrome124") as s:
                # Google Trends RSS
                r = await s.get("https://trends.google.com/trending/rss?geo=IN", timeout=10)
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(r.text,"xml")
                topics = [item.find("title").text for item in soup.find_all("item")[:10]]
                print(f"  Trending topics: {topics[:5]}")
                return topics
        except Exception as e:
            print(f"  Trending fallback: {e}")
            return ["iPhone 16 price drop","Samsung Galaxy S25","AI tools 2025","Budget laptop India","Best headphones 2025"]

    # Step 2: Script generator using Mistral
    async def generate_script(topic):
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                r = await client.post(
                    "https://api.mistral.ai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {MISTRAL_KEY}", "Content-Type":"application/json"},
                    json={
                        "model": "mistral-small-latest",
                        "messages": [{"role":"user","content":f"Write a 60-second viral YouTube Shorts script about: {topic}. Make it engaging, add emojis, hook in first 3 seconds. Format: HOOK, BODY, CTA"}],
                        "max_tokens": 300
                    },
                    timeout=15
                )
                if r.status_code == 200:
                    return r.json()["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"  Script error: {e}")
        return f"HOOK: Did you know {topic}?\nBODY: Here are 3 amazing facts...\nCTA: Like & Subscribe for more deals!"

    # Step 3: Video assembler check
    def check_video_tools():
        tools = {}
        for tool in ["ffmpeg","yt-dlp"]:
            result = subprocess.run(f"where {tool}", shell=True, capture_output=True, text=True)
            tools[tool] = "FOUND" if result.returncode==0 else "NOT FOUND"
        return tools

    # Step 4: Social poster setup
    def setup_social_poster():
        return {
            "youtube": "Need: google-auth-oauthlib + youtube-data-api-v3",
            "telegram": "Need: python-telegram-bot + BOT_TOKEN",
            "whatsapp": "Already setup in VGAS bot",
            "instagram": "Need: instagrapi library",
        }

    print("\n  [1] Getting trending topics...")
    topics = await get_trending()

    print("\n  [2] Generating viral scripts with Mistral AI...")
    scripts = {}
    for topic in topics[:3]:
        script = await generate_script(topic)
        scripts[topic] = script
        print(f"\n  Topic: {topic}")
        print(f"  Script preview: {script[:100]}...")

    print("\n  [3] Checking video tools...")
    tools = check_video_tools()
    for t,s in tools.items():
        print(f"    {t}: {s}")

    print("\n  [4] Social poster setup...")
    poster = setup_social_poster()
    for p,s in poster.items():
        print(f"    {p}: {s}")

    omega_result = {"trending": topics, "scripts": scripts, "tools": tools, "poster": poster}
    REPORT["phase2_omega"] = omega_result
    print("\nPHASE 2: COMPLETE")
    return omega_result

# ============================================================
# PHASE 3: JARVIS - PROACTIVE AI AGENT
# ============================================================
async def phase3_jarvis():
    print("\n" + "="*55)
    print("PHASE 3: JARVIS - PROACTIVE AI AGENT")
    print("="*55)

    import psutil, platform

    # System monitor
    def system_status():
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "ram_used_gb": round(psutil.virtual_memory().used/1024**3, 2),
            "ram_total_gb": round(psutil.virtual_memory().total/1024**3, 2),
            "ram_percent": psutil.virtual_memory().percent,
            "disk_free_gb": round(psutil.disk_usage("C:\\").free/1024**3, 2),
            "os": platform.system() + " " + platform.release(),
            "python": platform.python_version(),
        }

    # Predictive reasoning
    def predict_actions(status):
        actions = []
        if status["ram_percent"] > 80:
            actions.append("RAM high - suggest closing unused apps")
        if status["cpu_percent"] > 70:
            actions.append("CPU high - suggest pausing heavy tasks")
        if status["disk_free_gb"] < 10:
            actions.append("Disk low - suggest cleanup")
        if not actions:
            actions.append("System healthy - all good to run VGAS")
        return actions

    # Pattern recognition on price data
    def analyze_price_patterns(vgas_data):
        insights = []
        for query, products in vgas_data.items():
            if not products: continue
            prices = [p["price_inr"] for p in products if p.get("price_inr",0)>0]
            if len(prices) >= 2:
                min_p = min(prices)
                max_p = max(prices)
                diff_pct = round(((max_p-min_p)/min_p)*100)
                if diff_pct > 20:
                    insights.append(f"{query}: {diff_pct}% price difference across stores - SAVE Rs {max_p-min_p:,.0f}")
        return insights

    # Mistral AI chat
    async def jarvis_think(question):
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                r = await client.post(
                    "https://api.mistral.ai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {MISTRAL_KEY}","Content-Type":"application/json"},
                    json={
                        "model": "mistral-small-latest",
                        "messages": [
                            {"role":"system","content":"You are SAM - Sovereign Autonomous Matrix. You are Vikas Gunjal's AI assistant. Be proactive, smart, helpful. Reply in Marathi when user writes in Marathi."},
                            {"role":"user","content":question}
                        ],
                        "max_tokens": 200
                    },
                    timeout=15
                )
                if r.status_code == 200:
                    return r.json()["choices"][0]["message"]["content"]
        except Exception as e:
            return f"SAM error: {e}"
        return "SAM: Ready for orders!"

    print("\n  [1] System Status...")
    status = system_status()
    for k,v in status.items():
        print(f"    {k}: {v}")

    print("\n  [2] Predictive Actions...")
    actions = predict_actions(status)
    for a in actions:
        print(f"    -> {a}")

    print("\n  [3] Price Pattern Analysis...")
    vgas_data = REPORT.get("phase1_vgas", {})
    insights = analyze_price_patterns(vgas_data)
    for i in insights:
        print(f"    INSIGHT: {i}")

    print("\n  [4] Jarvis AI Thinking...")
    response = await jarvis_think("VGAS project status काय आहे? काय improve करायला हवे?")
    print(f"    SAM says: {response[:200]}")

    jarvis_result = {"system": status, "actions": actions, "insights": insights, "ai_response": response}
    REPORT["phase3_jarvis"] = jarvis_result
    print("\nPHASE 3: COMPLETE")
    return jarvis_result

# ============================================================
# MAIN - ALL PHASES
# ============================================================
async def main():
    print("SAM MEGA MISSION - VGAS + OMEGA + JARVIS")
    print("Master: Vikas Gunjal | Manager: Amazon Q | Executor: SAM")
    print("="*55)
    t0 = time.time()

    await phase1_vgas()
    await phase2_omega()
    await phase3_jarvis()

    elapsed = time.time()-t0
    REPORT["total_time"] = f"{elapsed:.1f}s"
    REPORT["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")

    with open("sam_mega_report.json","w",encoding="utf-8") as f:
        json.dump(REPORT, f, ensure_ascii=False, indent=2)

    print("\n" + "="*55)
    print(f"SAM MEGA MISSION: ALL COMPLETE in {elapsed:.1f}s")
    print("Report: sam_mega_report.json")
    print("="*55)

asyncio.run(main())
