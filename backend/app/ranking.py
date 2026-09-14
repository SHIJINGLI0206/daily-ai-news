from __future__ import annotations

import hashlib
import math
import re
from collections import Counter
from datetime import datetime, timezone
from typing import Dict, Iterable, List, Optional, Tuple

from .schemas import RankedTrend, RawTrend


SOURCE_QUALITY: Dict[str, float] = {
    "Research": 0.92,
    "Product": 0.90,
    "GitHub": 0.78,
    "Hugging Face": 0.84,
    "Video": 0.64,
}


def _utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _normalized_title(value: str) -> str:
    return re.sub(r"[^a-z0-9 ]", "", value.lower()).strip()


def _freshness(item: RawTrend, now: datetime) -> float:
    age_hours = max(0.0, (_utc(now) - _utc(item.published_at)).total_seconds() / 3600)
    return max(0.0, min(1.0, math.exp(-age_hours / 72.0)))


def _velocity(item: RawTrend) -> float:
    explicit = item.metrics.get("velocity")
    if explicit is not None:
        return max(0.0, min(1.0, explicit))
    engagement = max(0.0, item.metrics.get("engagement", 0.0))
    return max(0.12, min(1.0, math.log1p(engagement) / math.log1p(1_000_000)))


def calculate_hotness(item: RawTrend, now: datetime, user_affinity: float = 0.5) -> int:
    """Return a transparent 0-100 hotness score.

    The weights intentionally favor freshness and momentum, while source quality,
    novelty, corroboration, and optional user affinity keep the feed useful.
    """
    freshness = _freshness(item, now)
    velocity = _velocity(item)
    novelty = max(0.0, min(1.0, item.metrics.get("novelty", 0.7)))
    corroboration = max(0.0, min(1.0, item.metrics.get("corroboration", 0.25)))
    quality = SOURCE_QUALITY.get(item.source_kind, 0.6)
    affinity = max(0.0, min(1.0, user_affinity))
    repeat_penalty = max(0.0, min(1.0, item.metrics.get("repeat_penalty", 0.0)))

    weighted = (
        0.25 * freshness
        + 0.25 * velocity
        + 0.20 * novelty
        + 0.15 * quality
        + 0.10 * corroboration
        + 0.05 * affinity
    )
    return max(0, min(100, round(weighted * 100 - repeat_penalty * 12)))


def deduplicate(items: Iterable[RawTrend]) -> List[RawTrend]:
    """Remove exact URL/title duplicates while keeping the strongest evidence."""
    by_key: Dict[str, RawTrend] = {}
    for item in items:
        canonical_url = item.href.split("#", 1)[0].split("?", 1)[0].rstrip("/")
        key = canonical_url or _normalized_title(item.title)
        current = by_key.get(key)
        if current is None or item.published_at > current.published_at:
            by_key[key] = item

    title_keys: Dict[str, RawTrend] = {}
    for item in by_key.values():
        key = _normalized_title(item.title)
        current = title_keys.get(key)
        if current is None or item.published_at > current.published_at:
            title_keys[key] = item
    return list(title_keys.values())


def rank_items(items: Iterable[RawTrend], now: Optional[datetime] = None) -> List[RankedTrend]:
    current_time = now or datetime.now(timezone.utc)
    unique_items = deduplicate(items)
    scored: List[Tuple[int, RawTrend]] = [(calculate_hotness(item, current_time), item) for item in unique_items]
    scored.sort(key=lambda pair: (pair[0], float(pair[1].metrics.get("engagement", 0) or 0), _utc(pair[1].published_at)), reverse=True)

    category_counts = Counter()
    ranked: List[RankedTrend] = []
    for score, item in scored:
        category_counts[item.category] += 1
        metric_signal = item.metrics.get("signal")
        signal = str(metric_signal) if metric_signal else f"{item.category} signal · {item.source}"
        ranked.append(
            RankedTrend(
                id=item.id,
                rank=len(ranked) + 1,
                title=item.title,
                summary=item.summary,
                signal=signal,
                category=item.category,
                source=item.source,
                source_kind=item.source_kind,
                score=score,
                published=_published_label(item.published_at, current_time),
                tags=item.tags[:5],
                href=item.href,
            )
        )
    return ranked


def _published_label(published_at: datetime, now: datetime) -> str:
    age_hours = max(0, int((_utc(now) - _utc(published_at)).total_seconds() // 3600))
    if age_hours < 1:
        return "Today · just now"
    if age_hours < 24:
        return f"Today · {age_hours}h ago"
    age_days = age_hours // 24
    return f"{age_days}d ago"


def stable_id(source: str, href: str, title: str) -> str:
    raw = f"{source}|{href}|{title}".encode("utf-8")
    return hashlib.sha1(raw).hexdigest()[:20]
