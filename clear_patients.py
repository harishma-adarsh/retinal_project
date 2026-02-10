"""
Clear all patient data from the database
Run with: python clear_patients.py
"""
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'retinal_project.settings')
django.setup()

from retina_app.models import MedicalReport
import shutil

def clear_all_patients():
    """Clear all medical reports and their associated files"""
    
    print("\n" + "="*60)
    print("CLEARING ALL PATIENT DATA")
    print("="*60)
    
    # Get count before deletion
    total_reports = MedicalReport.objects.count()
    
    if total_reports == 0:
        print("\nNo patient data found. Database is already empty.")
        return
    
    print(f"\nFound {total_reports} patient records")
    
    # Confirm deletion
    response = input(f"\nAre you sure you want to delete ALL {total_reports} patient records? (yes/no): ")
    
    if response.lower() != 'yes':
        print("\nCancelled. No data was deleted.")
        return
    
    print("\nDeleting patient records...")
    
    # Delete all medical reports (Django will handle file deletion if configured)
    deleted_count = MedicalReport.objects.all().delete()[0]
    
    print(f"✓ Deleted {deleted_count} patient records from database")
    
    # Clean up media files
    media_dirs = [
        'media/retinal_scans',
        'media/pdf_reports', 
        'media/reports'
    ]
    
    for dir_path in media_dirs:
        if os.path.exists(dir_path):
            try:
                # Remove all files in directory but keep the directory
                for filename in os.listdir(dir_path):
                    file_path = os.path.join(dir_path, filename)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                print(f"✓ Cleaned files from {dir_path}")
            except Exception as e:
                print(f"⚠ Warning: Could not clean {dir_path}: {e}")
    
    print("\n" + "="*60)
    print("DATABASE CLEARED SUCCESSFULLY")
    print("="*60)
    print("\n✓ All patient data has been removed")
    print("✓ Medical report files have been deleted")
    print("✓ Database is now empty and ready for new data\n")

if __name__ == "__main__":
    clear_all_patients()
