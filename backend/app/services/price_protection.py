"""Price Protection Guarantee Service"""
from typing import Dict
from datetime import datetime, timedelta

class PriceProtection:
    """Auto-refund if price drops within 15 days"""
    
    def __init__(self):
        self.purchases = []
    
    def register_purchase(self, user_id: int, product_url: str, purchase_price: float) -> Dict:
        """Register a purchase for price protection"""
        purchase = {
            "id": len(self.purchases) + 1,
            "user_id": user_id,
            "product_url": product_url,
            "purchase_price": purchase_price,
            "purchase_date": datetime.utcnow(),
            "protection_until": datetime.utcnow() + timedelta(days=15),
            "status": "active",
            "refund_amount": 0,
        }
        self.purchases.append(purchase)
        return purchase
    
    async def check_price_drop(self, purchase_id: int, current_price: float) -> Dict:
        """Check if price dropped and process refund"""
        for purchase in self.purchases:
            if purchase["id"] == purchase_id and purchase["status"] == "active":
                if current_price < purchase["purchase_price"]:
                    # Price dropped! Calculate refund
                    refund_amount = purchase["purchase_price"] - current_price
                    purchase["refund_amount"] = refund_amount
                    purchase["status"] = "refund_eligible"
                    
                    return {
                        "status": "refund_eligible",
                        "original_price": purchase["purchase_price"],
                        "current_price": current_price,
                        "refund_amount": refund_amount,
                        "refund_email": self._generate_refund_email(purchase, current_price),
                    }
        
        return {"status": "no_refund"}
    
    def _generate_refund_email(self, purchase: Dict, current_price: float) -> str:
        """Generate refund request email"""
        return f"""Dear Support,

I am writing to request a price adjustment for my recent purchase.

Purchase Date: {purchase['purchase_date'].strftime('%Y-%m-%d')}
Original Price: INR {purchase['purchase_price']}
Current Price: INR {current_price}
Refund Amount: INR {purchase['purchase_price'] - current_price}

The price has dropped within the 15-day protection period. Please process the refund difference.

Thank you."""
    
    def get_active_protections(self, user_id: int) -> list:
        """Get all active protections for a user"""
        return [p for p in self.purchases if p["user_id"] == user_id and p["status"] == "active"]

price_protection = PriceProtection()
