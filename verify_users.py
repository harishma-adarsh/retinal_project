import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'retinal_project.settings')
django.setup()

from django.contrib.auth.models import User
from retina_app.models import UserProfile

users_to_check = ['dr@demo.health', 'lab@demo.health', 'admin@eye4heart.ai']

for username in users_to_check:
    try:
        user = User.objects.get(username=username)
        profile = user.userprofile
        print(f"User: {user.username}, Email: {user.email}, Role: {profile.role}, Pwd_Check: {user.check_password('demo123')}")
    except User.DoesNotExist:
        print(f"User {username} NOT FOUND")
    except Exception as e:
        print(f"Error checking {username}: {e}")
