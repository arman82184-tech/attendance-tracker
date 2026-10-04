from datetime import datetime

from kivymd.uix.screen import MDScreen

from app.config import DATE_FORMAT, DISPLAY_TIME_FORMAT
from app.services.attendance_service import add_attendance
from app.utils.time_utils import parse_date, parse_time


class MarkAttendanceScreen(MDScreen):

    subject_id = None
    selected_status = None

    def on_pre_enter(self):
        """Reset the form whenever the screen opens."""

        now = datetime.now()

        self.ids.date_field.text = now.strftime(DATE_FORMAT)
        self.ids.time_field.text = now.strftime(DISPLAY_TIME_FORMAT)

        # Forget the previous choice, otherwise the label says
        # "Not selected" while an old status would still be saved.
        self.selected_status = None
        self.ids.status_label.text = "Status: Not selected"
        self.ids.error_label.text = ""

    def set_subject(self, subject_id):
        """Store the subject for which attendance is being marked."""

        self.subject_id = subject_id

    def set_status(self, status):
        """Set attendance status."""

        self.ids.status_label.text = f"Status: {status}"
        self.selected_status = status

    def save_attendance(self):
        """Validate and save the attendance record."""

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
                "Attendance cannot be marked for a future date."
            )
            return

        if self.selected_status is None:
            self.ids.error_label.text = "Please select Present or Absent."
            return

        if self.subject_id is None:
            self.ids.error_label.text = "No subject selected."
            return

        add_attendance(self.subject_id, date, time, self.selected_status)

        self.ids.error_label.text = ""

        details_screen = self.manager.get_screen("subject_details")
        details_screen.show_subject(self.subject_id)

        self.manager.current = "subject_details"

    def go_back(self):
        """Return to subject details."""

        self.manager.current = "subject_details"
