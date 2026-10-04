from datetime import datetime

from kivymd.uix.screen import MDScreen

from app.services.attendance_service import update_attendance
from app.services.attendance_service import get_all_attendance


class EditAttendanceScreen(MDScreen):

    attendance_id = None
    subject_id = None

    original_status = None

    def load_record(self, record):
        """Load an attendance record into the edit form."""

        self.attendance_id = record["id"]
        self.subject_id = record["subject_id"]
        self.original_status = record["status"]

        self.ids.date_field.text = record["date"]

        try:
            formatted_time = datetime.strptime(
                record["time"],
                "%H:%M"
            ).strftime("%I:%M %p")
        except ValueError:
            formatted_time = record["time"]
        
        self.ids.time_field.text = formatted_time

        self.selected_status = record["status"]

        self.ids.status_label.text = (
            f'Status: {record["status"]}'
        )

        self.ids.error_label.text = ""

    def set_status(self, status):
        """Set the selected attendance status."""

        self.selected_status = status

        self.ids.status_label.text = (
            f"Status: {status}"
        )

    def save_changes(self):
        """Save changes to the attendance record."""

        date = self.ids.date_field.text.strip()
        time = self.ids.time_field.text.strip()

        if not date or not time:
            self.ids.error_label.text = (
                "Please enter date and time."
            )
            return

        if not hasattr(self, "selected_status"):
            self.ids.error_label.text = (
                "Please select Present or Absent."
            )
            return

        update_attendance(
            self.attendance_id,
            date,
            time,
            self.selected_status
        )

        details_screen = self.manager.get_screen(
            "subject_details"
        )

        details_screen.show_subject(
            self.subject_id
        )

        self.manager.current = "subject_details"

    def go_back(self):
        """Return to subject details."""

        self.manager.current = "subject_details"