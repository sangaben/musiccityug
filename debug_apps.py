import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sangabiz.settings')
try:
    django.setup()
    print("✅ Django setup successful!")
    print("\n📋 INSTALLED_APPS:")
    for app in settings.INSTALLED_APPS:
        print(f"  - {app}")
    
    print("\n🔍 Checking if 'library' is in INSTALLED_APPS:")
    if 'library' in settings.INSTALLED_APPS:
        print("✅ 'library' is in INSTALLED_APPS")
    else:
        print("❌ 'library' is NOT in INSTALLED_APPS")
        
except Exception as e:
    print(f"❌ Error: {e}")
