from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            if hasattr(user, 'staff'):
                return redirect('staff:dashboard')
            elif hasattr(user, 'student'):
                return redirect('student:dashboard')
            else:
                messages.error(request, "User type not recognized.")
        else:
            messages.error(request, "Invalid username or password.")
    
    # Render the shared login page
    return render(request, 'common/login.html')

@login_required
def dashboard_view(request):
    return render(request, 'staff/dashboard.html', {'user': request.user})
# Create your views here.
