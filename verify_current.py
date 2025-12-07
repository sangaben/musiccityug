import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sangabiz.settings')

from django.conf import settings
print("=== CURRENT INSTALLED_APPS ===")
required_apps = ['accounts', 'music', 'artists', 'analytics', 'payments', 'library']
for app in required_apps:
    status = "✅ PRESENT" if app in settings.INSTALLED_APPS else "❌ MISSING"
    print(f"{app}: {status}")
