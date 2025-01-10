from django.contrib import admin
from django.urls import path
from .views import login_view
from . import views

app_name='staff'
urlpatterns = [
    # path('admin/', admin.site.urls),
    path('', login_view, name='login'),
   
    path('dashboard/', views.dashboard_view, name='dashboard'), 
]