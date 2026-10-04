"""
VGAS World Deal Hunter - Main Script
Continuously monitors prices and alerts on deals
"""
import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "backend"))

from app.database import init_db, SessionLocal
from app.models import ProductTrack, PriceHistory, User
from app.scrapers.crawler import crawler
from app.core.redis_cache import set_cache, get_cache
from app.services.affiliate import affiliate_manager
from app.services.price_monitor import price_monitor
import httpx

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("VGAS-Hunter")

SCAN_INTERVAL = int(os.getenv("SCAN_INTERVAL", "300"))
ALERT_WEBHOOK = os.getenv("ALERT_WEBHOOK", "http://localhost:8000/api/v1/notifications")


async def main():
    """Main entry point for the deal hunter"""
    logger.info("=" * 60)
    logger.info("  VGAS World Deal Hunter - Starting")
    logger.info("=" * 60)
    
    # Initialize database
    init_db()
    logger.info("Database initialized.")
    
    # Start price monitor
    price_monitor.start()
    logger.info("Price monitor activated.")
    
    # Main loop
    while True:
        try:
            db = SessionLocal()
            try:
                tracks = db.query(ProductTrack).filter(
                    ProductTrack.status == "watching"
                ).all()
                logger.info(f"Scanning {len(tracks)} tracked products...")
                
                for track in tracks:
                    try:
                        result = await crawler.crawl(track.url)
                        if result and result.get("price"):
                            new_price = result["price"]
                            old_price = track.current_price
                            
                            if new_price != old_price:
                                track.current_price = new_price
                                db.commit()
                                db.refresh(track)
                                
                                history = PriceHistory(
                                    product_id=track.id,
                                    price=new_price,
                                    store=result.get("store", track.store),
                                )
                                db.add(history)
                                db.commit()
                                
                                logger.info(
                                    f"📊 {track.title}: {old_price} -> {new_price}"
                                )
                                
                                if track.target_price > 0 and new_price <= track.target_price:
                                    logger.info(
                                        f"🔥 DEAL! {track.title} hit target price: {new_price}"
                                    )
                                    
                                    alert_data = {
                                        "type": "DEAL",
                                        "product": track.title,
                                        "price": new_price,
                                        "target": track.target_price,
                                        "store": track.store,
                                        "url": track.url,
                                        "timestamp": datetime.utcnow().isoformat(),
                                    }
                                    await set_cache(
                                        f"deal:{track.id}:{datetime.utcnow().timestamp()}",
                                        alert_data,
                                        expire_seconds=86400,
                                    )
                                    
                        await asyncio.sleep(2)
                    except Exception as e:
                        logger.error(f"Error scanning product: {e}")
                        continue
            finally:
                db.close()
            
            await asyncio.sleep(SCAN_INTERVAL)
            
        except KeyboardInterrupt:
            logger.info("Deal Hunter stopped by user.")
            break
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            await asyncio.sleep(60)


if __name__ == "__main__":
    asyncio.run(main())
