"""Database Models for Vgas Shopping AI"""
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(20))
    is_premium = Column(Boolean, default=False)
    plan = Column(String(20), default="free")
    upi_id = Column(String(50))
    stripe_customer_id = Column(String(100))
    referral_code = Column(String(20), unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    
    tracks = relationship("ProductTrack", back_populates="user")
    referrals = relationship("Referral", foreign_keys="Referral.referrer_id", back_populates="referrer")

class ProductTrack(Base):
    __tablename__ = "product_tracks"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    url = Column(String(500), nullable=False)
    title = Column(String(200))
    image_url = Column(String(500))
    current_price = Column(Float)
    target_price = Column(Float)
    store = Column(String(50))
    status = Column(String(20), default="watching")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="tracks")
    price_history = relationship("PriceHistory", back_populates="product")

class PriceHistory(Base):
    __tablename__ = "price_history"
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("product_tracks.id"))
    price = Column(Float, nullable=False)
    store = Column(String(50))
    recorded_at = Column(DateTime, default=datetime.utcnow)
    
    product = relationship("ProductTrack", back_populates="price_history")

class Referral(Base):
    __tablename__ = "referrals"
    id = Column(Integer, primary_key=True)
    referrer_id = Column(Integer, ForeignKey("users.id"))
    referee_id = Column(Integer, ForeignKey("users.id"))
    status = Column(String(20), default="pending")
    amount = Column(Float, default=50.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    referrer = relationship("User", foreign_keys=[referrer_id], back_populates="referrals")

class AffiliateClick(Base):
    __tablename__ = "affiliate_clicks"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("product_tracks.id"))
    store = Column(String(50))
    clicked_at = Column(DateTime, default=datetime.utcnow)
    converted = Column(Boolean, default=False)

class Subscription(Base):
    __tablename__ = "subscriptions"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    stripe_sub_id = Column(String(100))
    plan = Column(String(20))
    status = Column(String(20), default="active")
    started_at = Column(DateTime, default=datetime.utcnow)
    ends_at = Column(DateTime)
