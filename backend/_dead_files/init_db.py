# -*- coding: utf-8 -*-
"""Database Initialization - SQLite Auto-Setup"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import declarative_base
from pathlib import Path

Base = declarative_base()

async def init_database():
    """Initialize SQLite database with all tables"""
    from app.core.database import Base
    
    db_path = Path("vgas_production.db")
    engine = create_async_engine(
        f"sqlite+aiosqlite:///{db_path}",
        echo=False
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("  [OK] Database tables created")
    return engine

if __name__ == "__main__":
    asyncio.run(init_database())
