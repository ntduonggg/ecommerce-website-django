import os
import sys
import django

# Setup Django
sys.path.append('/var/app/current')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webapp.settings')
django.setup()

from django.conf import settings

print("=" * 50)
print("S3 Configuration Test")
print("=" * 50)
print(f"AWS_STORAGE_BUCKET_NAME: {settings.AWS_STORAGE_BUCKET_NAME}")
print(f"AWS_S3_REGION_NAME: {settings.AWS_S3_REGION_NAME}")
print(f"STATIC_URL: {settings.STATIC_URL}")
print(f"MEDIA_URL: {settings.MEDIA_URL}")
print(f"\nSTORAGES:")
for key, value in settings.STORAGES.items():
    print(f"  {key}: {value['BACKEND']}")
print("=" * 50)