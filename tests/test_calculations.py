import pytest

from app.utils.calculations import (
    calculate_attendance,
    classes_can_miss,
    classes_needed_to_reach_target,
)


def brute_needed(p, t, target):
    x = 0
    while (p + x) * 100 < target * (t + x):
        x += 1
    return x


def brute_miss(p, t, target):
    k = 0
    while p * 100 >= target * (t + k + 1):
        k += 1
    return k


def test_percentage_and_empty():
    assert calculate_attendance(3, 4) == 75.0
    assert calculate_attendance(0, 0) == 0.0


@pytest.mark.parametrize("p,t", [(0, 1), (1, 2), (3, 4), (5, 10), (20, 30), (74, 100)])
def test_needed_matches_brute_force(p, t):
    if p * 100 < 75 * t:
        assert classes_needed_to_reach_target(p, t, 75) == brute_needed(p, t, 75)
    else:
        assert classes_needed_to_reach_target(p, t, 75) == 0


@pytest.mark.parametrize("p,t", [(3, 4), (9, 10), (15, 20), (30, 30), (6, 8)])
def test_can_miss_matches_brute_force(p, t):
    assert classes_can_miss(p, t, 75) == brute_miss(p, t, 75)


def test_exactly_at_target_needs_nothing():
    assert classes_needed_to_reach_target(3, 4) == 0
    assert classes_can_miss(3, 4) == 0


def test_no_infinite_loops_on_bad_targets():
    with pytest.raises(ValueError):
        classes_needed_to_reach_target(3, 10, 100)   # used to hang forever
    with pytest.raises(ValueError):
        classes_can_miss(5, 5, 0)                    # used to hang forever
