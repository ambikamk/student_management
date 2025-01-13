from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from .models import FeedBackStudent, LeaveRequest, Student, LeaveReportStudent
from .forms import LeaveReportStudentForm, LeaveRequestForm


def home(request):
    return render(request,"student/home.html")

@login_required
def student_dashboard_view(request):
    return render(request, 'student/dashboard.html', {'user': request.user})
# Create your views here.

# Create your views here.

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

def student_feedback(request):
    student_obj = Student.objects.get(user=request.user.id)  # Use 'user' instead of 'admin'
    feedback_data = FeedBackStudent.objects.filter(student_id=student_obj)
    context = {
        "feedback_data": feedback_data
    }
    return render(request, 'student/student_feedback.html', context)
def student_feedback_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method.")
        return redirect('student:student_feedback')
    else:
        feedback = request.POST.get('feedback_message')
        student_obj = Student.objects.get(user=request.user.id)  # Use 'user' instead of 'admin'

        try:
            add_feedback = FeedBackStudent(student_id=student_obj, feedback=feedback, feedback_reply="")
            add_feedback.save()
            messages.success(request, "Feedback Sent.")
            return redirect('student:student_feedback')
        except:
            messages.error(request, "Failed to Send Feedback.")
            return redirect('student:student_feedback')
