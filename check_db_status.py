import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'retinal_project.settings')
django.setup()

from retina_app.models import MedicalReport

count = MedicalReport.objects.count()
print(f"MedicalReport Count: {count}")

media_scans = os.path.join(django.conf.settings.MEDIA_ROOT, 'scans')
media_reports = os.path.join(django.conf.settings.MEDIA_ROOT, 'reports')

scan_files = os.listdir(media_scans) if os.path.exists(media_scans) else []
report_files = os.listdir(media_reports) if os.path.exists(media_reports) else []

print(f"Scan Files: {len(scan_files)}")
print(f"Report Files: {len(report_files)}")
