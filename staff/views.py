
import io
import json
import base64
import matplotlib.pyplot as plt
from django.urls import reverse
from django.utils import timezone
from django.contrib import messages
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import authenticate, login,logout
from django.shortcuts import render ,redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from student.forms import StudyMaterialForm
from student.models import Result, SessionYearModel, Student, StudyMaterial, Subject, Attendance, AttendanceReport
from .models import FeedBackStaff, LeaveRequest, Staff, LeaveReportStaff,NotificationStaffs
from .forms import LeaveReportStaffForm, LeaveRequestForm, NotificationForm, StaffProfileForm



def home(request):
    return render(request, 'common/home.html')

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
    return redirect('staff:login')


@login_required
def dashboard_view(request):
    staff = request.user.staff

    # Count of total students under this staff
    students_count = Student.objects.filter(course__subject__staff=staff).distinct().count()

    # Count of total attendance taken by this staff
    total_attendance = Attendance.objects.filter(subject__staff=staff).count()

    # Count of leaves taken by this staff (filter only approved leaves)
    leaves_count = LeaveReportStaff.objects.filter(staff=staff, status='approved').count()

    # Count of subjects assigned to this staff
    total_subjects = Subject.objects.filter(staff=staff).count()

    # Visualization for attendance and leave chart
    if total_attendance == 0 and leaves_count == 0:
        # Add dummy data to ensure chart visibility when no data is available
        attendance_labels = ['No Attendance or Leaves']
        attendance_data = [1]
    else:
        attendance_labels = ['Total Attendance', 'Leaves']
        attendance_data = [total_attendance, leaves_count]

    fig, ax = plt.subplots()
    ax.pie(attendance_data, labels=attendance_labels, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')  # Equal aspect ratio ensures the pie is drawn as a circle.

    # Save the pie chart to a base64 string for embedding in HTML
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    attendance_chart_data = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()

    # Subjects and students chart
    fig2, ax2 = plt.subplots()
    ax2.bar(['Subjects', 'Students'], [total_subjects, students_count], color=['skyblue', 'orange'])
    ax2.set_xlabel('Categories')
    ax2.set_ylabel('Count')
    ax2.set_title('Subjects and Students Overview')

    # Save the bar chart to a base64 string for embedding in HTML
    buf2 = io.BytesIO()
    plt.savefig(buf2, format='png')
    buf2.seek(0)
    subjects_students_chart_data = base64.b64encode(buf2.getvalue()).decode('utf-8')
    buf2.close()

    context = {
        'students_count': students_count,
        'total_attendance': total_attendance,
        'leaves_count': leaves_count,
        'total_subjects': total_subjects,
        'attendance_chart': attendance_chart_data,
        'subjects_students_chart': subjects_students_chart_data,
        'user': request.user,
    }
    return render(request, 'staff/dashboard.html', context)


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
                return redirect(reverse('staff:staff_apply_leave'))
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
    
    try:
        subject = Subject.objects.get(id=subject_id)
        session_year = SessionYearModel.objects.get(id=session_year_id)
        
        # Create Attendance
        attendance = Attendance.objects.create(
            subject=subject,
            attendance_date=timezone.now().date(),
            session_year=session_year
        )
        
        # Create Attendance Report for each student
        for student_id in student_ids:
            try:
                student = Student.objects.get(id=student_id)
                status = request.POST.get(f'attendance_status_{student_id}') == '1'
                
                report = AttendanceReport.objects.create(
                    student=student,
                    attendance=attendance,
                    status=status  # True for present, False for absent
                )
                print(f"Debug - Created AttendanceReport for student {student.full_name}: Present={status}")
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
    
    try:
        attendance = Attendance.objects.get(id=attendance_id)
        
        for student_id in student_ids:
            try:
                attendance_report = AttendanceReport.objects.get(
                    student_id=student_id,
                    attendance=attendance
                )
                status = request.POST.get(f'attendance_status_{student_id}') == '1'
                attendance_report.status = status
                attendance_report.save()
            except AttendanceReport.DoesNotExist:
                print(f"Debug - Error: Attendance report not found for student {student_id}")
            
        messages.success(request, "Attendance updated successfully")
        return redirect('staff:update_attendance')
        
    except Exception as e:
        messages.error(request, f"Error updating attendance: {str(e)}")
        return redirect('staff:update_attendance')

@login_required
def staff_profile(request):
    staff = Staff.objects.get(user=request.user)
    if request.method == 'POST':
        form = StaffProfileForm(request.POST, instance=staff)
        if form.is_valid():
            form.save()
            return redirect('staff:dashboard')  # Redirect to the profile page after saving
    else:
        form = StaffProfileForm(instance=staff)
    return render(request, 'staff/staff_profile.html', {'form': form})

def change_password_staff(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Keeps the user logged in after password change
            messages.success(request, 'Your password was successfully updated!')
            return redirect('staff:dashboard')  # Redirect to staff's dashboard
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'staff/change_password.html', {'form': form})

@login_required
def add_result(request):
    staff = Staff.objects.get(user=request.user)
    subjects = Subject.objects.filter(staff=staff)
    session_years = SessionYearModel.objects.all()
    
    context = {
        'subjects': subjects,
        'session_years': session_years,
    }
    
    return render(request, 'staff/add_result.html', context)

@login_required
def get_students(request):
    subject_id = request.GET.get('subject')
    session_year_id = request.GET.get('session_year')
    
    students = Student.objects.filter(session_year_id=session_year_id, course=Subject.objects.get(id=subject_id).course)
    student_list = []
    
    for student in students:
        result = Result.objects.filter(student=student, subject_id=subject_id, session_year_id=session_year_id).first()
        student_data = {
            'id': student.id,
            'name': student.full_name,
            'assignment_marks': result.assignment_marks if result else 0,
            'exam_marks': result.exam_marks if result else 0
        }
        student_list.append(student_data)
    
    return JsonResponse({'students': student_list})

@login_required
def save_result(request):
    if request.method != 'POST':
        return HttpResponseBadRequest()
        
    subject_id = request.POST.get('subject')
    session_year_id = request.POST.get('session_year')
    student_data = json.loads(request.POST.get('student_results'))
    
    for data in student_data:
        student = Student.objects.get(id=data['student_id'])
        result, created = Result.objects.get_or_create(
            student=student,
            subject_id=subject_id,
            session_year_id=session_year_id,
            defaults={
                'assignment_marks': float(data['assignment_marks']),
                'exam_marks': float(data['exam_marks'])
            }
        )
        
        if not created:
            result.assignment_marks = float(data['assignment_marks'])
            result.exam_marks = float(data['exam_marks'])
            result.save()
    
    return JsonResponse({'status': 'success'})


@login_required
def upload_study_material(request):
    if not hasattr(request.user, 'staff'):
        return redirect('home')  # Redirect if not staff

    # Fetch study materials uploaded by the logged-in staff
    materials = StudyMaterial.objects.filter(uploaded_by=request.user.staff)

    if request.method == "POST":
        form = StudyMaterialForm(request.POST, request.FILES)
        if form.is_valid():
            study_material = form.save(commit=False)
            study_material.uploaded_by = request.user.staff  # Assign the logged-in staff
            study_material.save()
            return redirect('staff:upload_study_material')  # Reload page after upload
    else:
        form = StudyMaterialForm()

    return render(request, 'staff/upload_study_material.html', {
        'form': form,
        'materials': materials  # Pass study materials to the template
    })

@login_required
def edit_study_material(request, material_id):
    material = get_object_or_404(StudyMaterial, id=material_id, uploaded_by=request.user.staff)

    if request.method == "POST":
        form = StudyMaterialForm(request.POST, request.FILES, instance=material)
        if form.is_valid():
            form.save()
            return redirect('staff:upload_study_material')
    else:
        form = StudyMaterialForm(instance=material)

    return render(request, 'staff/edit_study_material.html', {'form': form})


@login_required
def delete_study_material(request, material_id):
    material = get_object_or_404(StudyMaterial, id=material_id, uploaded_by=request.user.staff)
    material.delete()
    return redirect('staff:upload_study_material')
