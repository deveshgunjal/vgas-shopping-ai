"""
Database connection and models for VGAS Shopping AI
"""

import asyncpg
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, JSON, Index, ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY, TIMESTAMP
from datetime import datetime
from typing import Optional, List
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

# Create base model
Base = declarative_base()

# Database engine
engine = None
async_session = None


async def init_db():
    """Initialize database connection with graceful fallback"""
    global engine, async_session
    
    try:
        # Create async engine for PostgreSQL
        engine = create_async_engine(
            settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
            echo=settings.DEBUG,
            pool_size=20,
            max_overflow=10,
            pool_pre_ping=True,
            pool_recycle=3600
        )
        
        # Create async session factory
        async_session = async_sessionmaker(
            bind=engine,
            expire_on_commit=False,
            class_=AsyncSession
        )
        
        # Test connection
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            logger.info("✅ PostgreSQL database connected & tables created successfully")
            
    except Exception as e:
        logger.warning(f"⚠️ PostgreSQL connection failed ({e}). Falling back to SQLite database...")
        try:
            engine = create_async_engine(
                "sqlite+aiosqlite:///./vgas_production.db",
                echo=False
            )
            async_session = async_sessionmaker(
                bind=engine,
                expire_on_commit=False,
                class_=AsyncSession
            )
            async with engine.begin() as conn:
                try:
                    await conn.run_sync(lambda sync_conn: Base.metadata.create_all(sync_conn, checkfirst=True))
                except Exception:
                    pass
            logger.info("✅ SQLite fallback database initialized successfully")
        except Exception as sq_err:
            logger.info(f"ℹ️ Database notice: {sq_err}")


async def get_db():
    """Dependency for getting database session"""
    async with async_session() as session:
        yield session


# Database Models
class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String(20), unique=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=True)
    name = Column(String(255), nullable=True)
    password_hash = Column(String(512), nullable=True)
    
    # Profile
    profile_pic = Column(String(512), nullable=True)
    preferred_language = Column(String(50), default="english")
    preferred_currency = Column(String(10), default="INR")
    country = Column(String(100), default="India")
    
    # Social
    google_id = Column(String(255), unique=True, nullable=True)
    facebook_id = Column(String(255), unique=True, nullable=True)
    
    # VIP Membership
    is_vip = Column(Boolean, default=False)
    vip_expiry = Column(DateTime, nullable=True)
    vip_auto_renew = Column(Boolean, default=False)
    
    # Stats
    total_searches = Column(Integer, default=0)
    total_purchases = Column(Integer, default=0)
    total_savings = Column(Float, default=0.0)
    
    # Referral
    referral_code = Column(String(20), unique=True, nullable=True)
    referred_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    
    # PayPal
    paypal_email = Column(String(255), nullable=True)
    
    # Bank Details (for cashback)
    bank_name = Column(String(255), nullable=True)
    bank_account = Column(String(50), nullable=True)
    bank_ifsc = Column(String(50), nullable=True)
    upi_id = Column(String(100), nullable=True)
    
    # Notifications
    push_notifications = Column(Boolean, default=True)
    email_notifications = Column(Boolean, default=True)
    whatsapp_notifications = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # Indexes
    __table_args__ = (
        Index('ix_users_phone', 'phone'),
        Index('ix_users_email', 'email'),
        Index('ix_users_referral', 'referral_code'),
        Index('ix_users_country', 'country'),
    )


class Product(Base):
    """Product model"""
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Identifiers
    sku = Column(String(255), unique=True, index=True, nullable=True)
    asin = Column(String(50), unique=True, index=True, nullable=True)
    upc = Column(String(50), unique=True, index=True, nullable=True)
    ean = Column(String(50), unique=True, index=True, nullable=True)
    
    # Basic info
    name = Column(String(1000), nullable=False, index=True)
    brand = Column(String(255), index=True, nullable=True)
    model = Column(String(255), nullable=True)
    category = Column(String(255), index=True, nullable=True)
    subcategory = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    
    # Images
    images = Column(JSON, nullable=True)
    main_image = Column(String(512), nullable=True)
    
    # Specifications
    specifications = Column(JSON, nullable=True)  # Key-value pairs
    features = Column(JSON, nullable=True)
    
    # Ratings & Reviews
    rating = Column(Float, default=0.0)
    rating_count = Column(Integer, default=0)
    review_count = Column(Integer, default=0)
    review_score = Column(Float, default=0.0)  # AI-calculated score
    
    # AI Analysis
    quality_score = Column(Float, default=0.0)
    functionality_score = Column(Float, default=0.0)
    authenticity_score = Column(Float, default=100.0)
    
    # Metadata
    color = Column(String(100), nullable=True)
    size = Column(String(100), nullable=True)
    weight = Column(Float, nullable=True)
    dimensions = Column(JSON, nullable=True)
    warranty = Column(String(255), nullable=True)
    
    # Country & Language
    country = Column(String(100), default="Global", index=True)
    language = Column(String(50), default="english")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Store(Base):
    """Store/E-commerce platform model"""
    __tablename__ = "stores"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    domain = Column(String(255), unique=True, nullable=False, index=True)
    logo = Column(String(512), nullable=True)
    description = Column(Text, nullable=True)
    
    # Location
    country = Column(String(100), default="Global", index=True)
    region = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    
    # Affiliate
    affiliate_network = Column(String(255), nullable=True)
    affiliate_id = Column(String(255), nullable=True)
    commission_rate = Column(Float, default=0.0)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_whitelisted = Column(Boolean, default=True)
    
    # Trust & Safety
    trust_score = Column(Float, default=100.0)
    is_verified = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('ix_stores_domain', 'domain'),
        Index('ix_stores_country', 'country'),
        Index('ix_stores_active', 'is_active'),
    )


