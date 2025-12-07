import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sangabiz.settings')
django.setup()

print("=== EXACT INSTALLED_APPS CONTENT ===")
print("Raw INSTALLED_APPS list:")
for i, app in enumerate(settings.INSTALLED_APPS, 1):
    print(f"  {i:2d}. '{app}'")

print(f"\nChecking for 'artists' with exact string match...")
print(f"'artists' in INSTALLED_APPS: {'artists' in settings.INSTALLED_APPS}")

# Check for any similar names
similar = [app for app in settings.INSTALLED_APPS if 'artist' in app.lower()]
print(f"Similar names found: {similar}")

# Check each custom app
print(f"\nCustom apps analysis:")
custom_apps = [app for app in settings.INSTALLED_APPS if not app.startswith('django.')]
for app in custom_apps:
    print(f"  - '{app}'")
