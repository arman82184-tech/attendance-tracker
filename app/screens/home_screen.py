from kivymd.uix.screen import MDScreen
from kivymd.uix.progressindicator import MDLinearProgressIndicator

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


class HomeScreen(MDScreen):

    MIN_ATTENDANCE = 75.0

    def on_enter(self):
        """Refresh dashboard whenever the screen is opened."""
        self.refresh_dashboard()

    def refresh_dashboard(self):
        """Load and display current attendance information."""

        # Get all attendance records
        all_records = get_all_attendance()

        # Calculate overall attendance
        statistics = calculate_subject_attendance(
            all_records
        )

        self.ids.overall_attendance.text = (
            f'{statistics["percentage"]:.2f}%'
        )

        percentage = statistics["percentage"]

        # Set overall progress bar value
        self.ids.overall_progress.value = percentage
        
        # Set progress bar color based on attendance
        if statistics["total"] == 0:
            self.ids.overall_progress.indicator_color = (
                0.5, 0.5, 0.5, 1
            )
        
        elif percentage < self.MIN_ATTENDANCE:
            self.ids.overall_progress.indicator_color = (
                0.9, 0.2, 0.2, 1
            )
        
        else:
            self.ids.overall_progress.indicator_color = (
                0.2, 0.7, 0.3, 1
            )     

        self.ids.overall_attendance.text = (
            f'{statistics["percentage"]:.2f}%'
        )  
        
        if statistics["total"] == 0:
            self.ids.overall_status.text = "No attendance records yet."
            self.ids.overall_status.text_color = (0.5, 0.5, 0.5, 1)
        
        elif percentage < self.MIN_ATTENDANCE:
            self.ids.overall_status.text = "WARNING: Overall attendance is below 75%"
            self.ids.overall_status.text_color = (0.9, 0.2, 0.2, 1)
        
        else:
            self.ids.overall_status.text = "OK: Overall attendance is safe"
            self.ids.overall_status.text_color = (0.2, 0.7, 0.3, 1)

        self.ids.total_classes.text = (
            f'Total Classes: {statistics["total"]}'
        )

        self.ids.present_classes.text = (
            f'Present: {statistics["present"]}'
        )

        self.ids.absent_classes.text = (
            f'Absent: {statistics["absent"]}'
        )

        # Load subjects
        subjects = get_all_subjects()

        # Clear old subject entries
        self.ids.subject_container.clear_widgets()

        # Add each subject
        for subject in subjects:

            records = get_attendance_for_subject(
                subject["id"]
            )

            stats = calculate_subject_attendance(
                records
            )

            percentage = stats["percentage"]

            self.ids.subject_container.add_widget(
                self.create_subject_label(
                    subject,
                    percentage
                )
            )

    def create_subject_label(self, subject, percentage):
        """Create a clickable subject card."""
    
        from kivymd.uix.card import MDCard
        from kivymd.uix.label import MDLabel
        from kivymd.uix.progressindicator import MDLinearProgressIndicator
        from kivy.metrics import dp
    
        records = get_attendance_for_subject(subject["id"])
    
        stats = calculate_subject_attendance(records)
    
        if stats["total"] == 0:
            status = "NO DATA"
            target_text = "No attendance records yet."
        
        elif percentage < self.MIN_ATTENDANCE:
            status = "WARNING"
            needed = classes_needed_to_reach_target(
                stats["present"],
                stats["total"]
            )
            target_text = (
                f"Attend next {needed} class"
                f"{'es' if needed != 1 else ''} "
                f"to reach 75%"
            )
        
        else:
            status = "OK"
            can_miss = classes_can_miss(
                stats["present"],
                stats["total"]
            )
            target_text = (
                f"Can miss {can_miss} class"
                f"{'es' if can_miss != 1 else ''} "
                f"and stay at 75%"
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
            text=(
                f"{status}  {subject['subject_name']}"
            ),
            font_size="19sp",
            bold=True,
            adaptive_height=True,
        )
    
        code_label = MDLabel(
            text=(
                f"{subject['subject_code']}  •  "
                f"{subject['professor_name']}"
            ),
            font_size="14sp",
            adaptive_height=True,
        )

        if percentage < self.MIN_ATTENDANCE:
            progress_color = (0.9, 0.2, 0.2, 1)
        else:
            progress_color = (0.2, 0.7, 0.3, 1)
        
        progress_bar = MDLinearProgressIndicator(
            value=percentage,
            type="determinate",
            indicator_color=progress_color,
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
            text=f"Target: {self.MIN_ATTENDANCE:.0f}%\n{target_text}",
            font_size="14sp",
            adaptive_height=True,
            halign="center",
            text_size=(None, None),
        )
    
        card.add_widget(name_label)
        card.add_widget(code_label)
        card.add_widget(progress_bar)
        card.add_widget(attendance_label)
        card.add_widget(target_label)
    
        card.bind(
            on_release=lambda instance: (
                self.open_subject(subject["id"])
            )
        )
    
        return card


    def open_subject(self, subject_id):
        """Open the details screen for a subject."""
    
        details_screen = self.manager.get_screen(
            "subject_details"
        )
    
        details_screen.show_subject(subject_id)
    
        self.manager.current = "subject_details"