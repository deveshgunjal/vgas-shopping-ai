"""
Auth API endpoints for VGAS Shopping API
User registration, login, JWT tokens, session management
"""

from fastapi import APIRouter, Query, HTTPException, Body, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import logging
import hashlib
import secrets

from app.core.config import settings
from app.core.redis_cache import get_cache, set_cache, delete_cache
from app.utils.logger import vgas_logger
from app.database import get_db
from app.models import User

router = APIRouter(prefix="/auth", tags=["Authentication"])
logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


class RegisterRequest(BaseModel):
    email: Optional[str] = Field(default=None, description="Email address")
    password: str = Field(..., min_length=6, description="Password")
    name: Optional[str] = Field(default="", description="Full name")
    phone: Optional[str] = Field(default=None, description="Phone number")
    referred_by_code: Optional[str] = Field(default=None, description="Referral code")


class LoginRequest(BaseModel):
    phone_or_email: Optional[str] = Field(default=None, description="Phone number or email")
    email: Optional[str] = Field(default=None, description="Email (legacy)")
    phone: Optional[str] = Field(default=None, description="Phone (legacy)")
    username: Optional[str] = Field(default=None, description="Username (legacy)")
    password: str = Field(..., description="Password")

    def get_identifier(self) -> str:
        """Get the login identifier (email or phone)"""
        return (self.phone_or_email or self.email or self.phone or self.username or "").strip()


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: Dict[str, Any]


def _hash_password(password: str) -> str:
    """Hash password with salt"""
    salt = secrets.token_hex(16)
    hashed = hashlib.sha256(f"{salt}{password}".encode()).hexdigest()
    return f"{salt}${hashed}"


def _verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    try:
        salt, hash_val = hashed.split("$")
        return hashlib.sha256(f"{salt}{password}".encode()).hexdigest() == hash_val
    except Exception:
        return False


def _generate_token(user_id: str) -> str:
    """Generate simple JWT-like token"""
    import hmac
    import base64

    header = (
        base64.urlsafe_b64encode(b'{"alg":"HS256","typ":"JWT"}').rstrip(b"=").decode()
    )
    payload_data = f"{user_id}:{datetime.utcnow().isoformat()}"
    payload = base64.urlsafe_b64encode(payload_data.encode()).rstrip(b"=").decode()
    signature = hmac.new(
        (settings.SECRET_KEY or "vgas-secret-key").encode(),
        f"{header}.{payload}".encode(),
        hashlib.sha256,
    ).digest()
    sig = base64.urlsafe_b64encode(signature).rstrip(b"=").decode()
    return f"{header}.{payload}.{sig}"


