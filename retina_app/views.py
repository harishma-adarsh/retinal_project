import os
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import UserProfile, MedicalReport
from django.http import JsonResponse
from .ml_utils import predict_image
from .pdf_utils import generate_pdf_report
from django.core.files.base import ContentFile
from datetime import datetime
import json
from django.utils.timesince import timesince
from django.utils import timezone
from datetime import timedelta

def index(request):
    return render(request, 'index.html')

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        # In this project, we use email as username
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            login(request, user)
            try:
                profile = user.userprofile
                if profile.role == 'doctor':
                    return redirect('doctor')
                elif profile.role == 'lab':
                    return redirect('lab')
                elif profile.role == 'admin':
                    return redirect('admin_panel')
            except UserProfile.DoesNotExist:
                # Fallback if no profile exists
                return redirect('index')
        else:
            messages.error(request, "Invalid email or password")
            
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def doctor_view(request):
    if request.user.userprofile.role != 'doctor':
        return redirect('index')
    
    # Fetch reports for this doctor (or all if simplified logic)
    reports = MedicalReport.objects.all().order_by('-created_at')
    
    # Serialize for JS
    patients_list = []
    for r in reports:
        # Determine status
        status = r.status

        # Standardize risk values
        r_label = "N/A"
        r_val = 0
        if r.prediction:
            if 'high' in r.prediction.lower():
                r_label = "High Risk"
                r_val = 88
            elif 'low' in r.prediction.lower():
                r_label = "Low Risk"
                r_val = 12

        patients_list.append({
            'name': r.patient_name,
            'id': r.patient_id,
            'status': status,
            'updated': f"{timesince(r.created_at)} ago",
            'risk': r_val,
            'risk_label': r_label,
            'pdf_url': r.pdf_report.url if r.pdf_report else ""
        })
    
    context = {
        'reports': reports,
        'patients': patients_list,
        'patient_count': reports.count(),
        'high_risk_count': reports.filter(prediction__icontains='high').count(),
        'completed_count': reports.filter(status='Completed').count(),
        'pending_count': reports.filter(status='In Progress').count() + reports.filter(status='Pending').count(),
    }
    return render(request, 'doctor.html', context)

@login_required
def lab_view(request):
    if request.user.userprofile.role != 'lab':
        return redirect('index')
    
    reports = MedicalReport.objects.all().order_by('-created_at')
    
    # Separate lists for 'Registry' (Pending) and 'Uploads' (Completed with image)
    # Using simple logic: if image is present, it's a "sync", else it's a "pending patient"
    
    patients_list = []
    uploads_list = []
    
    for r in reports:
        # Determine status
        status = r.status
        
        # Add to registry list
        doc_display = "Unassigned"
        if r.doctor:
            if r.doctor.first_name or r.doctor.last_name:
                doc_display = f"Dr. {r.doctor.first_name} {r.doctor.last_name}".strip()
            else:
                doc_display = r.doctor.username

        # Standardize risk values
        r_label = "Low Risk" # Default
        r_val = 12
        
        pred_clean = str(r.prediction or "").lower()
        if 'high' in pred_clean:
            r_label = "High Risk"
            r_val = 88
        elif 'low' in pred_clean:
            r_label = "Low Risk"
            r_val = 12
        else:
            r_label = "N/A"
            r_val = 0

        patients_list.append({
            'name': r.patient_name,
            'pid': r.patient_id,
            'doctor': doc_display,
            'doctor_username': r.doctor.username if r.doctor else "",
            'status': status,
            'risk': r_val,
            'risk_label': r_label,
            'pdf_url': r.pdf_report.url if r.pdf_report else "",
            'created': f"{timesince(r.created_at)} ago"
        })

        # Add to uploads list if it has an image
        if r.image:
             # Standardize risk values for display
             u_label = "N/A"
             u_risk_val = 0
             if r.prediction:
                 p_lower = r.prediction.lower()
                 if 'high' in p_lower:
                     u_label = "High Risk"
                     u_risk_val = 88
                 elif 'low' in p_lower:
                     u_label = "Low Risk"
                     u_risk_val = 12

             uploads_list.append({
                 'patient': r.patient_name,
                 'file': os.path.basename(r.image.name),
                 'type': 'Retina Scan',
                 'risk': u_risk_val,
                 'pdf_url': r.pdf_report.url if r.pdf_report else "",
                 'when': f"{timesince(r.created_at)} ago",
                 'prediction': u_label
             })
             
    # Fetch doctors
    doctor_users = User.objects.filter(userprofile__role='doctor')
    doctors_list = []
    for d in doctor_users:
        display_name = f"Dr. {d.first_name} {d.last_name}" if (d.first_name or d.last_name) else d.username
        doctors_list.append({
            'username': d.username,
            'display_name': display_name
        })
        
    context = {
        'patients': patients_list,
        'uploads': uploads_list,
        'doctors': doctors_list,
        'total_count': reports.count(),
        'pending_count': reports.filter(image='').count()
    }

    return render(request, 'lab.html', context)

