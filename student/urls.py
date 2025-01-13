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
]