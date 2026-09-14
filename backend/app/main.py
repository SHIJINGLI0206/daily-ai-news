from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Optional

from fastapi import Depends, FastAPI, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from .config import Settings
from .ingestion import IngestionService
from .scheduler import run_daily_scheduler
from .schemas import HealthResponse, IngestionRunResponse, IngestionStatusResponse, TrendListResponse
from .sources import build_adapters
from .storage import SQLiteStore


settings = Settings.from_env()
store = SQLiteStore(settings.database_path)
adapters = build_adapters(settings)
ingestion = IngestionService(store, adapters, settings)


@asynccontextmanager
async def lifespan(_: FastAPI):
    stop_event = asyncio.Event()
    scheduler_task: Optional[asyncio.Task[None]] = None
    if settings.ingestion_on_startup:
        try:
            await ingestion.run()
        except Exception:
            pass
    if settings.schedule_enabled:
        scheduler_task = asyncio.create_task(run_daily_scheduler(ingestion.run, settings.schedule_time, settings.schedule_timezone, stop_event))
    yield
    stop_event.set()
    if scheduler_task:
        await scheduler_task


app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=list(settings.allowed_origins), allow_credentials=False, allow_methods=["GET", "POST"], allow_headers=["*"])


async def require_ingestion_token(x_ingestion_token: Optional[str] = Header(default=None)) -> None:
    if settings.ingestion_token and x_ingestion_token != settings.ingestion_token:
        raise HTTPException(status_code=401, detail="Invalid ingestion token")


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="ok", app=settings.app_name, database=str(settings.database_path), scheduler_enabled=settings.schedule_enabled)


@app.get("/api/trends", response_model=TrendListResponse)
async def list_trends(category: Optional[str] = Query(default=None), query: Optional[str] = Query(default=None), limit: int = Query(default=50, ge=1, le=100)) -> TrendListResponse:
    return TrendListResponse(items=store.list_trends(category=category, query=query, limit=limit), generated_at=datetime.now(timezone.utc), source_count=len(adapters))


@app.get("/api/ingestion/status", response_model=IngestionStatusResponse)
async def ingestion_status() -> IngestionStatusResponse:
    return IngestionStatusResponse(scheduler_enabled=settings.schedule_enabled, schedule_time=settings.schedule_time, schedule_timezone=settings.schedule_timezone, last_run=store.last_run())


@app.post("/api/ingestion/run", response_model=IngestionRunResponse, dependencies=[Depends(require_ingestion_token)])
async def run_ingestion() -> IngestionRunResponse:
    try:
        return await ingestion.run()
    except RuntimeError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
