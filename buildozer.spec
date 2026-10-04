[app]

title = Attendance Tracker
package.name = attendancetracker
package.domain = org.attendancetracker

# main.py must be in this folder (it is, at the project root)
source.dir = .
source.include_exts = py,kv,png,jpg,json
# Keep tests, build output and your personal database OUT of the APK
source.exclude_dirs = tests, data, bin, .buildozer, .github, venv, .venv, __pycache__
source.exclude_patterns = *.db, test.py

version = 0.1

# sqlite3 is required because the app uses a database.
# The last four are the extra libraries KivyMD 2.x needs on Android.
requirements = python3,kivy==2.3.0,kivymd==2.0.0,sqlite3,pillow,materialyoucolor,exceptiongroup,asyncgui,asynckivy

orientation = portrait
fullscreen = 0

# No permissions needed: the database is kept in the app's private storage.
android.accept_sdk_license = True
# 64-bit only: all modern phones. Halves build time/memory/disk use.
android.archs = arm64-v8a

[buildozer]

log_level = 2
warn_on_root = 1
