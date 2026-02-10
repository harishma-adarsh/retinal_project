import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'retinal_project.settings')
django.setup()

from django.contrib.auth.models import User
from retina_app.models import UserProfile

print("--- Data Check ---")
for u in User.objects.all():
    try:
        up = u.userprofile
        print(f"User: {u.username}, Role: {up.role}, First: {u.first_name}, Last: {u.last_name}")
    except UserProfile.DoesNotExist:
        print(f"User: {u.username}, Role: NO PROFILE")
print("--- End Check ---")
