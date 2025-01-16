from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import LeaveReportStudentForm, LeaveRequestForm, NotificationForm, StudentProfileForm  
from .models import FeedBackStudent, LeaveRequest, Student, LeaveReportStudent, AttendanceReport, Subject,NotificationStudent
 

    


@login_required
def student_dashboard_view(request):
    # Get the logged-in student
    student = Student.objects.get(user=request.user)

    # Count of total attendance (total attendance sessions the student was marked)
    total_attendance = AttendanceReport.objects.filter(student=student).count()

    # Count of present sessions (where status = True)
    present_count = AttendanceReport.objects.filter(student=student, status=True).count()

    # Count of absent sessions (where status = False)
    absent_count = AttendanceReport.objects.filter(student=student, status=False).count()

    # Count of total subjects for the student's course
    total_subjects = Subject.objects.filter(course=student.course).count()

    context = {
        'total_attendance': total_attendance,
        'present_count': present_count,
        'absent_count': absent_count,
        'total_subjects': total_subjects,
        'user': request.user
    }
    return render(request, 'student/dashboard.html', context)


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
        
 
# Check if the user is an admin
def is_admin(user):
    return user.is_superuser

# Admin view to send a notification to a student
@user_passes_test(is_admin)
def send_notification_to_student(request):
    if request.method == "POST":
        form = NotificationForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Notification sent successfully.")
                return redirect('send_notification_to_student')  # Replace with the URL name
            except Exception as e:
                messages.error(request, f"Error sending notification: {e}")
        else:
            messages.error(request, "Invalid form submission.")
    else:
        form = NotificationForm()

    context = {
        'form': form,
        'page_title': 'Send Notification to Student',
    }
    return render(request, "common/notification_template.html", context)

# Student view to see notifications
@login_required
def student_notifications(request):
    student = get_object_or_404(Student, user=request.user)
    notifications = NotificationStudent.objects.filter(student_id=student).order_by('-created_at')

    context = {
        'notifications': notifications,
        'page_title': 'My Notifications',
    }
    return render(request, "student/notification_template.html", context)
# Add the following views

@login_required
def view_attendance(request):
    student = request.user.student
    attendance_reports = AttendanceReport.objects.filter(student=student).select_related(
        'attendance__subject', 'attendance__session_year'
    ).order_by('-attendance__attendance_date')

    # Group attendance by subject
    subjects = Subject.objects.filter(course=student.course)
    attendance_by_subject = {}

    for subject in subjects:
        subject_attendance = attendance_reports.filter(attendance__subject=subject)
        if subject_attendance.exists():
            total_classes = subject_attendance.count()
            present_count = subject_attendance.filter(status=True).count()
            attendance_percentage = (present_count / total_classes) * 100 if total_classes > 0 else 0

            attendance_by_subject[subject] = {
                'total_classes': total_classes,
                'present_count': present_count,
                'attendance_percentage': round(attendance_percentage, 2),
                'attendance_records': subject_attendance
            }

    context = {
        'attendance_by_subject': attendance_by_subject,
        'student': student
    }

    return render(request, 'student/view_attendance.html', context)

@login_required
def attendance_detail(request):
    student = request.user.student
    subject_id = request.GET.get('subject')

    if not subject_id:
        messages.error(request, "Please select a subject")
        return redirect('student:view_attendance')

    try:
        subject = Subject.objects.get(id=subject_id, course=student.course)
        attendance_reports = AttendanceReport.objects.filter(
            student=student,
            attendance__subject=subject
        ).select_related('attendance').order_by('-attendance__attendance_date')

        context = {
            'subject': subject,
            'attendance_reports': attendance_reports,
            'student': student
        }

        return render(request, 'student/attendance_detail.html', context)

    except Subject.DoesNotExist:
        messages.error(request, "Subject not found")
        return redirect('student:view_attendance')

# ... (rest of the code remains the same)

@login_required
def student_profile(request):
    student = Student.objects.get(user=request.user)
    if request.method == 'POST':
        form = StudentProfileForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            return redirect('student:dashboard')  # Redirect to the profile page after saving
    else:
        form = StudentProfileForm(instance=student)
    return render(request, 'student/student_profile.html', {'form': form})

def change_password_student(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Keeps the user logged in after password change
            messages.success(request, 'Your password was successfully updated!')
            return redirect('student:dashboard')  # Redirect to student's dashboard
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'student/change_password.html', {'form': form})