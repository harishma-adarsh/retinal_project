import os
import django
import sys

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'retinal_project.settings')
django.setup()

from django.contrib.auth.models import User
from retina_app.models import UserProfile, MedicalReport

def seed_data():
    print("--- Clearing Database ---")
    MedicalReport.objects.all().delete()
    UserProfile.objects.all().delete()
    # Delete all users to ensure a fresh start with requested credentials
    User.objects.all().delete() 
    print("Database cleared.")

    print("--- Creating Users ---")
    
    # Admin
    admin_email = 'admin@eye4heart.ai'
    admin = User.objects.create_superuser(admin_email, admin_email, 'demo123')
    UserProfile.objects.create(user=admin, role='admin')
    print(f"Created Admin: {admin_email}")
    
    # Doctor
    dr_email = 'dr@demo.health'
    dr = User.objects.create_user(dr_email, dr_email, 'demo123', first_name='Aarav', last_name='Patel')
    UserProfile.objects.create(user=dr, role='doctor', specialization='Retina Specialist')
    print(f"Created Doctor: {dr_email}")

    # Lab Tech
    lab_email = 'lab@demo.health'
    lab = User.objects.create_user(lab_email, lab_email, 'demo123', first_name='Lab', last_name='Technician')
    UserProfile.objects.create(user=lab, role='lab')
    print(f"Created Lab: {lab_email}")

    print("--- Seed Complete ---")

if __name__ == "__main__":
    seed_data()
