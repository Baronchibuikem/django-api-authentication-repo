import logging
from uuid import UUID
from django.template.loader import render_to_string
from django.utils import timezone
from rest_framework import status
from django.core.mail import send_mail

from account.models import CustomUser, UserEmail
from account.constants import EMAIL_TYPE_WELCOME
from django.conf import settings
from djangoauthentications.celery import app



def _send_welcome_mail_task(user_id: UUID) -> bool:
    """Send user a welcome email and notification when registration is successful."""
    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        return False

    if UserEmail.objects.filter(user=user, email_type=EMAIL_TYPE_WELCOME).exists():
        return False

    result = send_mail(
            'Welcome to the Tribe',
            'Welcome to our platform, your registration was successful.',
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=False,
        )

    if result:
        UserEmail.objects.create(user=user, email_type=EMAIL_TYPE_WELCOME)

    return True


@app.task(name='send_welcome_mail_task')
def send_welcome_mail_task(user_id: UUID) -> bool:
    """Send a welcome email and notification to a user upon successful registration."""
    return _send_welcome_mail_task(user_id)