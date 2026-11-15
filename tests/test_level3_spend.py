"""Level 3 spend ledger tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from pinconv2.level3_spend import Level3Ledger


def test_level3_spend_tracks_steps_and_cap(tmp_path: Path) -> None:
    ledger = Level3Ledger(tmp_path / "level3-spend.jsonl")
    ledger.zero("stock-sourcing", "stock", "candidate fetch")
    reservation = ledger.reserve("hero-generation", "fal", "brand sting", 0.5)
    ledger.receipt(reservation, 0.4)
    assert ledger.spent() == 0.4
    assert ledger.remaining() == 1.6
    assert ledger.summary()["within_cap"] is True

    with pytest.raises(ValueError):
        ledger.reserve("oversized", "fal", "too much", 2.0)
