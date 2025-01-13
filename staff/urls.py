from django.contrib import admin
from django.urls import path
from .views import login_view,logout_view
from . import views

app_name='staff'
urlpatterns = [
    # path('admin/', admin.site.urls),
    path('', login_view, name='login'),
     path('logout/', logout_view, name='logout'),
   
    path('dashboard/', views.dashboard_view, name='dashboard'), 
    path('apply-leave/', views.staff_apply_leave, name='staff_apply_leave'),
]