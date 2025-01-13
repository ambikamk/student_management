from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login,logout
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
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard_view(request):
    return render(request, 'staff/dashboard.html', {'user': request.user})
# Create your views here.

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from .models import FeedBackStaff, LeaveRequest, Staff, LeaveReportStaff
from .forms import LeaveReportStaffForm, LeaveRequestForm

def staff_apply_leave(request):
    form = LeaveRequestForm(request.POST or None)
    staff = request.user  # Assuming the User model is directly used for students

    context = {
        'form': form,
        'leave_history': LeaveRequest.objects.filter(user=staff),
        'page_title': 'Apply for Leave'
    }

    if request.method == 'POST':
        if form.is_valid():
            try:
                obj = form.save(commit=False)
                obj.user = staff  # Assign the current logged-in user
                obj.save()
                messages.success(
                    request, "Application for leave has been submitted for review."
                )
                return redirect(reverse('staff_apply_leave'))
            except Exception as e:
                messages.error(request, f"Could not submit: {str(e)}")
        else:
            messages.error(request, "Form contains errors!")

    return render(request, "staff/staff_apply_leave.html", context)


def staff_feedback(request):
    # Query the Staff model using the 'user' field instead of 'admin'
    staff_obj = Staff.objects.get(user=request.user)  # Use 'user' instead of 'admin'
    feedback_data = FeedBackStaff.objects.filter(staff_id=staff_obj)
    context = {
        "feedback_data": feedback_data
    }
    return render(request, "staff/staff_feedback.html", context)

def staff_feedback_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method.")
        return redirect('staff:staff_feedback')
    else:
        feedback = request.POST.get('feedback_message')
        # Query the Staff model using the 'user' field instead of 'admin'
        staff_obj = Staff.objects.get(user=request.user)  # Use 'user' instead of 'admin'

        try:
            add_feedback = FeedBackStaff(staff_id=staff_obj, feedback=feedback, feedback_reply="")
            add_feedback.save()
            messages.success(request, "Feedback Sent.")
            return redirect('staff:staff_feedback')
        except Exception as e:
            messages.error(request, f"Failed to Send Feedback: {str(e)}")
            return redirect('staff:staff_feedback')
