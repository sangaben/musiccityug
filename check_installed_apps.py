import os
import sys
import django
from django.conf import settings

print("=== DEBUGGING INSTALLED_APPS ===")

# Check current working directory
print(f"Current directory: {os.getcwd()}")

# Check if we're using the right settings
print(f"DJANGO_SETTINGS_MODULE: {os.environ.get('DJANGO_SETTINGS_MODULE', 'Not set')}")

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sangabiz.settings')
try:
    django.setup()
    print("✅ Django setup successful")
    
    # Print ALL installed apps
    print("\n📋 ALL INSTALLED_APPS:")
    for i, app in enumerate(settings.INSTALLED_APPS, 1):
        print(f"  {i:2d}. {app}")
    
    # Check specifically for library
    print(f"\n🔍 Is 'library' in INSTALLED_APPS?")
    if 'library' in settings.INSTALLED_APPS:
        print("✅ YES - 'library' is in INSTALLED_APPS")
    else:
        print("❌ NO - 'library' is NOT in INSTALLED_APPS")
        print("Looking for similar names...")
        similar = [app for app in settings.INSTALLED_APPS if 'lib' in app.lower()]
        if similar:
            print(f"Found similar: {similar}")
    
    # Try to get the library app config
    try:
        from django.apps import apps
        library_config = apps.get_app_config('library')
        print(f"✅ Library app config found: {library_config}")
    except Exception as e:
        print(f"❌ Could not get library app config: {e}")
        
except Exception as e:
    print(f"❌ Django setup failed: {e}")
    import traceback
    traceback.print_exc()
