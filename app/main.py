from pathlib import Path

from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager
from kivy.utils import platform

from kivymd.app import MDApp

from app.database.database import configure_database, initialize_database

from app.screens.home_screen import HomeScreen
from app.screens.add_subject_screen import AddSubjectScreen
from app.screens.subject_details_screen import SubjectDetailsScreen
from app.screens.mark_attendance_screen import MarkAttendanceScreen
from app.screens.edit_attendance_screen import EditAttendanceScreen
from app.screens.monthly_attendance_screen import MonthlyAttendanceScreen


# Always resolve ui.kv relative to this file, not the current folder.
KV_FILE = Path(__file__).resolve().parent / "ui.kv"


class AttendanceTrackerApp(MDApp):

    def build(self):

        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Blue"

        if platform == "android":
            # Keep the database in the app's private storage.
            configure_database(Path(self.user_data_dir) / "attendance.db")

            # Slide the screen up so the keyboard doesn't hide the text field.
            Window.softinput_mode = "below_target"

        # Back button (Android) / Esc key (desktop)
        Window.bind(on_keyboard=self.on_back_key)

        initialize_database()

        Builder.load_file(str(KV_FILE))

        screen_manager = ScreenManager()

        screen_manager.add_widget(HomeScreen(name="home"))
        screen_manager.add_widget(AddSubjectScreen(name="add_subject"))
        screen_manager.add_widget(SubjectDetailsScreen(name="subject_details"))
        screen_manager.add_widget(MarkAttendanceScreen(name="mark_attendance"))
        screen_manager.add_widget(EditAttendanceScreen(name="edit_attendance"))
        screen_manager.add_widget(
            MonthlyAttendanceScreen(name="monthly_attendance")
        )

        return screen_manager

    def on_back_key(self, window, key, *args):
        """Go back one screen instead of closing the whole app."""

        if key != 27:               # 27 = Android back button / Esc
            return False

        if self.root.current == "home":
            return False            # on the home screen: normal exit

        screen = self.root.current_screen

        # Close the calendar day-dialog first, if it is open
        if (
            self.root.current == "monthly_attendance"
            and screen._overlay is not None
        ):
            screen.close_day_details()
            return True

        screen.go_back()
        return True


if __name__ == "__main__":
    AttendanceTrackerApp().run()
