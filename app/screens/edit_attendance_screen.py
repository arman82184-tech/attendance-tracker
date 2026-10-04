from datetime import datetime

from kivymd.uix.screen import MDScreen

from app.config import DATE_FORMAT
from app.services.attendance_service import update_attendance
from app.utils.time_utils import display_time, parse_date, parse_time


class EditAttendanceScreen(MDScreen):

    attendance_id = None
    subject_id = None

    original_status = None
    selected_status = None

    def load_record(self, record):
        """Load an attendance record into the edit form."""

        self.attendance_id = record["id"]
        self.subject_id = record["subject_id"]
        self.original_status = record["status"]

        self.ids.date_field.text = record["date"]
        self.ids.time_field.text = display_time(record["time"])

        self.selected_status = record["status"]

        self.ids.status_label.text = f'Status: {record["status"]}'
        self.ids.error_label.text = ""

    def set_status(self, status):
        """Set the selected attendance status."""

        self.selected_status = status
        self.ids.status_label.text = f"Status: {status}"

    def save_changes(self):
        """Validate and save changes to the attendance record."""

        date_text = self.ids.date_field.text.strip()
        time_text = self.ids.time_field.text.strip()

        if not date_text or not time_text:
            self.ids.error_label.text = "Please enter date and time."
            return

        try:
            date = parse_date(date_text)
        except ValueError:
            self.ids.error_label.text = "Date must look like 2026-09-24."
            return

        try:
            time = parse_time(time_text)
        except ValueError:
            self.ids.error_label.text = (
                "Time must look like 14:30 or 02:30 PM."
            )
            return

        if date > datetime.now().strftime(DATE_FORMAT):
            self.ids.error_label.text = (
                "Attendance cannot be set for a future date."
            )
            return

        if self.selected_status is None:
            self.ids.error_label.text = "Please select Present or Absent."
            return

        update_attendance(
            self.attendance_id, date, time, self.selected_status
        )

        details_screen = self.manager.get_screen("subject_details")
        details_screen.show_subject(self.subject_id)

        self.manager.current = "subject_details"

    def go_back(self):
        """Return to subject details."""

        self.manager.current = "subject_details"
