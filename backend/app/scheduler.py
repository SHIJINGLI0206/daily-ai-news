from __future__ import annotations

import asyncio
from datetime import datetime, time, timedelta, timezone
from typing import Awaitable, Callable, Optional
from zoneinfo import ZoneInfo


def seconds_until_next_run(schedule_time: str, timezone_name: str, now: Optional[datetime] = None) -> float:
    hour, minute = (int(part) for part in schedule_time.split(":", 1))
    zone = ZoneInfo(timezone_name)
    local_now = (now or datetime.now(timezone.utc)).astimezone(zone)
    target = datetime.combine(local_now.date(), time(hour=hour, minute=minute), tzinfo=zone)
    if target <= local_now:
        target += timedelta(days=1)
    return max(1.0, (target - local_now).total_seconds())


async def run_daily_scheduler(run_ingestion: Callable[[], Awaitable[object]], schedule_time: str, timezone_name: str, stop_event: asyncio.Event) -> None:
    while not stop_event.is_set():
        delay = seconds_until_next_run(schedule_time, timezone_name)
        try:
            await asyncio.wait_for(stop_event.wait(), timeout=delay)
        except asyncio.TimeoutError:
            try:
                await run_ingestion()
            except Exception:
                # The next cycle remains scheduled even if one source run fails.
                continue
