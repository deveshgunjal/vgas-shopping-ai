"""Bootstrap Database with Mock Data"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import init_db, SessionLocal
from app.models import User, ProductTrack, PriceHistory
from datetime import datetime, timedelta
import random

def seed():
    print("Seeding database...")
    init_db()
    db = SessionLocal()
    
    # Create demo user
    user = User(
        username="demo_user",
        email="demo@vgas.ai",
        phone="+919999999999",
        plan="free",
        referral_code="VGAS2024",
    )
    db.add(user)
    db.commit()
    
    # Create demo products
    products = [
        {"title": "iPhone 15 Pro Max 256GB", "url": "https://amazon.in/dp/B0CHX1W1XY", "store": "amazon", "price": 159900, "target": 179900},
        {"title": "Samsung Galaxy S24 Ultra", "url": "https://amazon.in/dp/B0CMDL4WP6", "store": "amazon", "price": 129999, "target": 149999},
        {"title": "Sony WH-1000XM5", "url": "https://amazon.in/dp/B09XS7JWHH", "store": "amazon", "price": 24990, "target": 34990},
        {"title": "MacBook Air M3", "url": "https://amazon.in/dp/B0CX23V2ZK", "store": "amazon", "price": 114900, "target": 134900},
        {"title": "OnePlus 12 5G", "url": "https://amazon.in/dp/B0CMDL5DPV", "store": "amazon", "price": 64999, "target": 69999},
    ]
    
    for p in products:
        track = ProductTrack(
            user_id=user.id,
            url=p["url"],
            title=p["title"],
            current_price=p["price"],
            target_price=p["target"],
            store=p["store"],
        )
        db.add(track)
        db.commit()
        
        # Add price history
        for i in range(30):
            history = PriceHistory(
                product_id=track.id,
                price=p["price"] + random.uniform(-5000, 5000),
                store=p["store"],
                recorded_at=datetime.utcnow() - timedelta(days=i),
            )
            db.add(history)
        db.commit()
    
    db.close()
    print("Database seeded with demo data!")

if __name__ == "__main__":
    seed()
