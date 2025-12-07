import os
import sys
import django
from django.conf import settings

print("=== COMPLETE ARTISTS APP DEBUG ===")

# Check current directory and Python path
print(f"Current directory: {os.getcwd()}")
print(f"Python path: {sys.path}")

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sangabiz.settings')
try:
    django.setup()
    print("✅ Django setup successful")
    
    # Check INSTALLED_APPS
    print(f"\n📋 INSTALLED_APPS:")
    custom_apps = [app for app in settings.INSTALLED_APPS if not app.startswith('django.')]
    for i, app in enumerate(custom_apps, 1):
        print(f"  {i:2d}. {app}")
    
    # Check if 'artists' is in INSTALLED_APPS
    print(f"\n🔍 Is 'artists' in INSTALLED_APPS? {'artists' in settings.INSTALLED_APPS}")
    
    # Try to get artists app config
    from django.apps import apps
    try:
        artists_config = apps.get_app_config('artists')
        print(f"✅ Artists app config found: {artists_config}")
        print(f"   Path: {artists_config.path}")
        print(f"   Models: {[model.__name__ for model in artists_config.get_models()]}")
    except LookupError as e:
        print(f"❌ Artists app config not found: {e}")
    
    # Check artists directory structure
    artists_path = os.path.join(os.getcwd(), 'artists')
    print(f"\n📁 Artists directory: {artists_path}")
    print(f"   Exists: {os.path.exists(artists_path)}")
    if os.path.exists(artists_path):
        print("   Contents:")
        for item in os.listdir(artists_path):
            item_path = os.path.join(artists_path, item)
            print(f"     - {item} (file: {os.path.isfile(item_path)})")
    
    # Try to import Artist model directly
    print(f"\n🔄 Testing Artist model import...")
    try:
        from artists.models import Artist
        print("✅ Successfully imported Artist model")
        print(f"   Artist._meta.app_label: {Artist._meta.app_label}")
    except ImportError as e:
        print(f"❌ Failed to import Artist: {e}")
        import traceback
        traceback.print_exc()
        
except Exception as e:
    print(f"❌ Django setup failed: {e}")
    import traceback
    traceback.print_exc()
