from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('doctor', 'Doctor'),
        ('lab', 'Lab Technician'),
        ('admin', 'Admin'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    specialization = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.role}"

class MedicalReport(models.Model):
    patient_name = models.CharField(max_length=100)
    patient_id = models.CharField(max_length=50, blank=True)
    doctor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, limit_choices_to={'userprofile__role': 'doctor'})
    image = models.ImageField(upload_to='scans/', blank=True, null=True)
    pdf_report = models.FileField(upload_to='reports/', blank=True, null=True)
    prediction = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report - {self.patient_name} - {self.created_at.strftime('%Y-%m-%d')}"
