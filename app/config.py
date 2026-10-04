"""Central place for app-wide settings (no more magic numbers)."""

# Minimum attendance percentage required (used by every screen).
MIN_ATTENDANCE = 75.0

# How dates/times are STORED in the database.
DATE_FORMAT = "%Y-%m-%d"      # 2026-09-04
DB_TIME_FORMAT = "%H:%M"      # 24-hour, e.g. 23:21 (sorts correctly as text)

# How times are SHOWN to the user.
DISPLAY_TIME_FORMAT = "%I:%M %p"   # 11:21 PM
