"""Scrapers module for VGAS Shopping AI"""
from app.scrapers.amazon_scraper import AmazonScraper
from app.scrapers.flipkart_scraper import FlipkartScraper
from app.scrapers.myntra_scraper import MyntraScraper
from app.scrapers.ajio_scraper import AjioScraper
from app.scrapers.global_scrapers import GlobalScrapers

def get_scraper(domain_or_name: str):
    """Factory function to get appropriate scraper for a domain or name"""
    domain = domain_or_name.lower()
    if "amazon" in domain:
        return AmazonScraper()
    elif "flipkart" in domain:
        return FlipkartScraper()
    elif "myntra" in domain:
        return MyntraScraper()
    elif "ajio" in domain:
        return AjioScraper()
    
    # Check in GlobalScrapers
    return GlobalScrapers.get_scraper(domain)
