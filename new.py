import os
import django
from django.core.management import call_command

# 1️⃣ Set settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
# ⚠️ Tumhare project structure me core + data apps hain, toh settings.py ka path ye hi hoga
# Agar settings.py kisi subfolder me hai, waha ka Python path use karo.

# 2️⃣ Setup Django
django.setup()

# 3️⃣ Dump data to UTF-8
with open("data.json", "w", encoding="utf-8") as f:
    call_command(
        "dumpdata",
        "--natural-foreign",
        "--natural-primary",
        "-e", "contenttypes",
        "-e", "auth.Permission",
        stdout=f,
        verbosity=2
    )

print("✅ Data exported to data.json with UTF-8 encoding")
