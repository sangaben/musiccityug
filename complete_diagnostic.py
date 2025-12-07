import os
import sys
import django
from django.conf import settings

print("=== COMPLETE DJANGO DIAGNOSTIC ===")

# Basic system info
print(f"Python: {sys.version}")
print(f"Current dir: {os.getcwd()}")
print(f"DJANGO_SETTINGS_MODULE: {os.environ.get('DJANGO_SETTINGS_MODULE', 'Not set')}")

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sangabiz.settings')
try:
    django.setup()
    print("✅ Django setup successful")
    
    # Check ALL installed apps
    print(f"\n📋 ALL INSTALLED_APPS:")
    for i, app in enumerate(settings.INSTALLED_APPS, 1):
        print(f"  {i:2d}. {app}")
    
    # Check custom apps specifically
    custom_apps = [app for app in settings.INSTALLED_APPS if not app.startswith('django.')]
    print(f"\n🎯 CUSTOM APPS: {custom_apps}")
    print(f"   'artists' in INSTALLED_APPS: {'artists' in settings.INSTALLED_APPS}")
    
    # Check app registry
    from django.apps import apps
    print(f"\n🔍 APP REGISTRY:")
    for app_config in apps.get_app_configs():
        print(f"  - {app_config.name}: {app_config.path}")
    
    # Specifically check artists
    try:
        artists_config = apps.get_app_config('artists')
        print(f"✅ Artists app found in registry!")
        print(f"   Models: {[m.__name__ for m in artists_config.get_models()]}")
    except LookupError:
        print(f"❌ Artists app NOT in app registry!")
    
    # Check file structure
    print(f"\n📁 FILE STRUCTURE:")
    for app in ['accounts', 'music', 'artists', 'library', 'payments', 'analytics']:
        app_path = os.path.join(os.getcwd(), app)
        if os.path.exists(app_path):
            files = [f for f in os.listdir(app_path) if f.endswith('.py')]
            print(f"  {app}: {files}")
        else:
            print(f"  {app}: ❌ DIRECTORY MISSING")
            
except Exception as e:
    print(f"❌ Django setup failed: {e}")
    import traceback
    traceback.print_exc()
