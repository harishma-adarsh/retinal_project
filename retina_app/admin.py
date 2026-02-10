from django.contrib import admin
from .models import UserProfile, MedicalReport

admin.site.register(UserProfile)
admin.site.register(MedicalReport)
