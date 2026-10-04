import sqlite3

import pytest

from app.database import database
from app.services import attendance_service as att
from app.services import subject_service as subj


@pytest.fixture()
def db(tmp_path):
    database.configure_database(tmp_path / "test.db")
    database.initialize_database()
    yield


def test_duplicate_subject_code_raises_integrity_error(db):
    subj.add_subject("Maths", "M1", "Dr A")
    with pytest.raises(sqlite3.IntegrityError):
        subj.add_subject("Maths 2", "M1", "Dr B")


def test_history_is_sorted_newest_first_with_24h_times(db):
    subj.add_subject("Maths", "M1", "Dr A")
    sid = subj.get_all_subjects()[0]["id"]
    att.add_attendance(sid, "2026-09-04", "09:00", "Present")
    att.add_attendance(sid, "2026-09-04", "20:10", "Absent")
    att.add_attendance(sid, "2026-09-04", "11:00", "Present")
    times = [r["time"] for r in att.get_attendance_for_subject(sid)]
    assert times == ["20:10", "11:00", "09:00"]


def test_delete_subject_cascades(db):
    subj.add_subject("Maths", "M1", "Dr A")
    sid = subj.get_all_subjects()[0]["id"]
    att.add_attendance(sid, "2026-09-04", "09:00", "Present")
    subj.delete_subject(sid)
    assert att.get_all_attendance() == []


def test_legacy_12_hour_times_are_migrated(tmp_path):
    database.configure_database(tmp_path / "old.db")
    database.initialize_database()
    subj.add_subject("Maths", "M1", "Dr A")
    sid = subj.get_all_subjects()[0]["id"]
    con = database.get_connection()
    con.execute("INSERT INTO attendance (subject_id,date,time,status) VALUES (?,?,?,?)",
                (sid, "2026-09-04", "11:23 PM", "Absent"))
    con.execute("INSERT INTO attendance (subject_id,date,time,status) VALUES (?,?,?,?)",
                (sid, "2026-09-04", "09:05 AM", "Present"))
    con.commit(); con.close()

    database.initialize_database()   # runs the clean-up again on app start

    times = sorted(r["time"] for r in att.get_attendance_for_subject(sid))
    assert times == ["09:05", "23:23"]
