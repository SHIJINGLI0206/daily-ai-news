from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


SourceKind = Literal["Research", "Product", "GitHub", "Hugging Face", "Video"]
TrendCategory = Literal["Agents", "Models", "Infrastructure", "Research", "Creative"]


class RawTrend(BaseModel):
    id: str
    title: str = Field(min_length=3, max_length=300)
    summary: str = Field(default="", max_length=1200)
    source: str
    source_kind: SourceKind
    category: TrendCategory
    published_at: datetime
    href: str
    tags: List[str] = Field(default_factory=list)
    metrics: Dict[str, Any] = Field(default_factory=dict)


class RankedTrend(BaseModel):
    id: str
    rank: int
    title: str
    summary: str
    signal: str
    category: TrendCategory
    source: str
    source_kind: SourceKind
    score: int
    published: str
    tags: List[str]
    href: str


class TrendListResponse(BaseModel):
    items: List[RankedTrend]
    generated_at: datetime
    source_count: int


class IngestionRunResponse(BaseModel):
    status: str
    started_at: datetime
    finished_at: datetime
    item_count: int
    source_count: int
    errors: List[str] = Field(default_factory=list)


class IngestionStatusResponse(BaseModel):
    scheduler_enabled: bool
    schedule_time: str
    schedule_timezone: str
    last_run: Optional[IngestionRunResponse] = None


class HealthResponse(BaseModel):
    status: str
    app: str
    database: str
    scheduler_enabled: bool
