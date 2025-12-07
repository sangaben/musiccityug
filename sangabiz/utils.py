# sangabiz/utils.py
import os
from django.conf import settings    
DEBUG = settings.DEBUG
def environment_callback(request):
    return {
        "BUILD_ID": os.getenv("BUILD_ID", "local"),
        "APP_VERSION": "1.0.0",
        "ENVIRONMENT": "Development" if DEBUG else "Production",
    }