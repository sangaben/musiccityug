import os
import django

print("=== ACTUAL SETTINGS BEING USED ===")
print(f"Current directory: {os.getcwd()}")
print(f"DJANGO_SETTINGS_MODULE: {os.environ.get('DJANGO_SETTINGS_MODULE', 'Not set')}")

# Try to setup and see what happens
try:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sangabiz.settings')
    django.setup()
    
    from django.conf import settings
    print(f"Settings module: {settings.SETTINGS_MODULE}")
    print(f"BASE_DIR: {settings.BASE_DIR}")
    
    print(f"\nACTUAL INSTALLED_APPS:")
    for app in settings.INSTALLED_APPS:
        if not app.startswith('django.'):
            print(f"  - {app}")
            
    # Check for our apps
    our_apps = ['accounts', 'music', 'artists', 'analytics', 'payments', 'library']
    print(f"\nOUR APPS STATUS:")
    for app in our_apps:
        if app in settings.INSTALLED_APPS:
            print(f"  ✅ {app}")
        else:
            print(f"  ❌ {app}")
            
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
