import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'retinal_project.settings')
django.setup()

from django.contrib.auth.models import User
from retina_app.models import UserProfile

def create_user(username, email, password, role):
    if not User.objects.filter(username=username).exists():
        user = User.objects.create_user(username=username, email=email, password=password)
        UserProfile.objects.create(user=user, role=role)
        print(f"Created {role} user: {username}")
    else:
        print(f"User {username} already exists")

if __name__ == "__main__":
    create_user('dr@demo.health', 'dr@demo.health', 'demo123', 'doctor')
    create_user('lab@demo.health', 'lab@demo.health', 'demo123', 'lab')
    create_user('admin@eye4heart.ai', 'admin@eye4heart.ai', 'demo123', 'admin')