class ProductVariant(Base):
    """Product variant (different sellers/prices for same product)"""
    __tablename__ = "product_variants"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False, index=True)
    store_id = Column(Integer, ForeignKey('stores.id'), nullable=False, index=True)
    
    # Price info
    current_price = Column(Float, nullable=False)
    original_price = Column(Float, nullable=True)
    discount_percentage = Column(Float, default=0.0)
    currency = Column(String(10), default="INR", index=True)
    
    # Stock
    is_in_stock = Column(Boolean, default=True)
    stock_count = Column(Integer, nullable=True)
    estimated_delivery = Column(String(255), nullable=True)
    
    # Seller
    seller_id = Column(String(255), nullable=True)
    seller_name = Column(String(255), nullable=True)
    seller_rating = Column(Float, default=0.0)
    seller_is_brand = Column(Boolean, default=False)
    
    # Shipping
    shipping_cost = Column(Float, default=0.0)
    shipping_method = Column(String(255), nullable=True)
    estimated_delivery_days = Column(Integer, nullable=True)
    
    # Product URL
    product_url = Column(String(1000), nullable=False)
    affiliate_url = Column(String(1000), nullable=True)
    
    # Condition
    condition = Column(String(50), default="new")  # new, refurbished, used, open_box
    warranty_type = Column(String(100), nullable=True)  # brand, seller, none
    warranty_period = Column(String(100), nullable=True)  # 6 months, 1 year, etc.
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_scraped = Column(DateTime, nullable=True)
    
    # Indexes
    __table_args__ = (
        Index('ix_product_variants_product', 'product_id'),
        Index('ix_product_variants_store', 'store_id'),
        Index('ix_product_variants_price', 'current_price'),
        Index('ix_product_variants_currency', 'currency'),
        Index('ix_product_variants_stock', 'is_in_stock'),
    )


class PriceHistory(Base):
    """Price history tracking"""
    __tablename__ = "price_history"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False, index=True)
    variant_id = Column(Integer, ForeignKey('product_variants.id'), nullable=True, index=True)
    
    # Price data
    price = Column(Float, nullable=False)
    original_price = Column(Float, nullable=True)
    discount_percentage = Column(Float, default=0.0)
    currency = Column(String(10), default="INR")
    
    # Metadata
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    source = Column(String(255), nullable=True)
    is_sale = Column(Boolean, default=False)
    sale_event = Column(String(255), nullable=True)  # Black Friday, Diwali Sale, etc.
    
    # Indexes
    __table_args__ = (
        Index('ix_price_history_product', 'product_id'),
        Index('ix_price_history_variant', 'variant_id'),
        Index('ix_price_history_timestamp', 'timestamp'),
    )


class SearchQuery(Base):
    """User search queries"""
    __tablename__ = "search_queries"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True, index=True)
    
    # Query
    query = Column(String(1000), nullable=False, index=True)
    query_type = Column(String(50), default="text")  # text, image, voice, url
    
    # Results
    result_count = Column(Integer, default=0)
    best_price = Column(Float, nullable=True)
    best_store = Column(String(255), nullable=True)
    savings = Column(Float, default=0.0)
    
    # Metadata
    ip_address = Column(String(50), nullable=True)
    device_info = Column(JSON, nullable=True)
    location = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Indexes
    __table_args__ = (
        Index('ix_search_queries_user', 'user_id'),
        Index('ix_search_queries_query', 'query'),
        Index('ix_search_queries_created', 'created_at'),
    )


class Comparison(Base):
    """Product comparisons"""
    __tablename__ = "comparisons"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True, index=True)
    
    # Products being compared
    product_ids = Column(JSON, nullable=False)
    names = Column(JSON, nullable=True)
    
    # Results
    winner_id = Column(Integer, nullable=True)
    winner_name = Column(String(255), nullable=True)
    best_price = Column(Float, nullable=True)
    savings = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Indexes
    __table_args__ = (
        Index('ix_comparisons_user', 'user_id'),
        Index('ix_comparisons_created', 'created_at'),
    )


