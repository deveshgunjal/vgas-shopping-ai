"""AI Price Analyzer & Validator"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta

class PriceAnalyzer:
    """Validates prices, detects fake discounts, calculates unit prices"""
    
    def validate_discount(self, original: float, current: float) -> Dict:
        """Validate if discount is genuine"""
        if not original or not current or original <= 0:
            return {"valid": False, "reason": "Invalid prices"}
        
        discount_pct = ((original - current) / original) * 100
        
        is_fake = False
        reason = ""
        
        # Fake discount detection
        if discount_pct > 80:
            is_fake = True
            reason = "Unrealistic discount (>80%)"
        elif discount_pct < 5:
            reason = "Minimal discount"
        
        return {
            "valid": not is_fake,
            "discount_percent": round(discount_pct, 1),
            "savings": round(original - current, 2),
            "reason": reason,
            "verdict": "FAKE" if is_fake else ("GOOD" if discount_pct > 30 else "OK"),
        }
    
    def calculate_unit_price(self, price: float, quantity: int, unit: str = "piece") -> Dict:
        """Calculate price per unit for comparison"""
        if quantity <= 0:
            return {"unit_price": price, "unit": unit}
        
        unit_price = price / quantity
        return {
            "unit_price": round(unit_price, 2),
            "total_price": price,
            "quantity": quantity,
            "unit": unit,
        }
    
    def is_good_price(self, current_price: float, history: List[float]) -> Dict:
        """Determine if current price is good based on history"""
        if not history:
            return {"verdict": "UNKNOWN", "reason": "No price history"}
        
        avg = sum(history) / len(history)
        min_price = min(history)
        max_price = max(history)
        
        if current_price <= min_price:
            return {"verdict": "BEST", "reason": "All-time low price!", "savings": round(max_price - current_price, 2)}
        elif current_price <= avg * 0.9:
            return {"verdict": "GOOD", "reason": f"Below average ({avg:.0f})"}
        elif current_price <= avg:
            return {"verdict": "OK", "reason": f"Around average ({avg:.0f})"}
        else:
            return {"verdict": "HIGH", "reason": f"Above average ({avg:.0f})", "overpay": round(current_price - avg, 2)}
    
    def calculate_discount_stack(self, base_price: float, coupons: List[Dict]) -> Dict:
        """Calculate final price after stacking all discounts"""
        total_discount = 0
        steps = [{"step": "Base Price", "amount": base_price}]
        
        for coupon in coupons:
            if coupon.get("type") == "percentage":
                discount = base_price * (coupon["value"] / 100)
            else:
                discount = coupon["value"]
            
            total_discount += discount
            steps.append({
                "step": f"Coupon: {coupon.get('code', 'N/A')}",
                "discount": round(discount, 2),
                "running_total": round(base_price - total_discount, 2),
            })
        
        final_price = max(0, base_price - total_discount)
        
        return {
            "original_price": base_price,
            "total_discount": round(total_discount, 2),
            "final_price": round(final_price, 2),
            "savings_percent": round((total_discount / base_price) * 100, 1) if base_price > 0 else 0,
            "steps": steps,
        }

analyzer = PriceAnalyzer()