@login_required
def admin_view(request):
    if request.user.userprofile.role != 'admin':
        return redirect('index')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add_user':
            name = request.POST.get('name')
            email = request.POST.get('email')
            password = request.POST.get('password')
            role = request.POST.get('role')
            specialization = request.POST.get('specialization')
            
            if User.objects.filter(username=email).exists():
                messages.error(request, f"User with email {email} already exists.")
            else:
                user = User.objects.create_user(username=email, email=email, password=password, first_name=name)
                UserProfile.objects.create(user=user, role=role, specialization=specialization)
                messages.success(request, f"Successfully added {role}: {name}")
                return redirect('admin_panel')
        
        elif action == 'onboard_patient':
            pname = request.POST.get('patient_name')
            pid = request.POST.get('patient_id')
            pdoc_username = request.POST.get('doctor_username')
            
            if pname and pid:
                # Only block if there is a completed report (with prediction) in the last 7 days
                one_week_ago = timezone.now() - timedelta(days=7)
                if MedicalReport.objects.filter(patient_id=pid, prediction__isnull=False, created_at__gte=one_week_ago).exists():
                    messages.error(request, f"Patient {pid} has a completed report within the last 7 days. Please wait 1 week.")
                    return redirect('admin_panel')

                report = MedicalReport(patient_name=pname, patient_id=pid)
                if pdoc_username:
                    try:
                        doc = User.objects.get(username=pdoc_username, userprofile__role='doctor')
                        report.doctor = doc
                    except User.DoesNotExist:
                        pass
                report.save()
                messages.success(request, f"Successfully onboarded patient: {pname}")
            else:
                messages.error(request, "Missing patient name or ID.")
            return redirect('admin_panel')

    # Get user lists
    doctors = User.objects.filter(userprofile__role='doctor')
    labs = User.objects.filter(userprofile__role='lab')
    
    # Fetch doctors for onboarding dropdown
    doctor_users = User.objects.filter(userprofile__role='doctor')
    doctors_list_dropdown = []
    for d in doctor_users:
        name = f"Dr. {d.first_name} {d.last_name}" if d.first_name else d.username
        doctors_list_dropdown.append({'username': d.username, 'display_name': name})

    context = {
        'doctors': doctors,
        'labs': labs,
        'doctor_count': doctors.count(),
        'lab_count': labs.count(),
        'total_users': User.objects.count(),
        'doctors_list_dropdown': doctors_list_dropdown,
        'total_reports': MedicalReport.objects.count(),
        'high_risk_percentage': round((MedicalReport.objects.filter(prediction__icontains='high').count() / MedicalReport.objects.count() * 100), 1) if MedicalReport.objects.exists() else 0
    }
    
    return render(request, 'admin.html', context)


@login_required
def analyze_image(request):
    if request.method == 'POST':
        try:
            image_file = request.FILES.get('image')
            pdf_file = request.FILES.get('pdf') # Accept manual PDF upload
            
            if not image_file and not pdf_file:
                 return JsonResponse({'status': 'error', 'message': 'No assets provided'}, status=400)

            patient_name = request.POST.get('patient_name', 'Unknown')
            patient_id = request.POST.get('patient_id', 'N/A')
            doctor_name = request.POST.get('doctor_name', 'Unassigned')

            # Check 7-day restriction ONLY for completed reports (those with a prediction)
            if patient_id and patient_id != 'N/A':
                one_week_ago = timezone.now() - timedelta(days=7)
                if MedicalReport.objects.filter(patient_id=patient_id, prediction__isnull=False, created_at__gte=one_week_ago).exists():
                     return JsonResponse({'status': 'error', 'message': f'Patient {patient_id} already has a completed report within the last 7 days. Please wait 1 week.'}, status=400)
            # 2. Find or Create Report (MANDATORY)
            report = None
            if patient_id and patient_id != 'N/A':
                report = MedicalReport.objects.filter(patient_id=patient_id, prediction__isnull=True).last()
            
            if not report:
                report = MedicalReport(patient_name=patient_name, patient_id=patient_id)
            else:
                # Update name if a new one was provided in the upload form
                report.patient_name = patient_name

            # 3. Process Assets
            # Image Analysis
            img_pred = "Low Risk"
            if image_file:
                report.image = image_file
                img_pred = predict_image(image_file)
            
            # PDF Analysis
            pdf_pred = None
            if pdf_file:
                report.pdf_report = pdf_file
                pdf_content = pdf_file.read().lower()
                pdf_file.seek(0)
                
                # Clinical Marker Logic
                h_clinical = [b"risk: high", b"high risk", b"positive result", b"finding: abnormal"]
                l_clinical = [b"risk: low", b"low risk", b"negative result", b"finding: normal", b"healthy", b"clear"]
                
                if any(m in pdf_content for m in h_clinical):
                    pdf_pred = "High Risk"
                elif any(m in pdf_content for m in l_clinical):
                    pdf_pred = "Low Risk"
                # No filename fallback - if no markers found, pdf_pred stays None

            # 4. FINAL DECISION - Trust Image Analysis First
            # Priority 1: Explicit PDF clinical markers (if present)
            # Priority 2: Image analysis (primary diagnostic tool)
            # Priority 3: Safe default
            
            if pdf_pred == "High Risk":
                # PDF explicitly says High Risk
                report.prediction = "High Risk"
            elif pdf_pred == "Low Risk":
                # PDF explicitly says Low Risk
                report.prediction = "Low Risk"
            elif img_pred:
                # Trust the image analysis
                report.prediction = img_pred
            else:
                # Safe default if nothing else available
                report.prediction = "Low Risk"

            report.status = "In Progress"

            # 5. Link Doctor
            if doctor_name:
                doc_user = User.objects.filter(username=doctor_name).first()
                if doc_user:
                    report.doctor = doc_user
            
            report.save()
            
            # Return full telemetry for instant UI sync
            numeric_val = 88 if 'high' in report.prediction.lower() else 12
            
            return JsonResponse({
                'status': 'success', 
                'prediction': report.prediction,
                'risk': numeric_val,
                'pdf_url': report.pdf_report.url if report.pdf_report else "",
                'message': 'Analysis completed and saved'
            })
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

