from datetime import datetime, timedelta, timezone
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.db.session import get_db
from app.models.models import User, UserRole

password_hash = PasswordHash.recommended()
bearer = HTTPBearer(auto_error=False)

def hash_password(password: str) -> str: return password_hash.hash(password)
def verify_password(password: str, hashed: str) -> bool: return password_hash.verify(password, hashed)

def create_access_token(user: User) -> str:
    exp = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_minutes)
    return jwt.encode({"sub": str(user.id), "role": user.role, "exp": exp}, settings.jwt_secret, algorithm=settings.jwt_algorithm)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer), db: AsyncSession = Depends(get_db)) -> User:
    if not credentials: raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    try: payload = jwt.decode(credentials.credentials, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except jwt.PyJWTError: raise HTTPException(status_code=401, detail="Invalid or expired token")
    try: user_id = int(payload["sub"])
    except (KeyError, ValueError): raise HTTPException(status_code=401, detail="Invalid token subject")
    user = await db.get(User, user_id)
    if not user: raise HTTPException(status_code=401, detail="User not found")
    return user

def require_roles(*roles: UserRole):
    async def dependency(user: User = Depends(get_current_user)):
        if user.role not in roles: raise HTTPException(status_code=403, detail="Insufficient permissions")
        return user
    return dependency
