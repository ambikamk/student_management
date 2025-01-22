from django.contrib import admin
from django.urls import path
from . import views

app_name='student'

urlpatterns = [
    # path('admin/', admin.site.urls),
    
   
    path('dashboard/', views.student_dashboard_view, name='dashboard'), 
    path('apply-leave/', views.student_apply_leave, name='student_apply_leave'),
    path('student_feedback/', views.student_feedback, name="student_feedback"),
    path('student_feedback_save/', views.student_feedback_save, name="student_feedback_save"),
    path('student/notifications/', views.student_notifications, name='student_notifications'),
    path('view-attendance/', views.view_attendance, name='view_attendance'),
    path('attendance-detail/', views.attendance_detail, name='attendance_detail'),
    path('student/profile/', views.student_profile, name='student_profile'),
    path('student/change_password/', views.change_password_student, name='change_password_student'),
    path('view_result/', views.view_result, name='view_result'),
    path('study-materials/', views.student_study_materials, name='study_material_list'),
]