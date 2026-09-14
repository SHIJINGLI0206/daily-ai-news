from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple


DEFAULT_RSS_FEEDS: Tuple[Tuple[str, str, str, str], ...] = (
    ("aws-ml", "AWS Machine Learning", "https://aws.amazon.com/blogs/machine-learning/feed/", "Infrastructure"),
    ("github-blog", "GitHub Blog", "https://github.blog/feed/", "Agents"),
    ("arxiv-ai", "arXiv cs.AI", "https://rss.arxiv.org/rss/cs.AI", "Research"),
)


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except ValueError:
        return default


@dataclass(frozen=True)
class Settings:
    app_name: str
    database_path: Path
    schedule_enabled: bool
    ingestion_on_startup: bool
    schedule_time: str
    schedule_timezone: str
    request_timeout_seconds: float
    max_items_per_source: int
    allowed_origins: Tuple[str, ...]
    ingestion_token: Optional[str]
    rss_feeds: Tuple[Tuple[str, str, str, str], ...]

    @classmethod
    def from_env(cls) -> "Settings":
        backend_root = Path(__file__).resolve().parents[1]
        database_path = Path(os.getenv("AI_RADAR_DB_PATH", str(backend_root / "data" / "ai_radar.sqlite3")))
        origins = tuple(item.strip() for item in os.getenv("AI_RADAR_ALLOWED_ORIGINS", "http://localhost:3000").split(",") if item.strip())
        feed_override = os.getenv("AI_RADAR_RSS_FEEDS", "").strip()
        rss_feeds = DEFAULT_RSS_FEEDS
        if feed_override:
            parsed = []
            for index, raw_feed in enumerate(feed_override.split(",")):
                parts = [part.strip() for part in raw_feed.split("|")]
                if len(parts) == 4:
                    parsed.append((parts[0], parts[1], parts[2], parts[3]))
                else:
                    parsed.append((f"custom-{index}", f"Custom feed {index + 1}", raw_feed.strip(), "Research"))
            rss_feeds = tuple(parsed)

        return cls(
            app_name=os.getenv("AI_RADAR_APP_NAME", "AI Radar API"),
            database_path=database_path,
            schedule_enabled=_env_bool("AI_RADAR_SCHEDULE_ENABLED", True),
            ingestion_on_startup=_env_bool("AI_RADAR_INGESTION_ON_STARTUP", False),
            schedule_time=os.getenv("AI_RADAR_SCHEDULE_TIME", "07:00"),
            schedule_timezone=os.getenv("AI_RADAR_SCHEDULE_TIMEZONE", "Pacific/Auckland"),
            request_timeout_seconds=float(os.getenv("AI_RADAR_REQUEST_TIMEOUT_SECONDS", "20")),
            max_items_per_source=_env_int("AI_RADAR_MAX_ITEMS_PER_SOURCE", 12),
            allowed_origins=origins,
            ingestion_token=os.getenv("AI_RADAR_INGESTION_TOKEN") or None,
            rss_feeds=rss_feeds,
        )
