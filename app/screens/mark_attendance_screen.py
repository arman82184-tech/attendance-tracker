from datetime import datetime

from kivymd.uix.screen import MDScreen

from app.services.attendance_service import add_attendance


class MarkAttendanceScreen(MDScreen):

    subject_id = None

    def on_pre_enter(self):
        """Set the default date and time whenever the screen opens."""

        now = datetime.now()

        self.ids.date_field.text = now.strftime("%Y-%m-%d")
        self.ids.time_field.text = now.strftime("%I:%M %p")

        self.ids.status_label.text = "Status: Not selected"

    def set_subject(self, subject_id):
        """Store the subject for which attendance is being marked."""

        self.subject_id = subject_id

    def set_status(self, status):
        """Set attendance status."""

        self.ids.status_label.text = f"Status: {status}"
        self.selected_status = status

    def save_attendance(self):
        """Save the attendance record."""

        date = self.ids.date_field.text.strip()
        time = self.ids.time_field.text.strip()

        if not date or not time:
            self.ids.error_label.text = "Please enter date and time."
            return

        if not hasattr(self, "selected_status"):
            self.ids.error_label.text = "Please select Present or Absent."
            return

        if self.subject_id is None:
            self.ids.error_label.text = "No subject selected."
            return

        add_attendance(
            self.subject_id,
            date,
            time,
            self.selected_status
        )

        self.ids.error_label.text = ""

        self.manager.current = "subject_details"

        details_screen = self.manager.get_screen(
            "subject_details"
        )

        details_screen.show_subject(self.subject_id)

    def go_back(self):
        """Return to subject details."""

        self.manager.current = "subject_details"