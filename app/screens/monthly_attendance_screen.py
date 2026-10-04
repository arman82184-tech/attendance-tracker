from datetime import datetime

from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout

from kivy.graphics import Color, Rectangle
from kivy.metrics import dp
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView

from kivymd.uix.button import MDButton, MDButtonText

from app.config import DATE_FORMAT
from app.services.attendance_service import get_attendance_for_subject
from app.utils.time_utils import display_time



class CalendarOverlay(FloatLayout):
    """Full-screen layer that swallows touches so the calendar behind
    it cannot be clicked while a day dialog is open."""

    def on_touch_down(self, touch):
        super().on_touch_down(touch)   # let the CLOSE button work
        return True

    def on_touch_move(self, touch):
        super().on_touch_move(touch)
        return True

    def on_touch_up(self, touch):
        super().on_touch_up(touch)
        return True


class CalendarDayCard(MDCard):

    def __init__(self, day=None, screen=None, **kwargs):
        super().__init__(**kwargs)
        self.day = day
        self.screen = screen

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            touch.ud["day_card_start"] = (id(self), touch.pos)
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        started = touch.ud.get("day_card_start")
        tap_distance = dp(10)

        if (
            started
            and started[0] == id(self)
            and self.collide_point(*touch.pos)
            and abs(touch.pos[0] - started[1][0]) < tap_distance
            and abs(touch.pos[1] - started[1][1]) < tap_distance
            and self.day is not None
            and self.screen is not None
        ):
            self.screen.show_day_details(self.day)

        return super().on_touch_up(touch)


class MonthlyAttendanceScreen(MDScreen):
    subject_id = None
    month = None
    year = None
    _overlay = None

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
        """Show a dialog listing every record for the tapped day."""

        day_date = datetime(self.year, self.month, day)
        date_string = day_date.strftime(DATE_FORMAT)

        day_records = [
            record
            for record in get_attendance_for_subject(self.subject_id)
            if record["date"] == date_string
        ]
        day_records.sort(key=lambda record: record["time"])

        # Only one dialog at a time
        self.close_day_details()

        # Full-screen layer that also dims the calendar behind the dialog
        overlay = CalendarOverlay(size_hint=(1, 1))
        self._overlay = overlay

        with overlay.canvas.before:
            Color(0, 0, 0, 0.45)
            dim = Rectangle(pos=overlay.pos, size=overlay.size)

        overlay.bind(
            pos=lambda widget, value: setattr(dim, "pos", value),
            size=lambda widget, value: setattr(dim, "size", value),
        )

        # The dialog: title + scrollable records + CLOSE, all in ONE card,
        # so nothing can overlap (the old CLOSE button floated on top of
        # the last record).
        dialog_card = MDCard(
            orientation="vertical",
            size_hint=(0.85, None),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            padding=dp(15),
            spacing=dp(10),
            elevation=8,
            radius=[dp(12)],
        )

        # Card grows with the number of records, up to 80% of the screen.
        row_height = dp(55)
        row_spacing = dp(8)
        rows = max(len(day_records), 1)
        wanted_height = (
            dp(15) * 2          # card padding
            + dp(40)            # title
            + dp(40)            # CLOSE button
            + dp(10) * 2        # spacing between the three parts
            + rows * (row_height + row_spacing)
        )

        def fit_height(*args):
            dialog_card.height = min(wanted_height, overlay.height * 0.8)

        overlay.bind(height=fit_height)
        fit_height()

        # Title
        dialog_card.add_widget(
            MDLabel(
                text=day_date.strftime("%B %d, %Y"),
                halign="center",
                font_size="20sp",
                bold=True,
                size_hint_y=None,
                height=dp(40),
            )
        )

        # Scrollable list of records (takes all the remaining space)
        records_box = MDBoxLayout(
            orientation="vertical",
            spacing=row_spacing,
            adaptive_height=True,
        )

        if not day_records:
            records_box.add_widget(
                MDLabel(
                    text="No attendance recorded for this day.",
                    halign="center",
                    adaptive_height=True,
                )
            )

        for record in day_records:
            if record["status"] == "Present":
                status_color = (0.2, 0.7, 0.3, 1)
            else:
                status_color = (0.9, 0.2, 0.2, 1)

            row = MDCard(
                orientation="horizontal",
                size_hint_y=None,
                height=row_height,
                padding=dp(10),
                elevation=1,
                radius=[dp(8)],
            )

            row.add_widget(
                MDLabel(
                    text=display_time(record["time"]),
                    halign="left",
                    font_size="16sp",
                )
            )

            row.add_widget(
                MDLabel(
                    text=record["status"],
                    halign="right",
                    font_size="16sp",
                    bold=True,
                    theme_text_color="Custom",
                    text_color=status_color,
                )
            )

            records_box.add_widget(row)

        scroll = ScrollView(size_hint=(1, 1))
        scroll.add_widget(records_box)
        dialog_card.add_widget(scroll)

        # CLOSE button, inside the card, below the list
        close_button = MDButton(
            style="filled",
            pos_hint={"center_x": 0.5},
        )
        close_button.add_widget(MDButtonText(text="Close"))
        close_button.bind(on_release=lambda instance: self.close_day_details())
        dialog_card.add_widget(close_button)

        overlay.add_widget(dialog_card)
        self.add_widget(overlay)

    def close_day_details(self):
        """Remove the day dialog if one is open."""
        overlay = getattr(self, "_overlay", None)

        if overlay is not None and overlay.parent is not None:
            self.remove_widget(overlay)

        self._overlay = None

    def on_leave(self, *args):
        """Don't leave a stale dialog behind when navigating away."""
        self.close_day_details()

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