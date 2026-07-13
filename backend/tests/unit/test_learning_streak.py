from datetime import date, timedelta

from app.services.learning import compute_streak

# 2026-07-10 is a Friday (weekday 4)
FRIDAY = date(2026, 7, 10)
SATURDAY = FRIDAY + timedelta(days=1)
SUNDAY = FRIDAY + timedelta(days=2)
MONDAY = FRIDAY + timedelta(days=3)


def days_before(d: date, n: int) -> set[date]:
    return {d - timedelta(days=i) for i in range(n)}


def test_empty_log_is_zero():
    assert compute_streak(set(), set(), FRIDAY) == 0


def test_consecutive_days():
    assert compute_streak(days_before(FRIDAY, 3), set(), FRIDAY) == 3


def test_today_unlogged_does_not_break_streak():
    logged = days_before(FRIDAY - timedelta(days=1), 3)
    assert compute_streak(logged, set(), FRIDAY) == 3


def test_gap_breaks_streak():
    logged = {FRIDAY, FRIDAY - timedelta(days=2)}
    assert compute_streak(logged, set(), FRIDAY) == 1


def test_rest_day_does_not_break_streak():
    # Logged Fri + Sat, Sunday (6) is rest, checking on Monday
    logged = {FRIDAY, SATURDAY, MONDAY}
    assert compute_streak(logged, {6}, MONDAY) == 3


def test_rest_day_log_still_counts():
    logged = {FRIDAY, SATURDAY, SUNDAY, MONDAY}
    assert compute_streak(logged, {6}, MONDAY) == 4


def test_missed_scheduled_day_breaks_despite_rest_days():
    # Saturday missed (not a rest day) → only Monday counts
    logged = {FRIDAY, MONDAY}
    assert compute_streak(logged, {6}, MONDAY) == 1
