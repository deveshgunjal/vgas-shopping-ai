"""
VGAS Deal Hunter Bot - Continuous Price Monitor
Monitors tracked products and alerts on deals
"""
import asyncio
import json
import logging
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "backend"))

from app.database import init_db, SessionLocal
from app.models import ProductTrack, PriceHistory, User
from app.scrapers.crawler import crawler
from app.core.redis_cache import set_cache, get_cache
from app.services.affiliate import affiliate_manager
from app.services.scheduler import scheduler_instance
import httpx

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("DealHunter")

DB_PATH = os.getenv("DATABASE_URL", "sqlite:///vgas_shopping.db")
ALERT_THRESHOLD = float(os.getenv("ALERT_THRESHOLD", "0.9"))
SCAN_INTERVAL = int(os.getenv("SCAN_INTERVAL", "300"))
ALERT_WEBHOOK = os.getenv("ALERT_WEBHOOK", "http://localhost:8000/api/v1/notifications")


class DealHunter:
    """Continuously monitors prices and alerts on deals"""

    def __init__(self):
        self.is_running = False
        self.scanned_count = 0
        self.deals_found = 0
        self.alerts_sent = 0

    async def init(self):
        """Initialize database and services"""
        init_db()
        logger.info("Deal Hunter initialized. Database ready.")

    async def scan_all_tracks(self):
        """Scan all tracked products for price changes"""
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
                        store = result.get("store", track.store)

                        # Update track
                        track.current_price = new_price
                        track.store = store
                        track.status = "watching"
                        db.commit()
                        db.refresh(track)

                        # Add to price history
                        history = PriceHistory(
                            product_id=track.id,
                            price=new_price,
                            store=store,
                        )
                        db.add(history)
                        db.commit()

                        self.scanned_count += 1

                        # Check for deal
                        if track.target_price > 0 and new_price <= track.target_price:
                            await self.trigger_deal_alert(track, new_price, old_price)
                            self.deals_found += 1

                        # Check for price drop > 10%
                        if old_price > 0 and new_price < old_price * 0.9:
                            await self.trigger_price_drop_alert(track, new_price, old_price)

                        await asyncio.sleep(1)  # Rate limit

                except Exception as e:
                    logger.error(f"Error scanning {track.url}: {e}")
                    continue

        finally:
            db.close()

    async def trigger_deal_alert(self, track: ProductTrack, price: float, old_price: float):
        """Send deal alert notification"""
        self.alerts_sent += 1
        alert = {
            "type": "DEAL_ALERT",
            "product_id": track.id,
            "title": track.title,
            "url": track.url,
            "price": price,
            "target_price": track.target_price,
            "store": track.store,
            "savings": round(track.target_price - price, 2),
            "timestamp": datetime.utcnow().isoformat(),
        }

        logger.info(f"🔥 DEAL ALERT: {track.title} is now {price} (target: {track.target_price})!")

        # Store alert in cache
        await set_cache(f"deal_alert:{track.id}:{datetime.utcnow().timestamp()}", alert, expire_seconds=86400)

        # Send webhook notification
        try:
            async with httpx.AsyncClient() as client:
                await client.post(ALERT_WEBHOOK, json=alert, timeout=10)
        except Exception as e:
            logger.error(f"Failed to send alert webhook: {e}")

        # Send WhatsApp notification if user has phone
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == track.user_id).first()
            if user and user.phone:
                await self.send_whatsapp_alert(user.phone, track, price)
        finally:
            db.close()

    async def trigger_price_drop_alert(self, track: ProductTrack, price: float, old_price: float):
        """Send price drop alert notification"""
        drop_pct = ((old_price - price) / old_price) * 100
        logger.info(f"📉 Price Drop: {track.title} dropped {drop_pct:.1f}% to {price}")

    async def send_whatsapp_alert(self, phone: str, track: ProductTrack, price: float):
        """Send WhatsApp alert via Twilio"""
        try:
            import httpx as htx
            twilio_sid = os.getenv("TWILIO_ACCOUNT_SID", "")
            twilio_token = os.getenv("TWILIO_AUTH_TOKEN", "")
            twilio_number = os.getenv("TWILIO_WHATSAPP_NUMBER", "")

            if not twilio_sid or not twilio_token:
                logger.warning("Twilio credentials not configured, skipping WhatsApp alert")
                return

            message = f"🔥 VGAS Deal Alert!\n\n{track.title}\nPrice: {price}\nStore: {track.store}\nTarget: {track.target_price}\n\nBuy now and save!"

            async with htx.AsyncClient() as client:
                await client.post(
                    "https://api.twilio.com/2010-04-01/Accounts/{}/Messages.json".format(twilio_sid),
                    auth=(twilio_sid, twilio_token),
                    data={
                        "To": f"whatsapp:{phone}",
                        "From": twilio_number,
                        "Body": message,
                    },
                    timeout=15,
                )
                logger.info(f"WhatsApp alert sent to {phone}")
        except Exception as e:
            logger.error(f"Failed to send WhatsApp alert: {e}")

    async def run(self):
        """Main loop"""
        await self.init()
        self.is_running = True
        logger.info("🚀 VGAS Deal Hunter started!")
        logger.info(f"Scan interval: {SCAN_INTERVAL}s")
        logger.info(f"Alert threshold: {ALERT_THRESHOLD}")

        while self.is_running:
            try:
                await self.scan_all_tracks()
                logger.info(
                    f"Scan complete. Scanned: {self.scanned_count}, "
                    f"Deals found: {self.deals_found}, Alerts sent: {self.alerts_sent}"
                )
            except Exception as e:
                logger.error(f"Error in scan cycle: {e}")

            await asyncio.sleep(SCAN_INTERVAL)

    def stop(self):
        """Stop the hunter"""
        self.is_running = False
        logger.info("Deal Hunter stopped.")


if __name__ == "__main__":
    hunter = DealHunter()
    try:
        asyncio.run(hunter.run())
    except KeyboardInterrupt:
        hunter.stop()
        logger.info("Deal Hunter terminated by user.")
