from django.contrib.auth.models import User
from django.db import models
from staff.models import Staff
from django.utils import timezone


class SessionYearModel(models.Model):
    id = models.AutoField(primary_key=True)
    session_start_year = models.DateField()
    session_end_year = models.DateField()

    def __str__(self):
        return f"{self.session_start_year.year} - {self.session_end_year.year}"

class Course(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
   

    def __str__(self):
        return self.name


class Subject(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE, default=1) #need to give defauult course
    staff= models.ForeignKey(Staff, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    session_year_id = models.ForeignKey(SessionYearModel, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.full_name

class LeaveReportStudent(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.CharField(max_length=60)
    message = models.TextField()
    status = models.SmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)




class LeaveRequest(models.Model):
    STATUS_CHOICES = [
        (0, 'Pending'),
        (1, 'Approved'),
        (2, 'Rejected'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='student_leave_requests')
    date = models.DateField()
    message = models.TextField()
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return f"{self.user.username} - {self.get_status_display()}"
    

class FeedBackStudent(models.Model):
    id = models.AutoField(primary_key=True)
    student_id = models.ForeignKey(Student, on_delete=models.CASCADE)
    feedback = models.TextField()
    feedback_reply = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()


# Create your models here.


class NotificationStudent(models.Model):
    id = models.AutoField(primary_key=True)
    student_id = models.ForeignKey(Student, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()


class Attendance(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    attendance_date = models.DateField(default=timezone.now)
    session_year = models.ForeignKey(SessionYearModel, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.subject.name} - {self.attendance_date}"

    def save(self, *args, **kwargs):
        if not self.id:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        return super().save(*args, **kwargs)

class AttendanceReport(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    attendance = models.ForeignKey(Attendance, on_delete=models.CASCADE)
    status = models.BooleanField(default=False)  # True for Present, False for Absent
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.student.full_name} - {self.attendance.attendance_date} - {'Present' if self.status else 'Absent'}"

    def save(self, *args, **kwargs):
        if not self.id:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        return super().save(*args, **kwargs)

<<<<<<< HEAD

=======
>>>>>>> bd0dc2661a40dec183d115edf39bb71d9b09c58e
class Result(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    session_year = models.ForeignKey(SessionYearModel, on_delete=models.CASCADE)
    assignment_marks = models.FloatField(default=0)
    exam_marks = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student.full_name} - {self.subject.name}"

    @property
    def total_marks(self):
        return self.assignment_marks + self.exam_marks
<<<<<<< HEAD


class StudyMaterial(models.Model):
    title = models.CharField(max_length=255)
    subject = models.ForeignKey('student.Subject', on_delete=models.CASCADE)
    session_year = models.ForeignKey(SessionYearModel, on_delete=models.CASCADE)
    uploaded_by = models.ForeignKey('staff.Staff', on_delete=models.CASCADE)
    file = models.FileField(upload_to='study_materials/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.subject.name}"
=======
>>>>>>> bd0dc2661a40dec183d115edf39bb71d9b09c58e
