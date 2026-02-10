import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'retinal_project.settings')
django.setup()

from django.contrib.auth.models import User
from retina_app.models import UserProfile

def setup_user(username, email, password, role):
    user, created = User.objects.get_or_create(username=username, defaults={'email': email})
    user.set_password(password)
    user.save()
    
    profile, p_created = UserProfile.objects.get_or_create(user=user, defaults={'role': role})
    if not p_created and profile.role != role:
        profile.role = role
        profile.save()
        
    status = "Created" if created else "Updated password for"
    print(f"{status} {role}: {username}")

if __name__ == "__main__":
    setup_user('dr@demo.health', 'dr@demo.health', 'demo123', 'doctor')
    setup_user('lab@demo.health', 'lab@demo.health', 'demo123', 'lab')
    setup_user('admin@eye4heart.ai', 'admin@eye4heart.ai', 'demo123', 'admin')
