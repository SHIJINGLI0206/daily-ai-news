from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any, List

from .config import Settings
from .ranking import rank_items
from .schemas import IngestionRunResponse
from .sources import collect_all
from .storage import SQLiteStore


class IngestionService:
    def __init__(self, store: SQLiteStore, adapters: List[Any], settings: Settings):
        self.store = store
        self.adapters = adapters
        self.settings = settings
        self._lock = asyncio.Lock()

    async def run(self) -> IngestionRunResponse:
        if self._lock.locked():
            raise RuntimeError("An ingestion run is already in progress")
        async with self._lock:
            started_at = datetime.now(timezone.utc)
            raw_items, errors = await collect_all(self.adapters, self.settings)
            ranked = rank_items(raw_items, started_at)
            if ranked:
                self.store.replace_trends(ranked)
            finished_at = datetime.now(timezone.utc)
            status = "completed" if not errors else ("completed_with_errors" if ranked else "failed")
            result = IngestionRunResponse(status=status, started_at=started_at, finished_at=finished_at, item_count=len(ranked), source_count=len(self.adapters), errors=errors)
            self.store.record_run(result)
            return result
