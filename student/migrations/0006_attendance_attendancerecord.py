# Generated by Django 5.1 on 2025-01-15 06:08

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0005_remove_attendancereport_attendance_id_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Attendance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(auto_now_add=True)),
                ('session_year', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='student.sessionyearmodel')),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='student.subject')),
            ],
        ),
        migrations.CreateModel(
            name='AttendanceRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.BooleanField(default=False)),
                ('attendance', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='student.attendance')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='student.student')),
            ],
        ),
    ]