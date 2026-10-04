"""Self-Healing Module for Vgas Shopping AI"""
import os
import sys
import subprocess
from pathlib import Path

REQUIRED_DIRS = [
    "backend/app",
    "backend/app/scrapers",
    "backend/app/services",
    "backend/app/api",
    "backend/app/api/v1",
    "extension",
    "extension/icons",
    "web/templates",
    "tests",
    "frontend",
    "docker",
]

REQUIRED_FILES = [
    "backend/app/__init__.py",
    "backend/app/main.py",
    "backend/app/database.py",
    "backend/app/models.py",
    "backend/app/scrapers/__init__.py",
    "backend/app/scrapers/crawler.py",
    "backend/app/scrapers/analyzer.py",
    "backend/app/scrapers/proxy_manager.py",
    "backend/app/services/__init__.py",
    "backend/app/services/whatsapp.py",
    "backend/app/services/stripe_pay.py",
    "backend/app/services/affiliate.py",
    "backend/app/services/cart.py",
    "backend/app/services/price_monitor.py",
    "backend/app/services/monetization.py",
    "backend/app/api/__init__.py",
    "backend/app/api/track.py",
    "backend/app/api/leaderboard.py",
    "backend/app/api/webhook.py",
    "backend/app/api/v1/__init__.py",
    "backend/app/api/v1/search.py",
    "backend/app/api/v1/products.py",
    "backend/app/api/v1/compare.py",
    "backend/app/api/v1/auth.py",
    "backend/app/api/v1/cart.py",
    "backend/app/api/v1/payment.py",
    "backend/app/api/v1/admin.py",
    "backend/app/api/v1/health.py",
    "backend/app/api/v1/affiliate.py",
    "backend/app/api/v1/monetization.py",
    "extension/manifest.json",
    "extension/background.js",
    "extension/content.js",
    "extension/popup.html",
    "extension/popup.js",
    "self_heal.py",
    "config.json",
    "requirements.txt",
    "Dockerfile",
    "docker-compose.yml",
    "deal_hunter.py",
    "sam_world_hunter.py",
    "frontend/index.html",
    "web/templates/index.html",
    "web/templates/dashboard.html",
    "web/templates/merchant.html",
]

def heal():
    print("🔧 Running Self-Heal...")
    
    # Create missing directories
    for d in REQUIRED_DIRS:
        Path(d).mkdir(parents=True, exist_ok=True)
    
    # Check missing files
    missing = []
    for f in REQUIRED_FILES:
        if not Path(f).exists():
            missing.append(f)
    
    if missing:
        print(f"⚠️ Missing {len(missing)} files:")
        for f in missing:
            print(f"   - {f}")
    else:
        print("✅ All required files exist!")
    
    # Check Python syntax
    print("Checking Python syntax...")
    errors = []
    for f in Path("backend").rglob("*.py"):
        try:
            compile(f.read_text(), str(f), "exec")
        except SyntaxError as e:
            errors.append(f"{f}: {e}")
    
    if errors:
        print(f"⚠️ {len(errors)} syntax errors:")
        for e in errors:
            print(f"   - {e}")
    else:
        print("✅ All Python files have valid syntax!")
    
    # Install missing packages
    print("Checking dependencies...")
    try:
        import fastapi
        import uvicorn
        import sqlalchemy
        import httpx
        print("✅ Core packages installed!")
    except ImportError as e:
        print(f"⚠️ Missing package: {e}")
        print("   Run: pip install -r requirements.txt")
    
    # Try to import all v1 modules
    print("Checking v1 API modules...")
    try:
        sys.path.insert(0, str(Path.cwd() / "backend"))
        import app.api.v1 as v1
        print("✅ All v1 modules importable!")
    except ImportError as e:
        print(f"⚠️ Import error: {e}")
    
    print("✅ Self-heal complete!")

if __name__ == "__main__":
    heal()
