from datetime import datetime, timedelta, timezone

from app.ranking import calculate_hotness, deduplicate, rank_items
from app.schemas import RawTrend


def make_item(item_id: str, title: str, hours_old: int, velocity: float, category: str = "Agents") -> RawTrend:
    return RawTrend(
        id=item_id,
        title=title,
        summary="A test signal",
        source="Test source",
        source_kind="Research",
        category=category,  # type: ignore[arg-type]
        published_at=datetime.now(timezone.utc) - timedelta(hours=hours_old),
        href=f"https://example.com/{item_id}",
        tags=["test"],
        metrics={"velocity": velocity, "novelty": 0.8, "corroboration": 0.5},
    )


def test_newer_and_faster_signal_ranks_higher() -> None:
    now = datetime.now(timezone.utc)
    newer = make_item("new", "New signal", 2, 0.9)
    older = make_item("old", "Old signal", 48, 0.4)
    ranked = rank_items([older, newer], now)
    assert ranked[0].id == "new"
    assert ranked[0].score > ranked[1].score


def test_duplicate_titles_are_collapsed() -> None:
    first = make_item("one", "Same AI signal!", 4, 0.7)
    second = make_item("two", "Same AI signal", 5, 0.7)
    assert len(deduplicate([first, second])) == 1


def test_score_is_bounded() -> None:
    item = make_item("bounded", "Bounded signal", 0, 1.0)
    assert 0 <= calculate_hotness(item, datetime.now(timezone.utc)) <= 100
