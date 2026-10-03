"""
Configuration settings for VGAS Shopping AI Backend
"""

from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List, Optional
import os


class Settings(BaseSettings):
    """Application settings"""

    # App Info
    APP_NAME: str = "VGAS Shopping AI"
    APP_VERSION: str = "2.5.0"
    AUTHOR_NAME: str = "Vikas Gunjal"
    AUTHOR_EMAIL: str = "gunjalvikas786@gmail.com"
    COMPANY_NAME: str = "VGAS - Vikas Gunjal Advance System"
    LOCATION: str = "Chhatrapati Sambhaji Nagar, Maharashtra, India"
    CONTACT_PHONE: str = "+91 9881300933"
    WEBSITE: str = "https://vgas-app.com"

    # Server Configuration
    DEBUG: bool = True
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    @field_validator("DEBUG", mode="before")
    @classmethod
    def parse_debug(cls, v):
        if isinstance(v, str):
            return v.lower() not in ("false", "0", "no", "release")
        return bool(v)

    # Database Configuration
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "password")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "vgas_shopping")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT", "5432"))

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    # Redis Configuration
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    REDIS_PASSWORD: Optional[str] = os.getenv("REDIS_PASSWORD", None)

    # API Keys
    KIMI_K3_API_KEY: Optional[str] = os.getenv(
        "KIMI_K3_API_KEY", "qVgvfCGdGPpcBph2QKC9U3dnEo5cQmlA"
    )
    MOONSHOT_API_KEY: Optional[str] = os.getenv(
        "MOONSHOT_API_KEY", "qVgvfCGdGPpcBph2QKC9U3dnEo5cQmlA"
    )
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY", None)
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY", None)

    # Affiliate Configuration
    AMAZON_AFFILIATE_ID: str = os.getenv("AMAZON_AFFILIATE_ID", "vgas-vikasg-21")
    FLIPKART_AFFILIATE_ID: Optional[str] = os.getenv("FLIPKART_AFFILIATE_ID", None)
    EARNKARO_API_KEY: Optional[str] = os.getenv("EARNKARO_API_KEY", None)
    CUELINKS_API_KEY: Optional[str] = os.getenv("CUELINKS_API_KEY", None)

    # WhatsApp Bot Configuration
    WHATSAPP_BOT_TOKEN: Optional[str] = os.getenv("WHATSAPP_BOT_TOKEN", None)
    WHATSAPP_PHONE_NUMBER: str = os.getenv("WHATSAPP_PHONE_NUMBER", "919881300933")
    WHATSAPP_WEBHOOK_URL: str = os.getenv(
        "WHATSAPP_WEBHOOK_URL", "http://localhost:8000/api/v1/whatsapp/webhook"
    )

    # PayPal Configuration
    PAYPAL_BUSINESS_EMAIL: str = os.getenv(
        "PAYPAL_BUSINESS_EMAIL", "gunjalvikas786@gmail.com"
    )
    PAYPAL_API_CLIENT_ID: Optional[str] = os.getenv("PAYPAL_API_CLIENT_ID", None)
    PAYPAL_API_SECRET: Optional[str] = os.getenv("PAYPAL_API_SECRET", None)
    PAYPAL_MODE: str = os.getenv("PAYPAL_MODE", "sandbox")  # sandbox or live

    # Currency & Exchange Rate
    CURRENCY_API_KEY: Optional[str] = os.getenv("CURRENCY_API_KEY", None)
    EXCHANGE_RATE_API: str = os.getenv(
        "EXCHANGE_RATE_API", "https://api.exchangerate-api.com/v4/latest/USD"
    )
    DEFAULT_CURRENCY: str = "INR"
    SUPPORTED_CURRENCIES: List[str] = [
        "INR",
        "USD",
        "EUR",
        "GBP",
        "AED",
        "CAD",
        "AUD",
        "SGD",
        "SAR",
        "QAR",
    ]

    # Scraper Configuration
    MAX_CONCURRENT_SCRAPERS: int = 10
    SCRAPER_TIMEOUT: int = 20
    # Real browser User-Agent so e-commerce sites don't block us as a bot
    USER_AGENT: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"

    # Supported Countries & Languages
    SUPPORTED_COUNTRIES: List[str] = [
        "India",
        "USA",
        "UK",
        "Germany",
        "France",
        "Japan",
        "UAE",
        "Canada",
        "Australia",
        "Singapore",
        "Saudi Arabia",
        "Qatar",
        "Kuwait",
        "Oman",
        "Bahrain",
        "Malaysia",
        "Indonesia",
    ]

    SUPPORTED_LANGUAGES: List[str] = [
        "marathi",
        "hindi",
        "english",
        "tamil",
        "telugu",
        "bengali",
        "gujarati",
        "kannada",
        "punjabi",
        "malayalam",
        "odia",
        "arabic",
        "spanish",
        "french",
        "german",
        "chinese",
        "japanese",
    ]

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", os.urandom(32).hex())
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "https://vgas-app.com",
        "https://www.vgas-app.com",
        "https://vgas-shopping-ai.vercel.app",
        "https://vgas-shopping-ai.netlify.app",
    ]

    # File Upload
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_DIR: str = "uploads"

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "vgas_backend.log"

    # Rate Limiting
    RATE_LIMIT: int = 100  # requests per minute
    RATE_LIMIT_BURST: int = 20

    # Whitelisted Domains for Scraping
    WHITELISTED_DOMAINS: List[str] = [
        # India
        "amazon.in",
        "flipkart.com",
        "myntra.com",
        "ajio.com",
        "tatacliq.com",
        "croma.com",
        "nykaa.com",
        "reliancedigital.in",
        "paytmmall.com",
        "snapdeal.com",
        "shopclues.com",
        # Global
        "amazon.com",
        "amazon.co.uk",
        "amazon.de",
        "amazon.jp",
        "amazon.ae",
        "walmart.com",
        "ebay.com",
        "aliexpress.com",
        "noon.com",
        "bestbuy.com",
        "target.com",
        "newegg.com",
        "overstock.com",
        # Asia
        "shopee.com",
        "lazada.com",
        "tokopedia.com",
        "daraz.pk",
        # Middle East
        "noon.com",
        "carrefouruae.com",
        "luluwebstore.com",
    ]

    # AI Model Configuration
    AI_MODEL: str = (
        "gemini-1.5-pro-latest"  # gemini-1.5-pro, gemini-1.5-flash, gpt-4o-mini
    )
    AI_TEMPERATURE: float = 0.7
    AI_MAX_TOKENS: int = 4096

    # Monetization
    VIP_MEMBERSHIP_PRICE: float = 99.0  # INR per month
    VIP_MEMBERSHIP_PRICE_USD: float = 1.99  # USD per month
    CASHBACK_PERCENTAGE: float = 2.0  # 2% cashback on purchases
    AFFILIATE_COMMISSION: float = 5.0  # 5% average commission

    # WhatsApp Broadcast
    WHATSAPP_BROADCAST_ENABLED: bool = True
    WHATSAPP_MAX_RECIPIENTS: int = 1000

    # Notifications
    PRICE_DROP_ALERT_ENABLED: bool = True
    STOCK_ALERT_ENABLED: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"


# Create settings instance
settings = Settings()
