<<<<<<< HEAD
# Generated by Django 5.1 on 2025-01-20 04:57
=======
# Generated by Django 5.1 on 2025-01-16 06:08
>>>>>>> bd0dc2661a40dec183d115edf39bb71d9b09c58e

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0007_remove_attendance_date_attendance_attendance_date_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Result',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('assignment_marks', models.FloatField(default=0)),
                ('exam_marks', models.FloatField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('session_year', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='student.sessionyearmodel')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='student.student')),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='student.subject')),
            ],
        ),
    ]
