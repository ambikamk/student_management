import json
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login,logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from student.models import SessionYearModel, Student, Subject, Attendance, AttendanceReport
from .models import FeedBackStaff, LeaveRequest, Staff, LeaveReportStaff
from .forms import LeaveReportStaffForm, LeaveRequestForm, NotificationForm

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
        


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import NotificationStaffs, Staff
from .forms import NotificationForm  # Create a form to handle notification creation

# Check if the user is an admin
def is_admin(user):
    return user.is_superuser

# Admin view to send a notification to a staff
@user_passes_test(is_admin)
def send_notification_to_staff(request):
    if request.method == "POST":
        form = NotificationForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Notification sent successfully.")
                return redirect('staff:send_notification_to_staff')  # Replace with the URL name
            except Exception as e:
                messages.error(request, f"Error sending notification: {e}")
        else:
            messages.error(request, "Invalid form submission.")
    else:
        form = NotificationForm()

    context = {
        'form': form,
        'page_title': 'Send Notification to Staff',
    }
    return render(request, "staff/notification_template.html", context)

# Staff view to see notifications
@login_required
def staff_notifications(request):
    staff = get_object_or_404(Staff, user=request.user)
    notifications = NotificationStaffs.objects.filter(staff_id=staff).order_by('-created_at')

    context = {
        'notifications': notifications,
        'page_title': 'My Notifications',
    }
    return render(request, "staff/notification_template.html", context)

@login_required
def take_attendance(request):
    staff = request.user.staff
    subjects = Subject.objects.filter(staff=staff)
    session_years = SessionYearModel.objects.all()
    
    context = {
        'subjects': subjects,
        'session_years': session_years,
    }
    
    if request.method == 'POST':
        subject_id = request.POST.get('subject')
        session_year_id = request.POST.get('session_year')
        
        subject = Subject.objects.get(id=subject_id)
        session_year = SessionYearModel.objects.get(id=session_year_id)
        
        students = Student.objects.filter(session_year_id=session_year)
        
        # Check if attendance already exists for today
        today = timezone.now().date()
        attendance_exists = Attendance.objects.filter(
            subject=subject,
            attendance_date=today,
            session_year=session_year
        ).exists()
        
        if attendance_exists:
            messages.error(request, "Attendance already taken for this subject today")
            return redirect('staff:take_attendance')
            
        context['subject_selected'] = subject
        context['session_year_selected'] = session_year
        context['students'] = students
        
    return render(request, 'staff/take_attendance.html', context)

@login_required
def save_attendance(request):
    if request.method != 'POST':
        messages.error(request, "Invalid Method")
        return redirect('staff:take_attendance')
        
    subject_id = request.POST.get('subject')
    session_year_id = request.POST.get('session_year')
    student_ids = request.POST.getlist('student_ids[]')
    attendance_status = request.POST.getlist('attendance_status[]')
    
    print(f"Debug - Save Attendance Data:")
    print(f"Subject ID: {subject_id}")
    print(f"Session Year ID: {session_year_id}")
    print(f"Student IDs: {student_ids}")
    print(f"Attendance Status: {attendance_status}")
    
    try:
        subject = Subject.objects.get(id=subject_id)
        session_year = SessionYearModel.objects.get(id=session_year_id)
        
        # Create Attendance
        attendance = Attendance.objects.create(
            subject=subject,
            attendance_date=timezone.now().date(),
            session_year=session_year
        )
        print(f"Debug - Created Attendance record: {attendance.id}")
        
        # Create Attendance Report for each student
        for idx, student_id in enumerate(student_ids):
            try:
                student = Student.objects.get(id=student_id)
                status = attendance_status[idx] if idx < len(attendance_status) else '0'
                
                report = AttendanceReport.objects.create(
                    student=student,
                    attendance=attendance,
                    status=status == '1'  # '1' for present, '0' for absent
                )
                print(f"Debug - Created AttendanceReport for student {student.full_name}: Present={status == '1'}")
            except Student.DoesNotExist:
                print(f"Debug - Error: Student with ID {student_id} not found")
            except Exception as e:
                print(f"Debug - Error creating attendance report: {str(e)}")
        
        messages.success(request, "Attendance taken successfully")
        return redirect('staff:take_attendance')
        
    except Exception as e:
        print(f"Debug - Error in save_attendance: {str(e)}")
        messages.error(request, f"Error taking attendance: {str(e)}")
        return redirect('staff:take_attendance')

@login_required
def update_attendance(request):
    staff = request.user.staff
    subjects = Subject.objects.filter(staff=staff)
    session_years = SessionYearModel.objects.all()
    context = {
        'subjects': subjects,
        'session_years': session_years
    }
    
    if request.method == 'POST':
        subject_id = request.POST.get('subject')
        session_year_id = request.POST.get('session_year')
        attendance_date = request.POST.get('attendance_date')
        
        print(f"Debug - Received data: subject_id={subject_id}, session_year_id={session_year_id}, date={attendance_date}")
        
        try:
            subject = Subject.objects.get(id=subject_id)
            session_year = SessionYearModel.objects.get(id=session_year_id)
            
            # Get all attendance records for the selected criteria
            attendances = Attendance.objects.filter(
                subject=subject,
                attendance_date=attendance_date,
                session_year=session_year
            )
            
            print(f"Debug - Found {attendances.count()} attendance records")
            
            if not attendances.exists():
                messages.error(request, "No attendance records found for the selected criteria")
                return redirect('staff:update_attendance')
            
            # Get the first attendance record and its reports
            attendance = attendances.first()
            attendance_reports = AttendanceReport.objects.filter(attendance=attendance)
            
            print(f"Debug - Found {attendance_reports.count()} attendance reports")
            
            context.update({
                'attendance_reports': attendance_reports,
                'attendance': attendance,
                'selected_date': attendance_date,
                'selected_subject': subject,
                'selected_session': session_year
            })
            
        except (Subject.DoesNotExist, SessionYearModel.DoesNotExist) as e:
            messages.error(request, f"Error: {str(e)}")
            return redirect('staff:update_attendance')
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            return redirect('staff:update_attendance')
        
    return render(request, 'staff/update_attendance.html', context)

@login_required
def save_updated_attendance(request):
    if request.method != 'POST':
        messages.error(request, "Invalid Method")
        return redirect('staff:update_attendance')
        
    attendance_id = request.POST.get('attendance_id')
    student_ids = request.POST.getlist('student_ids[]')
    attendance_status = request.POST.getlist('attendance_status[]')
    
    print(f"Debug - Update data: attendance_id={attendance_id}, students={len(student_ids)}, status={len(attendance_status)}")
    
    try:
        attendance = Attendance.objects.get(id=attendance_id)
        
        for student_id, status in zip(student_ids, attendance_status):
            attendance_report = AttendanceReport.objects.get(
                student_id=student_id,
                attendance=attendance
            )
            attendance_report.status = status == '1'
            attendance_report.save()
            
        messages.success(request, "Attendance updated successfully")
        return redirect('staff:update_attendance')
        
    except Exception as e:
        messages.error(request, f"Error updating attendance: {str(e)}")
        return redirect('staff:update_attendance')
