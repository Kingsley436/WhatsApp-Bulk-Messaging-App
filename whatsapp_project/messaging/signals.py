from django.contrib.auth.signals import user_logged_out
from django.dispatch import receiver
from django.contrib import messages

@receiver(user_logged_out)
def on_user_logged_out(sender, request, user, **kwargs):
    messages.info(request, "You have successfully logged out.")
