from app.database.database import get_connection


def add_subject(subject_name, subject_code, professor_name):
    """Add a new subject to the database."""

    connection = get_connection()

    try:
        connection.execute(
            """
            INSERT INTO subjects
                (subject_name, subject_code, professor_name)
            VALUES (?, ?, ?)
            """,
            (subject_name, subject_code, professor_name)
        )

        connection.commit()

    finally:
        connection.close()


def get_all_subjects():
    """Return all subjects."""

    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            SELECT
                id,
                subject_name,
                subject_code,
                professor_name
            FROM subjects
            ORDER BY subject_name
            """
        )

        return cursor.fetchall()

    finally:
        connection.close()


def get_subject(subject_id):
    """Return one subject by ID."""

    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            SELECT
                id,
                subject_name,
                subject_code,
                professor_name
            FROM subjects
            WHERE id = ?
            """,
            (subject_id,)
        )

        return cursor.fetchone()

    finally:
        connection.close()


def update_subject(subject_id, subject_name, subject_code, professor_name):
    """Update an existing subject."""

    connection = get_connection()

    try:
        connection.execute(
            """
            UPDATE subjects
            SET
                subject_name = ?,
                subject_code = ?,
                professor_name = ?
            WHERE id = ?
            """,
            (
                subject_name,
                subject_code,
                professor_name,
                subject_id
            )
        )

        connection.commit()

    finally:
        connection.close()


def delete_subject(subject_id):
    """Delete a subject and its attendance records."""

    connection = get_connection()

    try:
        connection.execute(
            """
            DELETE FROM subjects
            WHERE id = ?
            """,
            (subject_id,)
        )

        connection.commit()

    finally:
        connection.close()