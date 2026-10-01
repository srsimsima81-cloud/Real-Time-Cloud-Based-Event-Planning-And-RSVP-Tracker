from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
from app.models import models
from app.api import auth, events, rsvps, notifications, my_rsvps
from app.ws.websocket import router as websocket_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn: await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()

app = FastAPI(title=settings.app_name, version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_list, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(auth.router); app.include_router(events.router); app.include_router(rsvps.router); app.include_router(my_rsvps.router); app.include_router(notifications.router); app.include_router(websocket_router)

@app.get("/health")
async def health():
    async with engine.connect() as conn:
        await conn.execute(text("SELECT 1"))
    return {"status":"ok","database":"connected","environment":settings.environment}
