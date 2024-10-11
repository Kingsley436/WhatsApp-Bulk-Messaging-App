from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import User
# from django.contrib.auth.models import AbstractUser
from django.conf import settings


class Contact(models.Model):
    name = models.CharField(max_length=100)
    phone_number = models.CharField(
        max_length=20,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^\+\d{10,15}$',
                message='Phone number must be entered in the format: "+1234567890". Up to 15 digits allowed.'
            ),
        ]
    )
    last_message_sent = models.DateTimeField(null=True, blank=True)
    messages_sent = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name} ({self.phone_number})"


class ScheduledMessage(models.Model):
    # user = models.ForeignKey(User, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField(max_length=1000)
    scheduled_time = models.DateTimeField()
    contacts = models.ManyToManyField(Contact)
    sent = models.BooleanField(default=False)

    def __str__(self):
        return f"Message scheduled at {self.scheduled_time} by {self.user.username}"