class PriceAlert(Base):
    """Price drop alerts"""
    __tablename__ = "price_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    
    # Alert details
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False, index=True)
    product_name = Column(String(255), nullable=True)
    target_price = Column(Float, nullable=False)
    current_price = Column(Float, nullable=True)
    currency = Column(String(10), default="INR")
    
    # Status
    is_active = Column(Boolean, default=True)
    is_triggered = Column(Boolean, default=False)
    triggered_at = Column(DateTime, nullable=True)
    trigger_price = Column(Float, nullable=True)
    
    # Notification
    notification_sent = Column(Boolean, default=False)
    notification_methods = Column(JSON, default=['email', 'whatsapp'])
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('ix_price_alerts_user', 'user_id'),
        Index('ix_price_alerts_product', 'product_id'),
        Index('ix_price_alerts_active', 'is_active'),
        Index('ix_price_alerts_created', 'created_at'),
    )


class CashbackTransaction(Base):
    """Cashback transactions"""
    __tablename__ = "cashback_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    
    # Transaction details
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="INR")
    type = Column(String(50), default="purchase")  # purchase, referral, bonus
    
    # Related info
    order_id = Column(String(255), nullable=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=True)
    store_id = Column(Integer, ForeignKey('stores.id'), nullable=True)
    affiliate_link = Column(String(1000), nullable=True)
    
    # Status
    status = Column(String(50), default="pending")  # pending, approved, paid, rejected
    payment_method = Column(String(50), nullable=True)  # upi, bank, paypal
    payment_ref = Column(String(255), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    approved_at = Column(DateTime, nullable=True)
    paid_at = Column(DateTime, nullable=True)
    
    # Indexes
    __table_args__ = (
        Index('ix_cashback_user', 'user_id'),
        Index('ix_cashback_status', 'status'),
        Index('ix_cashback_created', 'created_at'),
    )


class AffiliateLink(Base):
    """Affiliate links generated"""
    __tablename__ = "affiliate_links"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True, index=True)
    
    # Link details
    original_url = Column(String(1000), nullable=False)
    affiliate_url = Column(String(1000), nullable=False)
    short_url = Column(String(255), nullable=True)
    
    # Metadata
    store_id = Column(Integer, ForeignKey('stores.id'), nullable=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=True)
    product_name = Column(String(255), nullable=True)
    
    # Stats
    clicks = Column(Integer, default=0)
    purchases = Column(Integer, default=0)
    conversions = Column(Integer, default=0)
    total_earnings = Column(Float, default=0.0)
    
    # Status
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('ix_affiliate_links_user', 'user_id'),
        Index('ix_affiliate_links_store', 'store_id'),
        Index('ix_affiliate_links_product', 'product_id'),
        Index('ix_affiliate_links_created', 'created_at'),
    )


class AIChat(Base):
    """AI chat conversations"""
    __tablename__ = "ai_chats"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True, index=True)
    
    # Message
    role = Column(String(50), default="user")  # user, assistant
    content = Column(Text, nullable=False)
    
    # Metadata
    language = Column(String(50), default="english")
    intent = Column(String(255), nullable=True)
    confidence = Column(Float, default=0.0)
    
    # Context
    session_id = Column(String(255), index=True, nullable=True)
    related_product_id = Column(Integer, ForeignKey('products.id'), nullable=True)
    related_store_id = Column(Integer, ForeignKey('stores.id'), nullable=True)
    
    # AI Response
    response_time = Column(Float, nullable=True)  # seconds
    tokens_used = Column(Integer, default=0)
    model_used = Column(String(100), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Indexes
    __table_args__ = (
        Index('ix_ai_chats_user', 'user_id'),
        Index('ix_ai_chats_session', 'session_id'),
        Index('ix_ai_chats_created', 'created_at'),
    )


class Notification(Base):
    """User notifications"""
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    
    # Notification details
    title = Column(String(500), nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String(50), default="info")  # info, warning, success, error, promotion
    
    # Related entities
    related_id = Column(Integer, nullable=True)
    related_type = Column(String(50), nullable=True)  # product, alert, transaction, etc.
    
    # Action
    action_url = Column(String(1000), nullable=True)
    action_text = Column(String(255), nullable=True)
    
    # Status
    is_read = Column(Boolean, default=False)
    is_sent = Column(Boolean, default=False)
    sent_via = Column(JSON, default=['app'])
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    read_at = Column(DateTime, nullable=True)
    sent_at = Column(DateTime, nullable=True)
    
    # Indexes
    __table_args__ = (
        Index('ix_notifications_user', 'user_id'),
        Index('ix_notifications_read', 'is_read'),
        Index('ix_notifications_created', 'created_at'),
    )


class MonetizationStats(Base):
    """Monetization statistics"""
    __tablename__ = "monetization_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Revenue sources
    ad_revenue = Column(Float, default=0.0)
    affiliate_revenue = Column(Float, default=0.0)
    membership_revenue = Column(Float, default=0.0)
    sponsorship_revenue = Column(Float, default=0.0)
    
    # Expenses
    server_cost = Column(Float, default=0.0)
    api_cost = Column(Float, default=0.0)
    
    # Metrics
    total_users = Column(Integer, default=0)
    active_users = Column(Integer, default=0)
    total_searches = Column(Integer, default=0)
    total_purchases = Column(Integer, default=0)
    total_affiliate_clicks = Column(Integer, default=0)
    
    # Indexes
    __table_args__ = (
        Index('ix_monetization_date', 'date'),
    )
