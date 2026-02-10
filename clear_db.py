import os
import django
import sys

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'retinal_project.settings')
django.setup()

from django.contrib.auth.models import User
from retina_app.models import UserProfile, MedicalReport
from django.conf import settings
import shutil

def clear_data():
    print("--- Clearing Database ---")
    
    # Delete Medical Reports
    reports_count = MedicalReport.objects.count()
    MedicalReport.objects.all().delete()
    print(f"Deleted {reports_count} Medical Reports.")
    
    # Delete User Profiles
    profiles_count = UserProfile.objects.count()
    UserProfile.objects.all().delete()
    print(f"Deleted {profiles_count} User Profiles.")
    
    # Delete Users (excluding superusers)
    users_count = User.objects.exclude(is_superuser=True).count()
    User.objects.exclude(is_superuser=True).delete()
    print(f"Deleted {users_count} Users (excluding superusers).")
    
    # Clear Media Files
    media_root = settings.MEDIA_ROOT
    if os.path.exists(media_root):
        print("\n--- Clearing Media Files ---")
        for folder in ['scans', 'reports']:
            folder_path = os.path.join(media_root, folder)
            if os.path.exists(folder_path):
                files = os.listdir(folder_path)
                for f in files:
                    file_path = os.path.join(folder_path, f)
                    try:
                        if os.path.isfile(file_path):
                            os.unlink(file_path)
                            print(f"Deleted file: {f}")
                    except Exception as e:
                        print(f"Error deleting {file_path}: {e}")
        print("Media files cleared.")
    
    print("\nDatabase and media values cleared successfully.")

if __name__ == "__main__":
    clear_data()
