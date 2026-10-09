from datetime import datetime, timedelta, timezone
from uuid import UUID

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.session import get_session
from app.models import Membership, User

hasher = PasswordHasher()
bearer = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    return hasher.hash(password)


def verify_password(encoded: str, password: str) -> bool:
    try:
        return hasher.verify(encoded, password)
    except VerifyMismatchError:
        return False


def create_access_token(user_id: UUID) -> str:
    settings = get_settings()
    now = datetime.now(timezone.utc)
    return jwt.encode({"sub": str(user_id), "iat": now, "exp": now + timedelta(minutes=settings.access_token_ttl_minutes)},
                      settings.app_secret_key.get_secret_value(), algorithm="HS256")


async def current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
                       session: AsyncSession = Depends(get_session)) -> User:
    unauthorized = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials",
                                  headers={"WWW-Authenticate": "Bearer"})
    if credentials is None:
        raise unauthorized
    try:
        payload = jwt.decode(credentials.credentials, get_settings().app_secret_key.get_secret_value(), algorithms=["HS256"])
        user_id = UUID(payload["sub"])
    except (jwt.PyJWTError, ValueError, KeyError):
        raise unauthorized from None
    user = await session.get(User, user_id)
    if user is None or user.status != "active":
        raise unauthorized
    return user


async def require_membership(community_id: UUID, user: User, session: AsyncSession,
                             roles: set[str] | None = None) -> Membership:
    result = await session.execute(select(Membership).where(
        Membership.community_id == community_id, Membership.user_id == user.id,
        Membership.status == "active"))
    membership = result.scalar_one_or_none()
    if membership is None:
        raise HTTPException(status_code=404, detail="Community not found")
    if roles and membership.role not in roles:
        raise HTTPException(status_code=403, detail="Insufficient community role")
    return membership
