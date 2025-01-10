from django.shortcuts import render
from django.contrib.auth.decorators import login_required
def home(request):
    return render(request,"student/home.html")

@login_required
def student_dashboard_view(request):
    return render(request, 'student/dashboard.html', {'user': request.user})
# Create your views here.
