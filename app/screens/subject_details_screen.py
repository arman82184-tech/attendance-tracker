from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDButton, MDButtonText
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.metrics import dp

from app.services.subject_service import get_subject
from app.services.attendance_service import get_attendance_for_subject
from app.services.attendance_service import delete_attendance
from app.config import MIN_ATTENDANCE
from app.utils.calculations import (
    calculate_subject_attendance,
    classes_needed_to_reach_target,
    classes_can_miss,
)
from app.utils.formatting import classes_text
from app.utils.time_utils import display_time


class SubjectDetailsScreen(MDScreen):

    subject_id = None

    def show_subject(self, subject_id):
        """Load and display details for the selected subject."""

        self.subject_id = subject_id

        subject = get_subject(subject_id)

        if subject is None:
            self.manager.current = "home"
            return

        records = get_attendance_for_subject(subject_id)

        stats = calculate_subject_attendance(records)

        percentage = stats["percentage"]
        
        minimum = f"{MIN_ATTENDANCE:.0f}%"

        if stats["total"] == 0:
            self.ids.target_message.text = "No attendance records yet."

        elif percentage < MIN_ATTENDANCE:
            needed = classes_needed_to_reach_target(
                stats["present"], stats["total"], MIN_ATTENDANCE
            )
            self.ids.target_message.text = (
                f"Below {minimum}\n"
                f"Attend the next {classes_text(needed)} "
                f"to reach {minimum}."
            )

        else:
            can_miss = classes_can_miss(
                stats["present"], stats["total"], MIN_ATTENDANCE
            )
            self.ids.target_message.text = (
                f"Attendance is safe\n"
                f"You can miss {classes_text(can_miss)} more "
                f"and stay at {minimum}."
            )

        self.ids.subject_name.text = (
            subject["subject_name"]
        )

        self.ids.subject_code.text = (
            subject["subject_code"]
        )

        self.ids.professor_name.text = (
            f'Professor: {subject["professor_name"]}'
        )

        self.ids.attendance_percentage.text = (
            f'{stats["percentage"]:.2f}%'
        )

        self.ids.present_classes.text = (
            f'Present: {stats["present"]}'
        )

        self.ids.absent_classes.text = (
            f'Absent: {stats["absent"]}'
        )

        self.ids.total_classes.text = (
            f'Total: {stats["total"]}'
        )

        self.load_attendance_history(records)

    def load_attendance_history(self, records):
        """Display attendance records."""

        self.ids.attendance_history.clear_widgets()

        if not records:

            empty_label = MDLabel(
                text="No attendance records yet.",
                halign="center",
                adaptive_height=True,
                font_size="16sp",
            )

            self.ids.attendance_history.add_widget(
                empty_label
            )

            return

        for record in records:

            card = self.create_attendance_card(
                record
            )

            self.ids.attendance_history.add_widget(
                card
            )

    def create_attendance_card(self, record):
        """Create an attendance history card."""

        card = MDCard(
            orientation="vertical",
            padding=dp(12),
            spacing=dp(8),
            size_hint_y=None,
            height=dp(105),
        )

        if record["status"] == "Present":
            status_text = "Present"
            status_color = (0.2, 0.7, 0.3, 1)
        else:
            status_text = "Absent"
            status_color = (0.9, 0.2, 0.2, 1)


        formatted_time = display_time(record["time"])

        info_label = MDLabel(
            text=(
                f'{record["date"]}    '
                f'{formatted_time}    '
                f'{status_text}'
            ),
            adaptive_height=True,
            font_size="16sp",
            theme_text_color="Custom",
            text_color=status_color,
        )

        button_layout = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(10),
            adaptive_height=True,
        )

        edit_button = MDButton(
            style="outlined",
        )

        edit_button.add_widget(
            MDButtonText(
                text="Edit"
            )
        )

        edit_button.bind(
            on_release=lambda instance:
            self.edit_attendance(record)
        )

        delete_button = MDButton(
            style="text",
        )

        delete_button.add_widget(
            MDButtonText(
                text="Delete"
            )
        )

        delete_button.bind(
            on_release=lambda instance:
            self.confirm_delete(record["id"])
        )

        button_layout.add_widget(edit_button)
        button_layout.add_widget(delete_button)

        card.add_widget(info_label)
        card.add_widget(button_layout)

        return card

    def edit_attendance(self, record):
        """Open edit attendance screen."""

        edit_screen = self.manager.get_screen(
            "edit_attendance"
        )

        edit_screen.load_record(record)

        self.manager.current = "edit_attendance"

    def confirm_delete(self, attendance_id):
        """Show delete confirmation."""
    
        self.delete_id = attendance_id
    
        layout = BoxLayout(
            orientation="vertical",
            spacing=dp(15),
            padding=dp(20),
        )
    
        message = Label(
            text="Are you sure you want to delete this attendance record?",
            halign="center",
            valign="middle",
        )
    
        message.bind(
            size=lambda instance, value:
            setattr(instance, "text_size", value)
        )
    
        buttons = BoxLayout(
            orientation="horizontal",
            spacing=dp(10),
            size_hint_y=None,
            height=dp(50),
        )
    
        cancel_button = MDButton(
            style="outlined",
        )
    
        cancel_button.add_widget(
            MDButtonText(
                text="Cancel"
            )
        )
    
        delete_button = MDButton(
            style="filled",
        )
    
        delete_button.add_widget(
            MDButtonText(
                text="Delete"
            )
        )
    
        buttons.add_widget(cancel_button)
        buttons.add_widget(delete_button)
    
        layout.add_widget(message)
        layout.add_widget(buttons)
    
        self.delete_popup = Popup(
            title="Delete Attendance?",
            content=layout,
            size_hint=(0.85, 0.35),
            auto_dismiss=False,
        )
    
        cancel_button.bind(
            on_release=lambda instance:
            self.delete_popup.dismiss()
        )
    
        delete_button.bind(
            on_release=lambda instance:
            self.delete_record()
        )
    
        self.delete_popup.open()

    def delete_record(self):
        """Delete the selected attendance record."""
    
        delete_attendance(self.delete_id)
    
        self.delete_popup.dismiss()
    
        self.show_subject(self.subject_id)

    def open_mark_attendance(self):
        """Open Mark Attendance screen."""

        mark_screen = self.manager.get_screen(
            "mark_attendance"
        )

        mark_screen.set_subject(
            self.subject_id
        )

        self.manager.current = "mark_attendance"

    def open_monthly_attendance(self):
        """Open monthly attendance screen."""
    
        monthly_screen = self.manager.get_screen(
            "monthly_attendance"
        )
    
        monthly_screen.show_month(
            self.subject_id
        )
    
        self.manager.current = "monthly_attendance"

    def go_back(self):
        """Return to home screen."""

        self.manager.current = "home"