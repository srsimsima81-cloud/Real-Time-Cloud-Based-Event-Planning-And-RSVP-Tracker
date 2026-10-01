from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import create_access_token, hash_password, verify_password, get_current_user
from app.db.session import get_db
from app.models.models import User, UserRole
from app.schemas.schemas import LoginRequest, TokenResponse, UserCreate, UserOut

router = APIRouter(prefix="/api", tags=["Auth"])

@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(data: UserCreate, db: AsyncSession = Depends(get_db)):
    if await db.scalar(select(User).where(User.email == data.email.lower())): raise HTTPException(409, "Email is already registered")
    if data.role == UserRole.ADMIN:
        raise HTTPException(403, "Admin accounts cannot be self-registered")
    user = User(name=data.name.strip(), email=data.email.lower(), password_hash=hash_password(data.password), role=data.role.value)
    db.add(user); await db.commit(); await db.refresh(user)
    return TokenResponse(access_token=create_access_token(user), user=user)

@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = await db.scalar(select(User).where(User.email == data.email.lower()))
    if not user or not verify_password(data.password, user.password_hash): raise HTTPException(401, "Invalid email or password")
    return TokenResponse(access_token=create_access_token(user), user=user)

@router.post("/logout")
async def logout(user=Depends(get_current_user)): return {"message": "Logged out. Discard the client token."}

@router.get("/me", response_model=UserOut)
async def me(user=Depends(get_current_user)): return user