@router.post("/register")
async def register(request: RegisterRequest = Body(...)):
    """Register a new user - supports email or phone"""
    try:
        identifier = request.email or request.phone
        if not identifier:
            raise HTTPException(status_code=400, detail="Email or phone is required")

        vgas_logger.info(f"New registration: {identifier}")

        # Check if user exists (by email or phone)
        user_key = f"user:{identifier}"
        existing = await get_cache(user_key)
        if existing:
            raise HTTPException(status_code=400, detail="User already exists")

        # Also check alternate identifier
        alt_key = f"user:{request.phone}" if request.email else f"user:{request.email}"
        if alt_key != user_key:
            existing_alt = await get_cache(alt_key)
            if existing_alt:
                raise HTTPException(status_code=400, detail="User already exists")

        # Create user
        password_hash = _hash_password(request.password)
        db = next(get_db())
        db_user = User(
            username=request.name or "User",
            email=request.email or f"{request.phone or secrets.token_hex(8)}@vgas.ai",
            phone=request.phone or "",
            plan="free",
            is_premium=False,
            referral_code=f"VGAS{secrets.token_hex(3).upper()}"
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        user_id = str(db_user.id)

        user_data = {
            "id": user_id,
            "email": request.email,
            "name": request.name or "",
            "phone": request.phone,
            "password_hash": password_hash,
            "created_at": datetime.utcnow().isoformat(),
            "plan": "free",
            "is_active": True,
            "referral_code": db_user.referral_code,
        }

        # Store user by both email and phone
        await set_cache(user_key, user_data, expire_seconds=86400 * 365)
        await set_cache(f"user_id:{user_id}", user_data, expire_seconds=86400 * 365)
        if request.email and request.phone:
            await set_cache(f"user:{request.phone}", user_data, expire_seconds=86400 * 365)

        # Generate token
        token = _generate_token(user_id)
        token_key = f"token:{token}"
        await set_cache(token_key, user_id, expire_seconds=86400 * 7)

        # Remove password from response
        user_response = {k: v for k, v in user_data.items() if k != "password_hash"}

        return {
            "message": "Registration successful",
            "access_token": token,
            "token_type": "bearer",
            "expires_in": 604800,
            "user": user_response,
            "timestamp": datetime.utcnow().isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/login")
async def login(request: LoginRequest = Body(...)):
    """Login user - supports phone_or_email, email, or phone"""
    try:
        # Get identifier from any field
        identifier = request.get_identifier()
        if not identifier:
            raise HTTPException(status_code=400, detail="Email or phone is required")

        # Try to find user by email, phone, or phone_or_email
        user_data = None
        lookup_keys = [
            f"user:{identifier}",
            f"user:{request.email}" if request.email else None,
            f"user:{request.phone}" if request.phone else None,
        ]
        for key in lookup_keys:
            if key:
                user_data = await get_cache(key)
                if user_data:
                    break

        if not user_data:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        # Verify password
        if not _verify_password(request.password, user_data.get("password_hash", "")):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        # Generate token
        token = _generate_token(user_data["id"])
        token_key = f"token:{token}"
        await set_cache(token_key, user_data["id"], expire_seconds=86400 * 7)

        # Remove password from response
        user_response = {k: v for k, v in user_data.items() if k != "password_hash"}

        return {
            "message": "Login successful",
            "access_token": token,
            "token_type": "bearer",
            "expires_in": 604800,
            "user": user_response,
            "timestamp": datetime.utcnow().isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/me")
async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Get current user profile"""
    try:
        token_key = f"token:{token}"
        user_id = await get_cache(token_key)
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid or expired token")

        # Find user by ID
        all_users_key = f"user_index"
        user_data = await get_cache(f"user_id:{user_id}")
        if not user_data:
            raise HTTPException(status_code=404, detail="User not found")

        user_response = {k: v for k, v in user_data.items() if k != "password_hash"}
        return {"user": user_response, "timestamp": datetime.utcnow().isoformat()}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get user error: {e}")
        raise HTTPException(status_code=401, detail="Authentication required")


@router.post("/logout")
async def logout(token: str = Depends(oauth2_scheme)):
    """Logout user"""
    try:
        token_key = f"token:{token}"
        await delete_cache(token_key)
        return {
            "message": "Logged out successfully",
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Logout error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/verify")
async def verify_token(token: str = Query(...)):
    """Verify if a token is valid"""
    try:
        token_key = f"token:{token}"
        user_id = await get_cache(token_key)
        return {
            "valid": bool(user_id),
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Token verify error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/refresh")
async def refresh_token(token: str = Body(..., embed=True)):
    """Refresh access token"""
    try:
        token_key = f"token:{token}"
        user_id = await get_cache(token_key)
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")

        # Generate new token
        new_token = _generate_token(user_id)
        new_token_key = f"token:{new_token}"
        await set_cache(new_token_key, user_id, expire_seconds=86400 * 7)

        # Invalidate old token
        await delete_cache(token_key)

        return {
            "access_token": new_token,
            "token_type": "bearer",
            "expires_in": 604800,
            "timestamp": datetime.utcnow().isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
