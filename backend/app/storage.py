from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Union

from .schemas import IngestionRunResponse, RankedTrend


class SQLiteStore:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS trends (
                    id TEXT PRIMARY KEY,
                    rank INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    signal TEXT NOT NULL,
                    category TEXT NOT NULL,
                    source TEXT NOT NULL,
                    source_kind TEXT NOT NULL,
                    score INTEGER NOT NULL,
                    published TEXT NOT NULL,
                    tags_json TEXT NOT NULL,
                    href TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS ingestion_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    status TEXT NOT NULL,
                    started_at TEXT NOT NULL,
                    finished_at TEXT NOT NULL,
                    item_count INTEGER NOT NULL,
                    source_count INTEGER NOT NULL,
                    errors_json TEXT NOT NULL
                );
                """
            )

    def replace_trends(self, items: List[RankedTrend]) -> None:
        updated_at = datetime.now(timezone.utc).isoformat()
        with self._connect() as connection:
            connection.execute("DELETE FROM trends")
            connection.executemany(
                """
                INSERT INTO trends (id, rank, title, summary, signal, category, source, source_kind, score, published, tags_json, href, updated_at)
                VALUES (:id, :rank, :title, :summary, :signal, :category, :source, :source_kind, :score, :published, :tags_json, :href, :updated_at)
                """,
                [
                    {**item.model_dump(exclude={"tags"}), "tags_json": json.dumps(item.tags), "updated_at": updated_at}
                    for item in items
                ],
            )

    def list_trends(self, category: Optional[str] = None, query: Optional[str] = None, limit: int = 50) -> List[RankedTrend]:
        clauses = []
        values: List[Union[str, int]] = []
        if category and category != "All":
            clauses.append("category = ?")
            values.append(category)
        if query:
            clauses.append("(lower(title) LIKE ? OR lower(summary) LIKE ? OR lower(tags_json) LIKE ?)")
            wildcard = f"%{query.lower()}%"
            values.extend([wildcard, wildcard, wildcard])
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        with self._connect() as connection:
            rows = connection.execute(f"SELECT * FROM trends {where} ORDER BY rank ASC LIMIT ?", [*values, limit]).fetchall()
        return [
            RankedTrend(
                id=row["id"], rank=row["rank"], title=row["title"], summary=row["summary"], signal=row["signal"], category=row["category"], source=row["source"], source_kind=row["source_kind"], score=row["score"], published=row["published"], tags=json.loads(row["tags_json"]), href=row["href"]
            )
            for row in rows
        ]

    def record_run(self, run: IngestionRunResponse) -> None:
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO ingestion_runs (status, started_at, finished_at, item_count, source_count, errors_json) VALUES (?, ?, ?, ?, ?, ?)",
                (run.status, run.started_at.isoformat(), run.finished_at.isoformat(), run.item_count, run.source_count, json.dumps(run.errors)),
            )

    def last_run(self) -> Optional[IngestionRunResponse]:
        with self._connect() as connection:
            row = connection.execute("SELECT * FROM ingestion_runs ORDER BY id DESC LIMIT 1").fetchone()
        if row is None:
            return None
        return IngestionRunResponse(status=row["status"], started_at=datetime.fromisoformat(row["started_at"]), finished_at=datetime.fromisoformat(row["finished_at"]), item_count=row["item_count"], source_count=row["source_count"], errors=json.loads(row["errors_json"]))
