from django.urls import path
from . import views
from .views import login_view, logout_view

app_name='staff'
urlpatterns = [
    path('', views.home, name='home'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'), 
    path('apply-leave/', views.staff_apply_leave, name='staff_apply_leave'),
    path('staff_feedback/', views.staff_feedback, name="staff_feedback"),
    path('staff_feedback_save/', views.staff_feedback_save, name="staff_feedback_save"),
    path('staff/notifications/', views.staff_notifications, name='staff_notifications'),
    path('take-attendance/', views.take_attendance, name='take_attendance'),
    path('save-attendance/', views.save_attendance, name='save_attendance'),
    path('update-attendance/', views.update_attendance, name='update_attendance'),
    path('save-updated-attendance/', views.save_updated_attendance, name='save_updated_attendance'),
    path('staff/profile/', views.staff_profile, name='staff_profile'),
    path('staff/change_password/', views.change_password_staff, name='change_password_staff'),
    path('add_result/', views.add_result, name='add_result'),
    path('get_students/', views.get_students, name='get_students'),
    path('save_result/', views.save_result, name='save_result'),
    path('upload-study-material/', views.upload_study_material, name='upload_study_material'),
    path('delete-material/<int:material_id>/', views.delete_study_material, name='delete_study_material'),
    path('edit-material/<int:material_id>/', views.edit_study_material, name='edit_study_material'),
]