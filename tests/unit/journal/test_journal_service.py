from __future__ import annotations

from pathlib import Path

import pytest

from ai_screener.core.exceptions import ValidationError
from ai_screener.journal.service import JournalService


def test_add_entry_creates_an_open_entry(journal_service: JournalService) -> None:
    entry = journal_service.add_entry(
        symbol="RELIANCE.NS", entry_price=100.0, rationale="Narrow CPR."
    )

    assert entry.is_closed is False
    assert entry.asset_type == "equity"


def test_close_entry_closes_it(journal_service: JournalService) -> None:
    entry = journal_service.add_entry(symbol="RELIANCE.NS", entry_price=100.0)

    closed = journal_service.close_entry(entry.id, exit_price=110.0)

    assert closed is not None
    assert closed.is_closed is True


def test_attach_screenshot_copies_the_file_and_records_its_path(
    journal_service: JournalService,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    screenshots_dir = tmp_path / "screenshots"
    monkeypatch.setattr(
        "ai_screener.journal.service.settings.JOURNAL_SCREENSHOTS_DIR",
        str(screenshots_dir),
    )

    source_file = tmp_path / "chart.png"
    source_file.write_bytes(b"fake-png-bytes")

    entry = journal_service.add_entry(symbol="RELIANCE.NS", entry_price=100.0)

    updated = journal_service.attach_screenshot(entry.id, str(source_file))

    assert updated.screenshot_path is not None
    stored_path = Path(updated.screenshot_path)
    assert stored_path.exists()
    assert stored_path.read_bytes() == b"fake-png-bytes"
    assert stored_path.parent == screenshots_dir


def test_attach_screenshot_raises_for_missing_source_file(
    journal_service: JournalService,
) -> None:
    entry = journal_service.add_entry(symbol="RELIANCE.NS", entry_price=100.0)

    with pytest.raises(ValidationError):
        journal_service.attach_screenshot(entry.id, "/does/not/exist.png")


def test_attach_screenshot_raises_for_unknown_entry(
    journal_service: JournalService,
    tmp_path: Path,
) -> None:
    source_file = tmp_path / "chart.png"
    source_file.write_bytes(b"data")

    with pytest.raises(ValidationError):
        journal_service.attach_screenshot(999, str(source_file))


def test_list_and_delete_entries(journal_service: JournalService) -> None:
    entry = journal_service.add_entry(symbol="RELIANCE.NS", entry_price=100.0)

    assert len(journal_service.list_entries()) == 1
    assert journal_service.delete_entry(entry.id) is True
    assert journal_service.list_entries() == []
