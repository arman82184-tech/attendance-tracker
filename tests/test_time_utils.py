import pytest

from app.utils.formatting import classes_text
from app.utils.time_utils import display_time, parse_date, parse_time


@pytest.mark.parametrize("text,expected", [
    ("23:21", "23:21"), ("11:23 PM", "23:23"), ("11:23 pm", "23:23"),
    ("12:05 AM", "00:05"), ("12:30 PM", "12:30"), ("2 PM", "14:00"),
    ("  08:10   PM ", "20:10"),
])
def test_parse_time(text, expected):
    assert parse_time(text) == expected


@pytest.mark.parametrize("bad", ["", "abc", "25:00", "13:00 PM", "9:75"])
def test_parse_time_rejects_garbage(bad):
    with pytest.raises(ValueError):
        parse_time(bad)


def test_parse_date():
    assert parse_date("2026-9-4") == "2026-09-04"
    with pytest.raises(ValueError):
        parse_date("04/09/2026")
    with pytest.raises(ValueError):
        parse_date("2026-02-30")


def test_display_time_never_crashes():
    assert display_time("23:21") == "11:21 PM"
    assert display_time("11:23 PM") == "11:23 PM"
    assert display_time("weird") == "weird"


def test_time_order_is_correct_after_normalising():
    # the old bug: as TEXT, "08:10 PM" sorted before "11:00 AM"
    times = ["11:00 AM", "08:10 PM", "09:00 AM"]
    assert sorted(parse_time(t) for t in times) == ["09:00", "11:00", "20:10"]


def test_classes_text():
    assert classes_text(1) == "1 class"
    assert classes_text(0) == "0 classes"
    assert classes_text(5) == "5 classes"
