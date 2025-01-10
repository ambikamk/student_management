from django.contrib.auth.models import User
from django.db import models
from staff.models import Staff

class Course(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='courses')

    def __str__(self):
        return self.name

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.full_name




# Create your models here.
