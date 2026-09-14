from __future__ import annotations

import html
import json
import math
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from typing import Any, Dict, Iterable, List, Optional, Sequence
from urllib.parse import quote
from xml.etree import ElementTree

import httpx

from .config import Settings
from .ranking import stable_id
from .schemas import RawTrend


def _clean_text(value: Optional[str], limit: int = 600) -> str:
    if not value:
        return ""
    without_tags = re.sub(r"<[^>]+>", " ", html.unescape(value))
    return re.sub(r"\s+", " ", without_tags).strip()[:limit]


def _parse_datetime(value: Optional[str]) -> datetime:
    if not value:
        return datetime.now(timezone.utc)
    try:
        parsed = parsedate_to_datetime(value)
    except (TypeError, ValueError, OverflowError):
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return datetime.now(timezone.utc)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _find_text(element: ElementTree.Element, names: Sequence[str]) -> str:
    for name in names:
        child = element.find(name)
        if child is not None and child.text:
            return child.text
        for nested in element.iter():
            if nested.tag.rsplit("}", 1)[-1] == name and nested.text:
                return nested.text
    return ""


@dataclass(frozen=True)
class FeedConfig:
    source_id: str
    source: str
    url: str
    category: str


class RSSAdapter:
    def __init__(self, feed: FeedConfig, settings: Settings):
        self.feed = feed
        self.settings = settings

    async def collect(self, client: httpx.AsyncClient) -> List[RawTrend]:
        response = await client.get(self.feed.url)
        response.raise_for_status()
        root = ElementTree.fromstring(response.text)
        entries = [node for node in root.iter() if node.tag.rsplit("}", 1)[-1] in {"item", "entry"}]
        collected: List[RawTrend] = []
        for entry in entries[: self.settings.max_items_per_source]:
            title = _clean_text(_find_text(entry, ("title",)), 300)
            href = _find_text(entry, ("link", "id"))
            link_element = next((node for node in entry if node.tag.rsplit("}", 1)[-1] == "link"), None)
            if link_element is not None:
                href = link_element.attrib.get("href", href)
            if not title or not href:
                continue
            summary = _clean_text(_find_text(entry, ("description", "summary", "content")))
            published_at = _parse_datetime(_find_text(entry, ("pubDate", "published", "updated")))
            tags = []
            for node in entry:
                if node.tag.rsplit("}", 1)[-1] == "category" and node.text:
                    tags.append(_clean_text(node.text, 40))
            tags = list(dict.fromkeys(tag for tag in tags if tag))[:5]
            collected.append(
                RawTrend(
                    id=stable_id(self.feed.source_id, href, title),
                    title=title,
                    summary=summary,
                    source=self.feed.source,
                    source_kind="Research" if self.feed.category == "Research" else "Product",
                    category=self.feed.category,  # type: ignore[arg-type]
                    published_at=published_at,
                    href=href,
                    tags=tags or [self.feed.category],
                    metrics={"velocity": 0.42, "novelty": 0.72, "corroboration": 0.25, "signal": f"{self.feed.source} update"},
                )
            )
        return collected


class HuggingFaceAdapter:
    url = "https://huggingface.co/api/models"

    def __init__(self, settings: Settings):
        self.settings = settings

    async def collect(self, client: httpx.AsyncClient) -> List[RawTrend]:
        response = await client.get(self.url, params={"sort": "downloads", "direction": -1, "limit": self.settings.max_items_per_source})
        response.raise_for_status()
        models = response.json()
        items: List[RawTrend] = []
        for model in models:
            model_id = model.get("id")
            if not model_id:
                continue
            downloads = float(model.get("downloads") or 0)
            last_modified = _parse_datetime(model.get("lastModified"))
            velocity = max(0.22, min(1.0, math.log1p(downloads) / math.log1p(1_000_000)))
            items.append(
                RawTrend(
                    id=stable_id("huggingface", model_id, model_id),
                    title=f"{model_id} is trending on Hugging Face",
                    summary=f"{model_id} has {int(downloads):,} recent downloads. Review its model card before using it in production.",
                    source="Hugging Face Trending",
                    source_kind="Hugging Face",
                    category="Models",
                    published_at=last_modified,
                    href=f"https://huggingface.co/{quote(model_id, safe='/')}",
                    tags=["Open weights", model.get("pipeline_tag") or "Model"],
                    metrics={"velocity": velocity, "novelty": 0.76, "corroboration": 0.2, "engagement": downloads, "signal": f"{int(downloads):,} downloads"},
                )
            )
        return items


class GitHubAdapter:
    url = "https://api.github.com/search/repositories"

    def __init__(self, settings: Settings):
        self.settings = settings

    async def collect(self, client: httpx.AsyncClient) -> List[RawTrend]:
        since = (datetime.now(timezone.utc) - timedelta(days=30)).date().isoformat()
        response = await client.get(self.url, params={"q": f"topic:artificial-intelligence created:>{since}", "sort": "stars", "order": "desc", "per_page": self.settings.max_items_per_source}, headers={"Accept": "application/vnd.github+json"})
        response.raise_for_status()
        repositories = response.json().get("items", [])
        items: List[RawTrend] = []
        for repository in repositories:
            name = repository.get("full_name")
            href = repository.get("html_url")
            if not name or not href:
                continue
            stars = float(repository.get("stargazers_count") or 0)
            created_at = _parse_datetime(repository.get("created_at"))
            age_days = max(1.0, (datetime.now(timezone.utc) - created_at).total_seconds() / 86400)
            star_velocity = stars / age_days
            velocity = max(0.2, min(1.0, math.log1p(star_velocity * 10) / math.log1p(1_000)))
            description = _clean_text(repository.get("description"), 300)
            items.append(
                RawTrend(
                    id=stable_id("github", href, name),
                    title=f"{name} is rising on GitHub",
                    summary=description or "An AI engineering repository gaining developer attention.",
                    source="GitHub Trending",
                    source_kind="GitHub",
                    category="Agents" if "agent" in f"{name} {description}".lower() else "Infrastructure",
                    published_at=created_at,
                    href=href,
                    tags=[repository.get("language") or "Open source", "GitHub"],
                    metrics={"velocity": velocity, "novelty": 0.82, "corroboration": 0.15, "engagement": stars, "signal": f"{int(stars):,} stars"},
                )
            )
        return items


def build_adapters(settings: Settings) -> List[Any]:
    feeds = [FeedConfig(*feed) for feed in settings.rss_feeds]
    return [RSSAdapter(feed, settings) for feed in feeds] + [HuggingFaceAdapter(settings), GitHubAdapter(settings)]


async def collect_all(adapters: Iterable[Any], settings: Settings) -> tuple[List[RawTrend], List[str]]:
    errors: List[str] = []
    items: List[RawTrend] = []
    async with httpx.AsyncClient(timeout=settings.request_timeout_seconds, follow_redirects=True, headers={"User-Agent": "AI-Radar/0.1 (+https://github.com/SHIJINGLI0206/daily-ai-news)"}) as client:
        import asyncio

        results = await asyncio.gather(*(adapter.collect(client) for adapter in adapters), return_exceptions=True)
    for result in results:
        if isinstance(result, Exception):
            errors.append(f"{type(result).__name__}: {result}")
        else:
            items.extend(result)
    return items, errors
