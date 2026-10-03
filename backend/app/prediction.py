"""AI Price Prediction Engine - Prophet/ARIMA"""
from typing import Dict, List
from datetime import datetime, timedelta
import random

class PricePredictor:
    """Predict future prices using time-series forecasting"""
    
    def __init__(self):
        self.model = None
    
    async def predict_price(self, price_history: List[Dict], days_ahead: int = 14) -> Dict:
        """Predict price for next N days"""
        valid_history = []
        for p in price_history:
            if isinstance(p, dict):
                price = p.get("price")
            else:
                price = getattr(p, "price", None)
            if price is not None:
                valid_history.append(price)
                
        if len(valid_history) < 7:
            return {"error": "Need at least 7 days of history"}
        
        prices = [float(p) for p in valid_history]
        avg_price = sum(prices) / len(prices)
        min_price = min(prices)
        max_price = max(prices)
        current_price = prices[-1]
        
        # Simple prediction (would use Prophet in production)
        trend = (prices[-1] - prices[0]) / len(prices)
        predicted_price = current_price + (trend * days_ahead)
        predicted_price = max(min_price * 0.8, min(max_price * 1.2, predicted_price))
        
        # Calculate recommendation
        if predicted_price < current_price * 0.95:
            recommendation = "WAIT"
            reason = f"Price predicted to drop {((current_price - predicted_price) / current_price * 100):.1f}% in {days_ahead} days"
        elif predicted_price > current_price * 1.05:
            recommendation = "BUY_NOW"
            reason = f"Price predicted to rise {((predicted_price - current_price) / current_price * 100):.1f}% in {days_ahead} days"
        else:
            recommendation = "NEUTRAL"
            reason = "Price expected to remain stable"
        
        return {
            "current_price": current_price,
            "predicted_price": round(predicted_price, 2),
            "recommendation": recommendation,
            "reason": reason,
            "confidence": min(95, max(50, 100 - abs(trend) * 10)),
            "price_range": {
                "low": round(min_price * 0.95, 2),
                "high": round(max_price * 1.05, 2),
            }
        }
    
    async def get_best_time_to_buy(self, price_history: List[Dict]) -> Dict:
        """Determine best day of week to buy"""
        # Analyze historical patterns
        day_prices = {}
        for p in price_history:
            if isinstance(p, dict):
                price = p.get("price")
                date_val = p.get("date") or p.get("recorded_at")
            else:
                price = getattr(p, "price", None)
                date_val = getattr(p, "recorded_at", None) or getattr(p, "date", None)
            
            if price is None or date_val is None:
                continue
                
            if isinstance(date_val, str):
                try:
                    dt = datetime.fromisoformat(date_val)
                except ValueError:
                    continue
            elif isinstance(date_val, datetime):
                dt = date_val
            else:
                continue
                
            day = dt.strftime("%A")
            if day not in day_prices:
                day_prices[day] = []
            day_prices[day].append(float(price))
        
        if not day_prices:
            return {
                "best_day": "Unknown",
                "avg_savings": 0.0,
                "day_averages": {},
            }
            
        avg_by_day = {day: sum(prices)/len(prices) for day, prices in day_prices.items()}
        best_day = min(avg_by_day, key=avg_by_day.get)
        
        return {
            "best_day": best_day,
            "avg_savings": round(max(avg_by_day.values()) - min(avg_by_day.values()), 2),
            "day_averages": avg_by_day,
        }

price_predictor = PricePredictor()
