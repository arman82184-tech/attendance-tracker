import sqlite3

from kivymd.uix.screen import MDScreen

from app.services.subject_service import add_subject


class AddSubjectScreen(MDScreen):

    def on_pre_enter(self):
        """Start with a clean error message each time."""
        self.ids.error_label.text = ""

    def save_subject(self):
        """Save the entered subject to the database."""

        subject_name = self.ids.subject_name.text.strip()
        subject_code = self.ids.subject_code.text.strip()
        professor_name = self.ids.professor_name.text.strip()

        # Check for empty fields
        if not subject_name or not subject_code or not professor_name:
            self.ids.error_label.text = "Please fill in all fields."
            return

        try:
            add_subject(subject_name, subject_code, professor_name)

        except sqlite3.IntegrityError:
            # subject_code is UNIQUE
            self.ids.error_label.text = "Subject code already exists."
            return

        except sqlite3.Error as error:
            # Any other database problem: don't mislabel it as a duplicate
            self.ids.error_label.text = "Could not save the subject."
            print("Error adding subject:", error)
            return

        # Clear fields
        self.ids.subject_name.text = ""
        self.ids.subject_code.text = ""
        self.ids.professor_name.text = ""
        self.ids.error_label.text = ""

        # Go back to home screen
        self.manager.current = "home"

    def go_back(self):
        """Return to the home screen."""

        self.manager.current = "home"
