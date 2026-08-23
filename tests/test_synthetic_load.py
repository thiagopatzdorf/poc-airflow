from datetime import date, datetime, timezone

import pytest

from poc.synthetic_load import daily_target, expected_count, status_for


def test_daily_target_is_deterministic_and_bounded():
    target = daily_target(date(2026, 8, 23))
    assert target == daily_target(date(2026, 8, 23))
    assert 200 <= target <= 400


def test_expected_count_tracks_day_progress():
    assert expected_count(datetime(2026, 8, 23, 0, 0, tzinfo=timezone.utc), 240) == 0
    assert expected_count(datetime(2026, 8, 23, 12, 0, tzinfo=timezone.utc), 240) == 120
    assert expected_count(datetime(2026, 8, 24, 0, 0, tzinfo=timezone.utc), 240) == 0


def test_status_distribution_contains_operational_states():
    states = {status_for(i) for i in range(20)}
    assert states == {"COMPLETED", "AWAITING_SIGNATURES", "VALIDATED", "MANUAL_REVIEW", "QUARANTINED"}


def test_invalid_volume_range_is_rejected():
    with pytest.raises(ValueError):
        daily_target(date(2026, 8, 23), 400, 200)
