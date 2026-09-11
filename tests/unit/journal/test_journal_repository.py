from __future__ import annotations

from datetime import UTC, datetime

from ai_screener.journal.repositories.journal_repository import JournalRepository

_NOW = datetime.now(UTC)


def test_create_entry_returns_an_open_entry(
    journal_repository: JournalRepository,
) -> None:
    entry = journal_repository.create_entry(
        symbol="RELIANCE.NS",
        asset_type="equity",
        entry_date=_NOW,
        entry_price=100.0,
        rationale="Narrow monthly CPR breakout setup.",
    )

    assert entry.id is not None
    assert entry.is_closed is False
    assert entry.rationale == "Narrow monthly CPR breakout setup."


def test_close_entry_sets_exit_fields(
    journal_repository: JournalRepository,
) -> None:
    entry = journal_repository.create_entry(
        symbol="RELIANCE.NS",
        asset_type="equity",
        entry_date=_NOW,
        entry_price=100.0,
    )

    closed = journal_repository.close_entry(
        entry.id, exit_date=_NOW, exit_price=110.0, lessons_learned="Held too long."
    )

    assert closed is not None
    assert closed.is_closed is True
    assert closed.exit_price == 110.0
    assert closed.lessons_learned == "Held too long."


def test_close_entry_returns_none_for_unknown_id(
    journal_repository: JournalRepository,
) -> None:
    assert journal_repository.close_entry(999, _NOW, 100.0) is None


def test_update_notes(journal_repository: JournalRepository) -> None:
    entry = journal_repository.create_entry(
        symbol="RELIANCE.NS", asset_type="equity", entry_date=_NOW, entry_price=100.0
    )

    updated = journal_repository.update_notes(entry.id, "Watching for a retest.")

    assert updated is not None
    assert updated.notes == "Watching for a retest."


def test_attach_screenshot_sets_path(journal_repository: JournalRepository) -> None:
    entry = journal_repository.create_entry(
        symbol="RELIANCE.NS", asset_type="equity", entry_date=_NOW, entry_price=100.0
    )

    updated = journal_repository.attach_screenshot(entry.id, "/tmp/chart.png")

    assert updated is not None
    assert updated.screenshot_path == "/tmp/chart.png"


def test_list_entries_filters_by_symbol(journal_repository: JournalRepository) -> None:
    journal_repository.create_entry("RELIANCE.NS", "equity", _NOW, 100.0)
    journal_repository.create_entry("TCS.NS", "equity", _NOW, 200.0)

    assert [e.symbol for e in journal_repository.list_entries("RELIANCE.NS")] == [
        "RELIANCE.NS"
    ]
    assert len(journal_repository.list_entries()) == 2


def test_delete_entry(journal_repository: JournalRepository) -> None:
    entry = journal_repository.create_entry(
        symbol="RELIANCE.NS", asset_type="equity", entry_date=_NOW, entry_price=100.0
    )

    assert journal_repository.delete_entry(entry.id) is True
    assert journal_repository.get_entry(entry.id) is None
    assert journal_repository.delete_entry(entry.id) is False
