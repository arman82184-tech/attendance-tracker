from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager

from kivymd.app import MDApp

from app.database.database import initialize_database

from app.screens.home_screen import HomeScreen
from app.screens.add_subject_screen import AddSubjectScreen
from app.screens.subject_details_screen import SubjectDetailsScreen
from app.screens.mark_attendance_screen import MarkAttendanceScreen
from app.screens.edit_attendance_screen import EditAttendanceScreen
from app.screens.monthly_attendance_screen import MonthlyAttendanceScreen


class AttendanceTrackerApp(MDApp):

    def build(self):

        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Blue"

        initialize_database()

        Builder.load_file("app/ui.kv")

        screen_manager = ScreenManager()

        screen_manager.add_widget(
            HomeScreen(name="home")
        )

        screen_manager.add_widget(
            AddSubjectScreen(name="add_subject")
        )

        screen_manager.add_widget(
            SubjectDetailsScreen(name="subject_details")
        )

        screen_manager.add_widget(
            MarkAttendanceScreen(name="mark_attendance")
        )

        screen_manager.add_widget(
            EditAttendanceScreen(name="edit_attendance")
        )

        screen_manager.add_widget(
            MonthlyAttendanceScreen(
                name="monthly_attendance"
            )
        )        

        return screen_manager


if __name__ == "__main__":
    AttendanceTrackerApp().run()