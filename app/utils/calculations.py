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

    percentage = calculate_attendance(
        present,
        total
    )

    return {
        "present": present,
        "absent": absent,
        "total": total,
        "percentage": percentage,
    }


def classes_needed_to_reach_target(
    present,
    total,
    target=75.0
):
    """Calculate classes that must be attended to reach target."""

    if total == 0:
        return 0

    if (present / total) * 100 >= target:
        return 0

    classes_needed = 0

    while (
        (present + classes_needed)
        / (total + classes_needed)
    ) * 100 < target:

        classes_needed += 1

    return classes_needed


def classes_can_miss(
    present,
    total,
    target=75.0
):
    """Calculate classes that can be missed while staying at target."""

    if total == 0:
        return 0

    if (present / total) * 100 < target:
        return 0

    classes_can_miss = 0

    while (
        present
        / (total + classes_can_miss + 1)
    ) * 100 >= target:

        classes_can_miss += 1

    return classes_can_miss