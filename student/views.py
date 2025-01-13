from django.shortcuts import render
from django.contrib.auth.decorators import login_required
def home(request):
    return render(request,"student/home.html")

@login_required
def student_dashboard_view(request):
    return render(request, 'student/dashboard.html', {'user': request.user})
# Create your views here.

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from .models import LeaveRequest, Student, LeaveReportStudent
from .forms import LeaveReportStudentForm, LeaveRequestForm

def student_apply_leave(request):
    form = LeaveRequestForm(request.POST or None)
    student = request.user  # Assuming the User model is directly used for students

    context = {
        'form': form,
        'leave_history': LeaveRequest.objects.filter(user=student),
        'page_title': 'Apply for Leave'
    }

    if request.method == 'POST':
        if form.is_valid():
            try:
                obj = form.save(commit=False)
                obj.user = student  # Assign the current logged-in user
                obj.save()
                messages.success(
                    request, "Application for leave has been submitted for review."
                )
                return redirect(reverse('student_apply_leave'))
            except Exception as e:
                messages.error(request, f"Could not submit: {str(e)}")
        else:
            messages.error(request, "Form contains errors!")

    return render(request, "student/student_apply_leave.html", context)
