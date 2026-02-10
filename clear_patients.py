import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'retinal_project.settings')
django.setup()

from retina_app.models import MedicalReport
from django.conf import settings

def clear_patients():
    print("--- Clearing Patient Details ---")
    
    # Delete Medical Reports
    reports_count = MedicalReport.objects.count()
    MedicalReport.objects.all().delete()
    print(f"Deleted {reports_count} Medical Reports.")
    
    # Clear Media Files (scans and reports are patient data)
    media_root = settings.MEDIA_ROOT
    if os.path.exists(media_root):
        print("\n--- Clearing Patient Media Files ---")
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
        print("Patient media files cleared.")
    
    print("\nPatient details cleared successfully.")

if __name__ == "__main__":
    clear_patients()
