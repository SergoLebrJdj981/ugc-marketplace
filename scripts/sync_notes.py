#!/usr/bin/env python3
import datetime
import os

BASE_DIR = os.path.join("notes", "note")
FILES = ["project_plan.md", "tasks.md", "changelog.md", "readme.md"]

print("🔄 Сверка consistency между notes...")
timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

report_lines = []
for filename in FILES:
    path = os.path.join(BASE_DIR, filename)
    if os.path.exists(path):
        size = os.path.getsize(path)
        mtime = datetime.datetime.fromtimestamp(os.path.getmtime(path))
        report_lines.append(f"✅ {filename} — {size} байт, обновлён {mtime}")
    else:
        report_lines.append(f"❌ {filename} — отсутствует")

report_path = os.path.join(BASE_DIR, "revision_report.txt")
with open(report_path, "w", encoding="utf-8") as report_file:
    report_file.write(f"📘 Ревизионный отчёт — {timestamp}\n\n")
    for line in report_lines:
        report_file.write(line + "\n")

print("\n".join(report_lines))
print("\n📄 Отчёт сохранён в notes/note/revision_report.txt")
