import os
import sys
import django
from django.conf import settings

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mypage.settings')

try:
    django.setup()
except Exception as e:
    print(f"CRITICAL: Django setup failed: {e}")
    sys.exit(1)

print("\n--- Diagnostic Report ---")
print(f"Django Version: {django.get_version()}")
print(f"DEBUG mode: {settings.DEBUG}")

try:
    import cloudinary
    print(f"Cloudinary module imported successfully.")
except ImportError:
    print("CRITICAL: Cloudinary library not found.")

print("\n--- Storage Configuration ---")
try:
    storages = settings.STORAGES
    print(f"STORAGES setting: {storages}")
    default_backend = storages.get('default', {}).get('BACKEND')
    print(f"Default Storage Backend: {default_backend}")
except AttributeError:
    print("STORAGES setting not found (older Django version? Or variable missing)")

print("\n--- Cloudinary Configuration ---")
c_storage = getattr(settings, 'CLOUDINARY_STORAGE', None)
if c_storage:
    print("CLOUDINARY_STORAGE is set.")
    # Print masked credentials
    cn = c_storage.get('CLOUD_NAME')
    key = c_storage.get('API_KEY')
    secret = c_storage.get('API_SECRET')
    
    print(f"  CLOUD_NAME: {cn if cn else 'MISSING'}")
    print(f"  API_KEY: {'*' * 4 + key[-4:] if key and len(key) > 4 else 'MISSING/SHORT'}")
    print(f"  API_SECRET: {'*' * 4 + secret[-4:] if secret and len(secret) > 4 else 'MISSING/SHORT'}")
else:
    print("CRITICAL: CLOUDINARY_STORAGE setting is MISSING.")

print("\n--- Environment Variables ---")
print(f"CLOUDINARY_URL present: {'Yes' if os.environ.get('CLOUDINARY_URL') else 'No'}")
print(f"DATABASE_URL present: {'Yes' if os.environ.get('DATABASE_URL') else 'No'}")

print("\n--- Connectivity Test ---")
if c_storage and c_storage.get('CLOUD_NAME') and c_storage.get('API_KEY') and c_storage.get('API_SECRET'):
    try:
        from cloudinary.uploader import upload
        from io import BytesIO
        
        # Create a tiny in-memory image
        img_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
        
        print("Attempting to upload a test image to Cloudinary...")
        response = upload(BytesIO(img_data), public_id="diagnostic_test_image", folder="diagnostics")
        print("SUCCESS! Upload successful.")
        print(f"Image URL: {response.get('secure_url')}")
    except Exception as e:
        print(f"FAIL: Upload failed. Error: {e}")
else:
    print("SKIP: Cannot test upload due to missing credentials.")

print("\n--- End Report ---")
