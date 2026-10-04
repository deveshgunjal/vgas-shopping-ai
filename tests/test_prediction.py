"""Prediction Engine Tests"""
import pytest
from datetime import datetime, timedelta
from app.prediction import price_predictor

@pytest.mark.anyio
async def test_predict_price_insufficient_history():
    history = [{"price": 100}] * 5
    result = await price_predictor.predict_price(history)
    assert "error" in result
    assert "at least 7 days" in result["error"]

@pytest.mark.anyio
async def test_predict_price_neutral():
    history = [
        {"price": 100, "date": "2026-08-01"},
        {"price": 100, "date": "2026-08-02"},
        {"price": 101, "date": "2026-08-03"},
        {"price": 99, "date": "2026-08-04"},
        {"price": 100, "date": "2026-08-05"},
        {"price": 100, "date": "2026-08-06"},
        {"price": 100, "date": "2026-08-07"},
    ]
    result = await price_predictor.predict_price(history)
    assert "error" not in result
    assert result["recommendation"] == "NEUTRAL"
    assert result["confidence"] >= 50

@pytest.mark.anyio
async def test_predict_price_wait():
    # Price is dropping rapidly, recommend WAIT
    history = [
        {"price": 150 - i * 5, "date": (datetime.utcnow() - timedelta(days=7-i)).isoformat()}
        for i in range(7)
    ]
    result = await price_predictor.predict_price(history)
    assert result["recommendation"] == "WAIT"

@pytest.mark.anyio
async def test_predict_price_buy_now():
    # Price is rising rapidly, recommend BUY_NOW
    history = [
        {"price": 100 + i * 5, "date": (datetime.utcnow() - timedelta(days=7-i)).isoformat()}
        for i in range(7)
    ]
    result = await price_predictor.predict_price(history)
    assert result["recommendation"] == "BUY_NOW"

@pytest.mark.anyio
async def test_get_best_time_to_buy():
    # 7 days of history, Wednesday has lowest price
    base_date = datetime.utcnow()
    # Find a Wednesday and make it cheap
    history = []
    for i in range(14):
        date_val = base_date - timedelta(days=i)
        day_name = date_val.strftime("%A")
        price = 50 if day_name == "Wednesday" else 100
        history.append({"price": price, "date": date_val.isoformat()})
        
    result = await price_predictor.get_best_time_to_buy(history)
    assert result["best_day"] == "Wednesday"
    assert result["avg_savings"] > 0
