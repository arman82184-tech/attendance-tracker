from datetime import datetime

from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout

from kivy.metrics import dp
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout

from app.services.attendance_service import get_attendance_for_subject



class CalendarDayCard(MDCard):
    def __init__(self, day=None, screen=None, **kwargs):
        super().__init__(**kwargs)
        self.day = day
        self.screen = screen

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            if self.day is not None and self.screen is not None:
                self.screen.show_day_details(self.day)
    
        return super().on_touch_up(touch)


class MonthlyAttendanceScreen(MDScreen):
    subject_id = None
    month = None
    year = None

    def show_month(self, subject_id, month=None, year=None):
        if month is None:
            month = datetime.now().month

        if year is None:
            year = datetime.now().year

        self.subject_id = subject_id
        self.month = month
        self.year = year

        self.ids.month_title.text = datetime(
            year, month, 1
        ).strftime("%B %Y")

        self.create_calendar()

    def create_calendar(self):
        # Remove all existing date cells
        self.ids.calendar_grid.clear_widgets()
    
        # Get attendance records for this subject
        records = get_attendance_for_subject(self.subject_id)
    
        # Group attendance by date
        attendance_data = {}
    
        for record in records:
            date = record["date"]
    
            if date not in attendance_data:
                attendance_data[date] = []
    
            attendance_data[date].append(record["status"])
    
        # First day of the month
        first_day = datetime(
            self.year,
            self.month,
            1
        )
    
        # Monday = 0, Sunday = 6
        starting_day = first_day.weekday()
    
        # Find number of days in the month
        if self.month == 12:
            next_month = datetime(
                self.year + 1,
                1,
                1
            )
        else:
            next_month = datetime(
                self.year,
                self.month + 1,
                1
            )
    
        days_in_month = (
            next_month - first_day
        ).days
    
        # Empty cells before day 1
        for _ in range(starting_day):
            self.add_empty_cell()
    
        # Actual dates
        for day in range(1, days_in_month + 1):
            date_string = datetime(
                self.year,
                self.month,
                day
            ).strftime("%Y-%m-%d")
    
            statuses = attendance_data.get(
                date_string,
                []
            )
    
            self.add_date_cell(day, statuses)

    def add_empty_cell(self):
        cell = MDCard(
            size_hint=(1, None),
            height=dp(70),
            elevation=0,
            radius=[dp(8)],
        )

        self.ids.calendar_grid.add_widget(cell)

    def add_date_cell(self, day, statuses):
        cell = CalendarDayCard(
            day=day,
            screen=self,
            orientation="vertical",
            size_hint=(1, None),
            height=dp(70),
            padding=dp(5),
            elevation=1,
            radius=[dp(8)],
        )
    
        date_label = MDLabel(
            text=str(day),
            halign="center",
            valign="center",
            font_size="18sp",
            bold=True,
            size_hint_y=None,
            height=dp(30),
        )
    
        present_count = statuses.count("Present")
        absent_count = statuses.count("Absent")
    
        cell.add_widget(date_label)
    
        # Status row
        status_row = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(25),
            spacing=dp(2),
        )
    
        if present_count > 0:
            present_label = MDLabel(
                text=f"{present_count}P",
                halign="center",
                font_size="14sp",
                bold=True,
                theme_text_color="Custom",
                text_color=(0.2, 0.7, 0.3, 1),
            )
            status_row.add_widget(present_label)
    
        if absent_count > 0:
            absent_label = MDLabel(
                text=f"{absent_count}A",
                halign="center",
                font_size="14sp",
                bold=True,
                theme_text_color="Custom",
                text_color=(0.9, 0.2, 0.2, 1),
            )
            status_row.add_widget(absent_label)
    
        cell.add_widget(status_row)
    
        self.ids.calendar_grid.add_widget(cell)


    def show_day_details(self, day):
        date_string = datetime(
            self.year,
            self.month,
            day
        ).strftime("%Y-%m-%d")
    
        records = get_attendance_for_subject(self.subject_id)
    
        day_records = []
    
        for record in records:
            if record["date"] == date_string:
                day_records.append(record)
    
        # Create full-screen overlay
        overlay = FloatLayout(
            size_hint=(1, 1)
        )
    
        # Background card
        dialog_card = MDCard(
            size_hint=(0.85, 0.7),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            orientation="vertical",
            padding=dp(15),
            spacing=dp(10),
            elevation=8,
            radius=[dp(12)],
        )
    
        # Title
        title_label = MDLabel(
            text=datetime(
                self.year,
                self.month,
                day
            ).strftime("%B %d, %Y"),
            halign="center",
            font_size="20sp",
            bold=True,
            size_hint_y=None,
            height=dp(40),
        )
    
        dialog_card.add_widget(title_label)
    
        # Attendance records
        if not day_records:
    
            message = MDLabel(
                text="No attendance recorded for this day.",
                halign="center",
                valign="center",
            )
    
            dialog_card.add_widget(message)
    
        else:
    
            day_records.sort(
                key=lambda record: record["time"]
            )
    
            for record in day_records:
    
                try:
                    formatted_time = datetime.strptime(
                        record["time"],
                        "%H:%M"
                    ).strftime("%I:%M %p")
    
                except ValueError:
                    formatted_time = record["time"]
    
                if record["status"] == "Present":
                    status_color = (0.2, 0.7, 0.3, 1)
                else:
                    status_color = (0.9, 0.2, 0.2, 1)
    
                row = MDCard(
                    orientation="horizontal",
                    size_hint_y=None,
                    height=dp(55),
                    padding=dp(10),
                    elevation=1,
                    radius=[dp(8)],
                )
    
                time_label = MDLabel(
                    text=formatted_time,
                    halign="left",
                    valign="center",
                    font_size="16sp",
                )
    
                status_label = MDLabel(
                    text=record["status"],
                    halign="right",
                    valign="center",
                    font_size="16sp",
                    bold=True,
                    theme_text_color="Custom",
                    text_color=status_color,
                )
    
                row.add_widget(time_label)
                row.add_widget(status_label)
    
                dialog_card.add_widget(row)
    
        # Add the dialog card first
        overlay.add_widget(dialog_card)
        
        # Close button
        close_button = Button(
            text="CLOSE",
            size_hint=(0.75, None),
            height=dp(45),
            pos_hint={
                "center_x": 0.5,
                "center_y": 0.20,
            },
        )
        
        # Add button directly to the overlay
        # so the MDCard cannot interfere with its touch.
        overlay.add_widget(close_button)
        
        
        def close_overlay(instance):
            self.remove_widget(overlay)
        
        
        close_button.bind(
            on_release=close_overlay
        )
    
        # Add overlay directly to the screen
        self.add_widget(overlay)

    def previous_month(self):
        if self.month == 1:
            self.month = 12
            self.year -= 1
        else:
            self.month -= 1

        self.show_month(
            self.subject_id,
            self.month,
            self.year
        )

    def next_month(self):
        if self.month == 12:
            self.month = 1
            self.year += 1
        else:
            self.month += 1

        self.show_month(
            self.subject_id,
            self.month,
            self.year
        )

    def go_back(self):
        details_screen = self.manager.get_screen(
            "subject_details"
        )

        details_screen.show_subject(
            self.subject_id
        )

        self.manager.current = "subject_details"