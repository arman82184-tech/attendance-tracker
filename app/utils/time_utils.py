"""Helpers to validate and convert dates/times.

Rule: the database always stores time as 24-hour "HH:MM".
The UI shows it as 12-hour "hh:MM AM/PM" and accepts either when typing.
"""

from datetime import datetime

from app.config import DATE_FORMAT, DB_TIME_FORMAT, DISPLAY_TIME_FORMAT

_ACCEPTED_TIME_FORMATS = (
    DB_TIME_FORMAT,        # 14:30
    DISPLAY_TIME_FORMAT,   # 02:30 PM
    "%I:%M%p",             # 02:30PM
    "%I %p",               # 2 PM
)


def parse_date(text):
    """Return the date as 'YYYY-MM-DD'. Raise ValueError if invalid."""
    return datetime.strptime(text.strip(), DATE_FORMAT).strftime(DATE_FORMAT)


def parse_time(text):
    """Return the time as 24-hour 'HH:MM'. Raise ValueError if invalid."""
    cleaned = " ".join(text.strip().upper().split())

    for fmt in _ACCEPTED_TIME_FORMATS:
        try:
            return datetime.strptime(cleaned, fmt).strftime(DB_TIME_FORMAT)
        except ValueError:
            continue

    raise ValueError(f"Invalid time: {text!r}")


def display_time(stored_time):
    """Convert a stored time to 12-hour format for display.

    Never raises: unknown text is returned unchanged.
    """
    try:
        return datetime.strptime(
            parse_time(stored_time), DB_TIME_FORMAT
        ).strftime(DISPLAY_TIME_FORMAT)
    except ValueError:
        return stored_time
