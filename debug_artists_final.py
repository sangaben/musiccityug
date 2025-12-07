import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sangabiz.settings')

print("=== FINAL ARTISTS DEBUG ===")

# Check INSTALLED_APPS
print("INSTALLED_APPS:")
for app in settings.INSTALLED_APPS:
    if not app.startswith('django.'):
        print(f"  - {app}")

print(f"\n'artists' in INSTALLED_APPS: {'artists' in settings.INSTALLED_APPS}")

# Try to setup Django
try:
    django.setup()
    print("✅ Django setup successful")
    
    # Check app registry
    from django.apps import apps
    try:
        artists_config = apps.get_app_config('artists')
        print("✅ Artists app found in registry!")
    except LookupError:
        print("❌ Artists app NOT in registry!")
        
    # Try to import Artist model
    try:
        from artists.models import Artist
        print("✅ Artist model imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import Artist: {e}")
        
except Exception as e:
    print(f"❌ Django setup failed: {e}")
    import traceback
    traceback.print_exc()
