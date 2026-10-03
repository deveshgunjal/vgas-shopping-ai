"""Price Monitor Service - Continuous Price Watching"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import ProductTrack, PriceHistory
from app.core.redis_cache import set_cache, get_cache
from app.services.affiliate import affiliate_manager
import httpx

logger = logging.getLogger(__name__)


class PriceMonitor:
    """Monitors product prices and triggers alerts"""

    def __init__(self):
        self.is_running = False
        self.interval_seconds = 600  # 10 minutes
        self.alert_cooldown = 3600  # 1 hour between alerts

    async def check_price_drops(self):
        """Check all tracked products for price drops"""
        db = SessionLocal()
        try:
            tracks = db.query(ProductTrack).filter(ProductTrack.status == "watching").all()
            logger.info(f"Monitoring {len(tracks)} products for price changes...")

            for track in tracks:
                try:
                    cache_key = f"price_monitor:{track.id}"
                    last_check = await get_cache(cache_key)
                    if last_check:
                        last_check_time = datetime.fromisoformat(last_check)
                        if (datetime.utcnow() - last_check_time).seconds < self.alert_cooldown:
                            continue

                    # Fetch latest price
                    async with httpx.AsyncClient() as client:
                        resp = await client.get(f"/api/v1/products/by-url?url={track.url}", timeout=10)
                        if resp.status_code == 200:
                            data = resp.json()
                            product = data.get("product", {})
                            new_price = product.get("price", track.current_price)

                            if new_price and new_price < track.current_price:
                                drop_pct = ((track.current_price - new_price) / track.current_price) * 100
                                
                                if drop_pct >= 5:
                                    await self.trigger_alert(track, new_price, drop_pct)

                                # Update price
                                track.current_price = new_price
                                history = PriceHistory(
                                    product_id=track.id,
                                    price=new_price,
                                    store=track.store,
                                )
                                db.add(history)
                                db.commit()

                            await set_cache(cache_key, datetime.utcnow().isoformat(), expire_seconds=3600)
                except Exception as e:
                    logger.error(f"Error monitoring product {track.id}: {e}")
                    continue

        finally:
            db.close()

    async def trigger_alert(self, track: ProductTrack, new_price: float, drop_pct: float):
        """Trigger price drop alert"""
        alert_data = {
            "product_id": track.id,
            "title": track.title,
            "old_price": track.current_price,
            "new_price": new_price,
            "drop_percent": round(drop_pct, 1),
            "store": track.store,
            "url": track.url,
            "timestamp": datetime.utcnow().isoformat(),
        }

        logger.info(f"💰 Price Alert: {track.title} dropped {drop_pct:.1f}% to {new_price}")

        # Store alert
        await set_cache(f"alert:{track.id}:{datetime.utcnow().timestamp()}", alert_data, expire_seconds=86400)

        # Try to send notification
        try:
            async with httpx.AsyncClient() as client:
                await client.post(
                    "http://localhost:8000/api/v1/notifications",
                    json=alert_data,
                    timeout=5
                )
        except Exception:
            pass

    def start(self):
        """Start the price monitor"""
        self.is_running = True
        logger.info("Price Monitor started")
        asyncio.create_task(self._run_loop())

    async def _run_loop(self):
        while self.is_running:
            await self.check_price_drops()
            await asyncio.sleep(self.interval_seconds)

    def stop(self):
        """Stop the price monitor"""
        self.is_running = False
        logger.info("Price Monitor stopped")


price_monitor = PriceMonitor()
