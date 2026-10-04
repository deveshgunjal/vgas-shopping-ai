# -*- coding: utf-8 -*-
"""
VGAS COMPLETE PRODUCTION SETUP
सर्व काम एकत्र - Ready to Deploy
"""
import subprocess, sys, time, os, json
sys.stdout.reconfigure(encoding="utf-8")

print("="*80)
print("🚀 VGAS PRODUCTION SETUP - FINAL BUILD")
print("="*80)

# 1. CREATE REQUIREMENTS.TXT
print("\n[1/5] Creating requirements.txt...")
reqs = """fastapi==0.139.0
uvicorn==0.50.2
crawl4ai==0.9.2
beautifulsoup4==4.15.0
requests==2.34.2
lxml==6.1.1
redis==8.1.0
sqlalchemy==2.0.51
pydantic==2.13.4
python-dotenv==1.2.2
aiohttp==3.13.5
aiofiles==25.1.0
"""
with open("D:\\Sam\\Vgas Shooping Ai\\backend\\requirements.txt", "w") as f:
    f.write(reqs)
print("✅ requirements.txt created")

# 2. CREATE .ENV FILE
print("\n[2/5] Creating .env configuration...")
env = """APP_NAME=VGAS Shopping AI
APP_VERSION=2.5.0
DEBUG=True
PORT=8000

POSTGRES_USER=postgres
POSTGRES_PASSWORD=vgas2024
POSTGRES_DB=vgas_shopping
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

REDIS_URL=redis://localhost:6379/0

GEMINI_API_KEY=your_gemini_key
OPENAI_API_KEY=your_openai_key

AMAZON_AFFILIATE_ID=vgas-vikasg-21
FLIPKART_AFFILIATE_ID=vgas2024

WHATSAPP_BOT_TOKEN=your_whatsapp_token
WHATSAPP_PHONE_NUMBER=919881300933

PAYPAL_BUSINESS_EMAIL=gunjalvikas786@gmail.com
PAYPAL_API_CLIENT_ID=your_paypal_id
PAYPAL_API_SECRET=your_paypal_secret
PAYPAL_MODE=sandbox

SECRET_KEY=vgas-super-secret-key-2024

AUTHOR_NAME=Vikas Gunjal
AUTHOR_EMAIL=gunjalvikas786@gmail.com
CONTACT_PHONE=+91 9881300933
COMPANY_NAME=VGAS - Vikas Gunjal Advance System
LOCATION=Chhatrapati Sambhaji Nagar, Maharashtra, India
"""
with open("D:\\Sam\\Vgas Shooping Ai\\backend\\.env", "w") as f:
    f.write(env)
print("✅ .env created")

# 3. CREATE STARTUP SCRIPT
print("\n[3/5] Creating startup scripts...")
startup_bat = """@echo off
chcp 65001 >nul
title VGAS Shopping AI Backend
color 0A

cd /d "D:\\Sam\\Vgas Shooping Ai\\backend"

echo ============================================================
echo   VGAS SHOPPING AI - BACKEND SERVER
echo ============================================================
echo.
echo Starting on http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.

python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

pause
"""
with open("D:\\Sam\\Vgas Shooping Ai\\run_backend.bat", "w") as f:
    f.write(startup_bat)
print("✅ run_backend.bat created")

# 4. CREATE DEAL HUNTER RUNNER
print("\n[4/5] Creating deal hunter runner...")
runner = """@echo off
chcp 65001 >nul
title VGAS World Deal Hunter
color 0B

cd /d "D:\\Sam\\Vgas Shooping Ai\\backend"

echo ============================================================
echo   VGAS WORLD DEAL HUNTER - RUNNING
echo ============================================================
echo.

python sam_world_hunter.py

echo.
echo Results saved to: vgas_world_deals.json
pause
"""
with open("D:\\Sam\\Vgas Shooping Ai\\run_deal_hunter.bat", "w") as f:
    f.write(runner)
print("✅ run_deal_hunter.bat created")

# 5. CREATE README
print("\n[5/5] Creating README...")
readme = """# VGAS Shopping AI - Global Price Comparison Platform

## Quick Start

### 1. Install Dependencies
```bash
cd "D:\\Sam\\Vgas Shooping Ai\\backend"
pip install -r requirements.txt
playwright install chromium
```

### 2. Run Backend Server
```bash
python -m uvicorn app.main:app --reload --port 8000
```
Or double-click: `D:\\Sam\\Vgas Shooping Ai\\run_backend.bat`

### 3. Run Deal Hunter
```bash
python sam_world_hunter.py
```
Or double-click: `D:\\Sam\\Vgas Shooping Ai\\run_deal_hunter.bat`

## API Endpoints

- **Health Check**: http://localhost:8000/
- **API Docs**: http://localhost:8000/docs
- **Search**: http://localhost:8000/api/v1/search/?query=iPhone
- **Compare**: http://localhost:8000/api/v1/compare/
- **AI Chat**: http://localhost:8000/api/v1/ai/chat

## Features

✅ Global price comparison (100+ stores)
✅ Fake discount detection
✅ Multi-language support (24+ languages)
✅ Affiliate link generation
✅ WhatsApp bot integration
✅ Price alerts
✅ Real-time scraping

## Platforms Supported

- Amazon (India, USA, UK, Germany, Japan, UAE)
- Flipkart
- Snapdeal
- Myntra
- eBay
- Walmart
- Meesho
- Croma
- And 90+ more stores

## Monetization

- Affiliate commissions (4-10%)
- Ad revenue
- VIP membership
- Referral program

## Support

Email: gunjalvikas786@gmail.com
Phone: +91 9881300933
"""
with open("D:\\Sam\\Vgas Shooping Ai\\README_QUICK_START.md", "w") as f:
    f.write(readme)
print("✅ README_QUICK_START.md created")

print("\n" + "="*80)
print("✅ VGAS PRODUCTION SETUP COMPLETE!")
print("="*80)
print("""
📁 FILES CREATED:
  1. requirements.txt - All dependencies
  2. .env - Configuration
  3. run_backend.bat - Start backend server
  4. run_deal_hunter.bat - Run deal hunter
  5. README_QUICK_START.md - Quick start guide

🚀 TO RUN PROJECT:

  Option 1 (Easy - Windows):
    Double-click: D:\\Sam\\Vgas Shooping Ai\\run_backend.bat
    
  Option 2 (Manual):
    cd D:\\Sam\\Vgas Shooping Ai\\backend
    python -m uvicorn app.main:app --reload --port 8000

🌍 TO RUN DEAL HUNTER:
    Double-click: D:\\Sam\\Vgas Shooping Ai\\run_deal_hunter.bat
    Or: python sam_world_hunter.py

📊 RESULTS:
    - Backend: http://localhost:8000
    - API Docs: http://localhost:8000/docs
    - Deals JSON: vgas_world_deals.json

✅ ALL SYSTEMS READY - PROJECT COMPLETE!
""")
print("="*80)
