# Attendance Tracker

A Python attendance tracker for Android/desktop, built with Kivy and KivyMD 2.x.

## Features
- Add subjects (name, code, professor)
- Mark / edit / delete attendance (date, time, Present/Absent)
- Overall and per-subject attendance percentage with a 75% target
- Shows how many classes you must attend to recover, or can still miss
- Monthly calendar view

## Run on desktop
```bash
pip install -r requirements.txt
python main.py
```

## Notes
- Dates are stored as `YYYY-MM-DD`, times as 24-hour `HH:MM`
  (you can type `14:30` or `02:30 PM`).
- Change the target percentage in `app/config.py`.
- On Android the database is stored in the app's private storage.

## Tests
```bash
pip install pytest
pytest
```

## Build the Android APK
**Easiest (no setup):** push this repo to GitHub, open the **Actions** tab,
choose **Build Android APK**, click **Run workflow**, and download the
`attendance-tracker-apk` artifact when it finishes (first build ~20-40 min).

**Locally:** on Linux or Windows WSL2 (Ubuntu), install Buildozer and run
`buildozer -v android debug`; the APK appears in `bin/`.
