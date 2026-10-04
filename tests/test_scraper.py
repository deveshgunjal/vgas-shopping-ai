"""Scraper Tests"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

import pytest
from app.scrapers.analyzer import analyzer

def test_validate_discount_good():
    result = analyzer.validate_discount(1000, 500)
    assert result["valid"] is True
    assert result["discount_percent"] == 50.0

def test_validate_discount_fake():
    result = analyzer.validate_discount(1000, 100)
    assert result["valid"] is False

def test_is_good_price():
    history = [100, 110, 90, 105, 95]
    result = analyzer.is_good_price(80, history)
    assert result["verdict"] == "BEST"

def test_calculate_discount_stack():
    coupons = [
        {"code": "SAVE10", "type": "percentage", "value": 10},
        {"code": "FLAT100", "type": "fixed", "value": 100},
    ]
    result = analyzer.calculate_discount_stack(1000, coupons)
    assert result["final_price"] == 800
    assert result["savings_percent"] == 20.0
