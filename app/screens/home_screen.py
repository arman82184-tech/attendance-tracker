from kivy.metrics import dp

from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.progressindicator import MDLinearProgressIndicator
from kivymd.uix.screen import MDScreen

from app.config import MIN_ATTENDANCE
from app.services.subject_service import get_all_subjects
from app.services.attendance_service import (
    get_all_attendance,
    get_attendance_for_subject,
)
from app.utils.calculations import (
    calculate_subject_attendance,
    classes_needed_to_reach_target,
    classes_can_miss,
)
from app.utils.formatting import classes_text

GREY = (0.5, 0.5, 0.5, 1)
RED = (0.9, 0.2, 0.2, 1)
GREEN = (0.2, 0.7, 0.3, 1)


class HomeScreen(MDScreen):

    MIN_ATTENDANCE = MIN_ATTENDANCE

    def on_enter(self):
        """Refresh dashboard whenever the screen is opened."""
        self.refresh_dashboard()

    def refresh_dashboard(self):
        """Load and display current attendance information."""

        statistics = calculate_subject_attendance(get_all_attendance())
        percentage = statistics["percentage"]
        minimum = f"{self.MIN_ATTENDANCE:.0f}%"

        self.ids.overall_attendance.text = f"{percentage:.2f}%"
        self.ids.overall_progress.value = percentage

        if statistics["total"] == 0:
            colour = GREY
            message = "No attendance records yet."
        elif percentage < self.MIN_ATTENDANCE:
            colour = RED
            message = f"WARNING: Overall attendance is below {minimum}"
        else:
            colour = GREEN
            message = "OK: Overall attendance is safe"

        self.ids.overall_progress.indicator_color = colour
        self.ids.overall_status.text = message
        self.ids.overall_status.text_color = colour

        self.ids.total_classes.text = f'Total Classes: {statistics["total"]}'
        self.ids.present_classes.text = f'Present: {statistics["present"]}'
        self.ids.absent_classes.text = f'Absent: {statistics["absent"]}'

        # Rebuild the subject cards
        self.ids.subject_container.clear_widgets()

        for subject in get_all_subjects():
            # One query per subject (the old code ran it twice)
            stats = calculate_subject_attendance(
                get_attendance_for_subject(subject["id"])
            )

            self.ids.subject_container.add_widget(
                self.create_subject_card(subject, stats)
            )

    def create_subject_card(self, subject, stats):
        """Create a clickable subject card."""

        percentage = stats["percentage"]
        minimum = f"{self.MIN_ATTENDANCE:.0f}%"

        if stats["total"] == 0:
            status = "NO DATA"
            colour = GREY
            target_text = "No attendance records yet."

        elif percentage < self.MIN_ATTENDANCE:
            status = "WARNING"
            colour = RED
            needed = classes_needed_to_reach_target(
                stats["present"], stats["total"], self.MIN_ATTENDANCE
            )
            target_text = (
                f"Attend next {classes_text(needed)} to reach {minimum}"
            )

        else:
            status = "OK"
            colour = GREEN
            can_miss = classes_can_miss(
                stats["present"], stats["total"], self.MIN_ATTENDANCE
            )
            target_text = (
                f"Can miss {classes_text(can_miss)} and stay at {minimum}"
            )

        card = MDCard(
            orientation="vertical",
            padding=dp(15),
            spacing=dp(5),
            size_hint_y=None,
            height=dp(190),
            ripple_behavior=True,
        )

        name_label = MDLabel(
            text=f"{status}  {subject['subject_name']}",
            font_size="19sp",
            bold=True,
            adaptive_height=True,
        )

        code_label = MDLabel(
            text=f"{subject['subject_code']}  •  {subject['professor_name']}",
            font_size="14sp",
            adaptive_height=True,
        )

        progress_bar = MDLinearProgressIndicator(
            value=percentage,
            type="determinate",
            indicator_color=colour,
            size_hint_y=None,
            height=dp(8),
        )

        attendance_label = MDLabel(
            text=(
                f"Present: {stats['present']}    "
                f"Absent: {stats['absent']}    "
                f"Total: {stats['total']}    "
                f"Attendance: {percentage:.2f}%"
            ),
            font_size="15sp",
            adaptive_height=True,
        )

        target_label = MDLabel(
            text=f"Target: {minimum}\n{target_text}",
            font_size="14sp",
            adaptive_height=True,
            halign="center",
        )
        # (the old text_size=(None, None) switched centering off)
        target_label.bind(
            width=lambda label, width: setattr(label, "text_size", (width, None))
        )

        card.add_widget(name_label)
        card.add_widget(code_label)
        card.add_widget(progress_bar)
        card.add_widget(attendance_label)
        card.add_widget(target_label)

        subject_id = subject["id"]
        card.bind(on_release=lambda instance: self.open_subject(subject_id))

        return card

    def open_subject(self, subject_id):
        """Open the details screen for a subject."""

        details_screen = self.manager.get_screen("subject_details")
        details_screen.show_subject(subject_id)

        self.manager.current = "subject_details"
