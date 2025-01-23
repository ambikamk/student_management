import json
from django.http import HttpResponseBadRequest, JsonResponse
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test

from .forms import LeaveReportStudentForm, LeaveRequestForm, NotificationForm, StudentProfileForm,StudyMaterialFilterForm
from .models import FeedBackStudent, LeaveRequest, Result, SessionYearModel, Student, LeaveReportStudent, AttendanceReport, StudyMaterial, Subject,NotificationStudent
 
import matplotlib.pyplot as plt
import io
import base64
from django.shortcuts import render
from .models import AttendanceReport, Subject, Result
from django.contrib.auth.decorators import login_required

@login_required
def student_dashboard_view(request):
    student = request.user.student

    # Count of total attendance (total attendance sessions the student was marked)
    total_attendance = AttendanceReport.objects.filter(student=student).count()

    # Count of present sessions (where status = True)
    present_count = AttendanceReport.objects.filter(student=student, status=True).count()

    # Count of absent sessions (where status = False)
    absent_count = AttendanceReport.objects.filter(student=student, status=False).count()

    # Count of total subjects for the student's course
    total_subjects = Subject.objects.filter(course=student.course).count()

    # Visualizing attendance chart
    attendance_labels = ['Present', 'Absent']
    attendance_data = [present_count, absent_count]
    fig, ax = plt.subplots()
    ax.pie(attendance_data, labels=attendance_labels, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    # Save the pie chart to a base64 string for embedding in HTML
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    chart_data = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()

    # Exam marks for level of studies visualization
    results = Result.objects.filter(student=student)
    exam_marks = []
    subjects = []
    for result in results:
        subjects.append(result.subject.name)
        exam_marks.append(result.exam_marks)

    # Classify the student's level based on exam marks
    level = "Beginner"
    average_marks = sum(exam_marks) / len(exam_marks) if exam_marks else 0

    if average_marks >= 80:
        level = "Advanced"
    elif average_marks >= 60:
        level = "Intermediate"
    elif average_marks >= 40:
        level = "Basic"

    # Visualizing exam marks chart
    fig2, ax2 = plt.subplots()
    ax2.bar(subjects, exam_marks, color='skyblue')
    ax2.set_xlabel('Subjects')
    ax2.set_ylabel('Marks')
    ax2.set_title('Exam Marks by Subject')

    # Save the bar chart to a base64 string for embedding in HTML
    buf2 = io.BytesIO()
    plt.savefig(buf2, format='png')
    buf2.seek(0)
    exam_marks_data = base64.b64encode(buf2.getvalue()).decode('utf-8')
    buf2.close()

    context = {
        'total_attendance': total_attendance,
        'present_count': present_count,
        'absent_count': absent_count,
        'total_subjects': total_subjects,
        'user': request.user,
        'attendance_chart': chart_data,
        'exam_marks_chart': exam_marks_data,
        'level_of_study': level,
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



@login_required
def view_result(request):
    student = Student.objects.get(user=request.user)
    results = Result.objects.filter(student=student)
    
    result_data = []
    for result in results:
        # Calculate status (Pass/Fail) - assuming 40% is passing mark
        total_marks = result.assignment_marks + result.exam_marks
        max_marks = 100  # Assuming total possible marks is 100
        percentage = (total_marks / max_marks) * 100
        status = "Pass" if percentage >= 40 else "Fail"
        
        result_data.append({
            'subject': result.subject,
            'assignment_marks': result.assignment_marks,
            'exam_marks': result.exam_marks,
            'total_marks': total_marks,
            'status': status
        })
    
    context = {
        'results': result_data,
        'student': student
    }
    return render(request, 'student/view_result.html', context)


@login_required
def student_study_materials(request):
    if not hasattr(request.user, 'student'):
        return redirect('home')  # Redirect if not a student

    student = request.user.student
    
    # Default filter (if no filter is selected)
    study_materials = StudyMaterial.objects.filter(session_year=student.session_year_id, subject__course=student.course)

    # Handling the filtering logic if the form is submitted
    if request.method == 'POST':
        form = StudyMaterialFilterForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            session_year = form.cleaned_data['session_year']
            study_materials = study_materials.filter(subject=subject, session_year=session_year)
    else:
        form = StudyMaterialFilterForm()

    return render(request, 'student/study_material_list.html', {'materials': study_materials, 'form': form})

from django.shortcuts import render
from .models import Timetable
from django.http import Http404

def student_timetable(request):
    # Get the logged-in student
    if hasattr(request.user, 'student') and request.user.student.session_year_id:
        session_year_id = request.user.student.session_year_id.id
        timetable = Timetable.objects.filter(session_year_id=session_year_id)
    else:
        raise Http404("Session year not specified")

    context = {'timetable': timetable}
    return render(request, 'student/timetable.html', context)


import razorpay
from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
from django.http import JsonResponse
from .models import Fees

def fee_list(request):
    student = request.user.student
    fees = Fees.objects.filter(student=student)
    return render(request, 'student/fee_list.html', {'fees': fees})

def create_razorpay_order(request, fee_id):
    fee = get_object_or_404(Fees, id=fee_id)

    if fee.is_paid:
        return JsonResponse({'error': 'Fee already paid'}, status=400)

    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    
    order_data = {
        "amount": int(fee.amount * 100),  # Convert to paise
        "currency": "INR",
        "payment_capture": "1",
    }

    order = client.order.create(order_data)

    fee.razorpay_order_id = order['id']
    fee.save()

    return JsonResponse(order)

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def verify_payment(request):
    if request.method == "POST":
        data = request.POST
        razorpay_order_id = data.get('razorpay_order_id')
        payment_id = data.get('razorpay_payment_id')
        signature = data.get('razorpay_signature')

        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

        try:
            client.utility.verify_payment_signature({
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            })

            fee = Fees.objects.get(razorpay_order_id=razorpay_order_id)
            fee.is_paid = True
            fee.payment_id = payment_id
            fee.save()

            messages.success(request, 'Payment successful!')
            return redirect('student:fee_list')

        except razorpay.errors.SignatureVerificationError:
            messages.error(request, 'Payment verification failed!')
            return redirect('student:fee_list')
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
            return redirect('student:fee_list')

    return HttpResponseBadRequest('Invalid request')
