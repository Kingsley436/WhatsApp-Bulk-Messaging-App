from celery import shared_task
from django.conf import settings
from twilio.rest import Client
from .models import Contact, ScheduledMessage
from twilio.base.exceptions import TwilioRestException
import logging
from django.utils import timezone

logger = logging.getLogger(__name__)

@shared_task
def send_whatsapp_message(message_body, contact_ids):
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    failed_numbers = []
    for contact_id in contact_ids:
        try:
            contact = Contact.objects.get(id=contact_id)
            message = client.messages.create(
                body=message_body,
                from_=settings.TWILIO_WHATSAPP_NUMBER,
                to=f'whatsapp:{contact.phone_number}'
            )
            # Log message SID for successful messages
            logger.info(f"Message sent to {contact.phone_number}, SID: {message.sid}")
            contact.last_message_sent = timezone.now()
            contact.messages_sent += 1
            contact.save()
        except TwilioRestException as e:
            logger.error(f"Twilio error for {contact.phone_number}: {str(e)}")
            failed_numbers.append(contact.phone_number)
        except Contact.DoesNotExist:
            logger.error(f"Contact with ID {contact_id} does not exist.")
            failed_numbers.append("Unknown")
        except Exception as e:
            logger.error(f"Unexpected error for {contact.phone_number}: {str(e)}")
            failed_numbers.append(contact.phone_number)
    return failed_numbers



@shared_task
def send_scheduled_messages():
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    now = timezone.now()
    messages_to_send = ScheduledMessage.objects.filter(scheduled_time__lte=now, sent=False)
    for scheduled_message in messages_to_send:
        failed_numbers = []
        for contact in scheduled_message.contacts.all():
            try:
                message = client.messages.create(
                    body=scheduled_message.message,
                    from_=settings.TWILIO_WHATSAPP_NUMBER,
                    to=f'whatsapp:{contact.phone_number}'
                )
                logger.info(f"Message sent to {contact.phone_number}, SID: {message.sid}")
            except Exception as e:
                logger.error(f"Error sending to {contact.phone_number}: {str(e)}")
                failed_numbers.append(contact.phone_number)

        if failed_numbers:
            # Optionally, log or notify about failed messages
            logger.error(f"Failed to send messages to: {failed_numbers}")
            
        scheduled_message.sent = True
        scheduled_message.save()