@login_required
def add_patient(request):
    """
    Creates a new patient record (MedicalReport without image/prediction)
    so they appear in the Pending registry.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            patient_name = data.get('patient_name')
            patient_id = data.get('patient_id')
            doctor_name = data.get('doctor_name')
            
            # Simple validation
            if not patient_name or not patient_id:
                return JsonResponse({'status': 'error', 'message': 'Missing fields'}, status=400)

            # Only block if there is a completed report in the last 7 days
            one_week_ago = timezone.now() - timedelta(days=7)
            if MedicalReport.objects.filter(patient_id=patient_id, prediction__isnull=False, created_at__gte=one_week_ago).exists():
                 return JsonResponse({'status': 'error', 'message': f'Patient {patient_id} has a completed report within the last 7 days. Please wait 1 week.'}, status=400)

            report = MedicalReport(
                patient_name=patient_name,
                patient_id=patient_id,
            )
            
            # Link doctor if found
            if doctor_name:
                # First try direct username match (new behavior)
                doc = User.objects.filter(username=doctor_name, userprofile__role='doctor').first()
                if doc:
                    report.doctor = doc
                else:
                    # Fallback for old behavior or brittle name matching if needed
                    parts = doctor_name.replace("Dr. ", "").split(" ")
                    if len(parts) >= 2:
                        first = parts[0]
                        last = " ".join(parts[1:])
                        doc = User.objects.filter(first_name__iexact=first, last_name__iexact=last, userprofile__role='doctor').first()
                        if doc:
                            report.doctor = doc
            
            report.save()
            
            return JsonResponse({'status': 'success', 'message': 'Patient added'})
            
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
            
    return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=400)

@login_required
def complete_report(request):
    """
    Manually mark a report as completed.
    This generates a PDF even if no image was uploaded.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            pid = data.get('patient_id')
            
            report = MedicalReport.objects.filter(patient_id=pid).last()
            if not report:
                return JsonResponse({'status': 'error', 'message': 'Report not found'}, status=404)
            
            if not report.prediction:
                report.prediction = "Low Risk"
            
            report.status = "Completed"
            
            # Generate PDF upon finalization
            display_doctor_name = "Unassigned"
            if report.doctor:
                if report.doctor.first_name or report.doctor.last_name:
                    display_doctor_name = f"Dr. {report.doctor.first_name} {report.doctor.last_name}".strip()
                else:
                    display_doctor_name = report.doctor.username

            # Correct risk factor logic based on prediction
            pred_str = str(report.prediction or "").lower()
            if 'high' in pred_str:
                final_risk_val = 88
                report.prediction = "High Risk"
            else:
                final_risk_val = 12
                report.prediction = "Low Risk"

            pdf_data = {
                'patient_name': report.patient_name,
                'patient_id': report.patient_id,
                'doctor_name': display_doctor_name,
                'prediction': report.prediction,
                'risk_factor': final_risk_val,
                'date': datetime.now().strftime("%Y-%m-%d %H:%M"),
                'image_path': report.image.path if report.image else None
            }
            pdf_buffer = generate_pdf_report(pdf_data)
            filename = f"Final_Report_{pid}_{report.id}.pdf"
            
            # This ensures we overwrite any temporary/uploaded PDF with the final official report
            report.pdf_report.save(filename, ContentFile(pdf_buffer.getvalue()))
            
            report.save()
            return JsonResponse({'status': 'success', 'message': 'Report finalized', 'pdf_url': report.pdf_report.url})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=400)

