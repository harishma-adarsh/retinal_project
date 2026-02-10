from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('doctor/', views.doctor_view, name='doctor'),
    path('lab/', views.lab_view, name='lab'),
    path('admin_panel/', views.admin_view, name='admin_panel'),
    path('analyze/', views.analyze_image, name='analyze_image'),
    path('add_patient/', views.add_patient, name='add_patient'),
    path('complete_report/', views.complete_report, name='complete_report'),
]
