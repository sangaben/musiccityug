import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sangabiz.settings')
django.setup()

print("=== Checking artists app ===")

# Check if artists is in INSTALLED_APPS
print(f"Is 'artists' in INSTALLED_APPS? {'artists' in settings.INSTALLED_APPS}")

# Check all installed apps
print("\nAll custom apps in INSTALLED_APPS:")
for app in settings.INSTALLED_APPS:
    if not app.startswith('django.'):
        print(f"  - {app}")

# Try to import Artist model
try:
    from artists.models import Artist
    print("✅ Successfully imported Artist model")
except ImportError as e:
    print(f"❌ Failed to import Artist: {e}")

# Check artists app structure
import os
artists_path = os.path.join(os.getcwd(), 'artists')
print(f"\nArtists app path: {artists_path}")
print(f"Artists directory exists: {os.path.exists(artists_path)}")
if os.path.exists(artists_path):
    print("Artists directory contents:")
    for item in os.listdir(artists_path):
        print(f"  - {item}")
