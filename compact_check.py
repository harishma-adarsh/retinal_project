import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'retinal_project.settings')
django.setup()

from django.contrib.auth.models import User
from retina_app.models import UserProfile

print("START")
for u in User.objects.all():
    role = "NONE"
    try:
        role = u.userprofile.role
    except:
        pass
    print(f"{u.username}|{role}|{u.first_name}|{u.last_name}")
print("END")
