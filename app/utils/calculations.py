import math
from fractions import Fraction

from app.config import MIN_ATTENDANCE


def calculate_attendance(present, total):
    """Calculate attendance percentage."""

    if total == 0:
        return 0.0

    return (present / total) * 100


def get_attendance_counts(records):
    """Calculate present, absent and total classes."""

    total = len(records)

    present = sum(
        1 for record in records
        if record["status"] == "Present"
    )

    absent = total - present

    return present, absent, total


def calculate_subject_attendance(records):
    """Calculate attendance statistics for a subject."""

    present, absent, total = get_attendance_counts(records)

    return {
        "present": present,
        "absent": absent,
        "total": total,
        "percentage": calculate_attendance(present, total),
    }


def classes_needed_to_reach_target(present, total, target=MIN_ATTENDANCE):
    """Consecutive classes that must be attended to reach the target %.

    Uses exact arithmetic (no float rounding) and a closed-form formula,
    so it can never loop forever.  Solves (p + x) / (t + x) >= target/100.
    """

    if not 0 < target < 100:
        raise ValueError("target must be between 0 and 100 (exclusive)")

    if total == 0:
        return 0

    target = Fraction(str(target))

    if present * 100 >= target * total:
        return 0

    return math.ceil((target * total - 100 * present) / (100 - target))


def classes_can_miss(present, total, target=MIN_ATTENDANCE):
    """Classes that can still be missed while staying at/above the target %.

    Solves p / (t + k) >= target/100 for the largest whole k.
    """

    if not 0 < target <= 100:
        raise ValueError("target must be above 0 and at most 100")

    if total == 0:
        return 0

    target = Fraction(str(target))

    if present * 100 < target * total:
        return 0

    return math.floor((100 * present - target * total) / target)
