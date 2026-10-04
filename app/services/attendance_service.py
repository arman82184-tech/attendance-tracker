from app.database.database import get_connection


def add_attendance(subject_id, date, time, status):
    """Add an attendance record."""

    connection = get_connection()

    try:
        connection.execute(
            """
            INSERT INTO attendance
                (subject_id, date, time, status)
            VALUES (?, ?, ?, ?)
            """,
            (subject_id, date, time, status)
        )

        connection.commit()

    finally:
        connection.close()


def get_all_attendance():
    """Return all attendance records with subject information."""

    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            SELECT
                attendance.id,
                attendance.subject_id,
                subjects.subject_name,
                subjects.subject_code,
                subjects.professor_name,
                attendance.date,
                attendance.time,
                attendance.status

            FROM attendance

            INNER JOIN subjects
                ON attendance.subject_id = subjects.id

            ORDER BY
                attendance.date DESC,
                attendance.time DESC
            """
        )

        return cursor.fetchall()

    finally:
        connection.close()


def get_attendance_for_subject(subject_id):
    """Return attendance records for one subject."""

    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            SELECT
                attendance.id,
                attendance.subject_id,
                subjects.subject_name,
                subjects.subject_code,
                subjects.professor_name,
                attendance.date,
                attendance.time,
                attendance.status

            FROM attendance

            INNER JOIN subjects
                ON attendance.subject_id = subjects.id

            WHERE attendance.subject_id = ?

            ORDER BY
                attendance.date DESC,
                attendance.time DESC
            """,
            (subject_id,)
        )

        return cursor.fetchall()

    finally:
        connection.close()


def update_attendance(attendance_id, date, time, status):
    """Update an attendance record."""

    connection = get_connection()

    try:
        connection.execute(
            """
            UPDATE attendance

            SET
                date = ?,
                time = ?,
                status = ?

            WHERE id = ?
            """,
            (
                date,
                time,
                status,
                attendance_id
            )
        )

        connection.commit()

    finally:
        connection.close()


def delete_attendance(attendance_id):
    """Delete an attendance record."""

    connection = get_connection()

    try:
        connection.execute(
            """
            DELETE FROM attendance
            WHERE id = ?
            """,
            (attendance_id,)
        )

        connection.commit()

    finally:
        connection.close()