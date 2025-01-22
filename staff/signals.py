from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.contrib.auth.models import User
from .models import Staff

@receiver(post_save, sender=Staff)
def send_staff_credentials_email(sender, instance, created, **kwargs):
    if created:  # Only send email when a new staff member is created
        subject = "Staff Account Created"
        message = f"Hello {instance.full_name},\n\nYour staff account has been created.\nUsername: {instance.user.username}\nPassword: (Set by admin)\n\nPlease login and update your password."
        send_mail(subject, message, "mkambika287@gmail.com", [instance.email], fail_silently=False)
