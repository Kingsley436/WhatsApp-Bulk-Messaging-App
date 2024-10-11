import csv
import io
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ContactForm, MessageForm, CSVUploadForm, ScheduleMessageForm, ScheduledMessage
from .models import Contact
from django.conf import settings
from twilio.rest import Client
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .tasks import send_whatsapp_message
from django.utils import timezone
from django.core.exceptions import ValidationError


def index(request):
    return HttpResponse("Hello, world!")

def home(request):
    return render(request, 'messaging/home.html')

@login_required
def add_contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Contact added successfully.')
            return redirect('list_contacts')
    else:
        form = ContactForm()
    return render(request, 'messaging/add_contact.html', {'form': form})


@login_required
def list_contacts(request):
    contacts = Contact.objects.all()
    return render(request, 'messaging/list_contacts.html', {'contacts': contacts})


@login_required
def send_message(request):
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message_body = form.cleaned_data['message']
            # Example validation: disallow certain keywords
            prohibited_keywords = ['spam', 'advertisement']
            if any(keyword in message_body.lower() for keyword in prohibited_keywords):
                messages.error(request, 'Your message contains prohibited content.')
                return redirect('send_message')
            contacts = Contact.objects.all()
            contact_ids = list(contacts.values_list('id', flat=True))
            # Enqueue the task
            send_whatsapp_message.delay(message_body, contact_ids)
            messages.success(request, 'Your messages are being sent in the background.')
            return redirect('send_message')
    else:
        form = MessageForm()
    return render(request, 'messaging/send_message.html', {'form': form})


@login_required
def upload_contacts_csv(request):
    if request.method == 'POST':
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']
            if not csv_file.name.endswith('.csv'):
                messages.error(request, 'This is not a CSV file.')
                return redirect('upload_contacts_csv')
            try:
                data_set = csv_file.read().decode('UTF-8')
                io_string = io.StringIO(data_set)
                reader = csv.reader(io_string, delimiter=',', quotechar='"')
                header = next(reader)  # Skip header
                added = 0
                skipped = 0
                for row in reader:
                    if len(row) < 2:
                        skipped += 1  # Skip incomplete rows
                        continue
                    name, phone_number = row[0].strip(), row[1].strip()
                    # Validate phone number format
                    if not phone_number.startswith('+') or not phone_number[1:].isdigit():
                        skipped += 1
                        continue
                    contact, created = Contact.objects.get_or_create(
                        phone_number=phone_number,
                        defaults={'name': name}
                    )
                    if created:
                        added += 1
                    else:
                        skipped += 1  # Duplicate entry
                messages.success(request, f"Contacts uploaded successfully! Added: {added}, Skipped (duplicates or invalid): {skipped}.")
                return redirect('list_contacts')
            except UnicodeDecodeError:
                messages.error(request, 'Error decoding the CSV file. Please ensure it is UTF-8 encoded.')
                return redirect('upload_contacts_csv')
            except Exception as e:
                messages.error(request, f"An unexpected error occurred: {str(e)}")
                return redirect('upload_contacts_csv')
    else:
        form = CSVUploadForm()
    return render(request, 'messaging/upload_contacts_csv.html', {'form': form})


@login_required
def schedule_message(request):
    if request.method == 'POST':
        form = ScheduleMessageForm(request.POST)
        if form.is_valid():
            scheduled_message = form.save(commit=False)
            scheduled_message.user = request.user
            scheduled_message.save()
            form.save_m2m()
            messages.success(request, 'Message scheduled successfully.')
            return redirect('list_scheduled_messages')
    else:
        form = ScheduleMessageForm()
    return render(request, 'messaging/schedule_message.html', {'form': form})


@login_required
def list_scheduled_messages(request):
    scheduled_messages = ScheduledMessage.objects.filter(user=request.user, sent=False)
    return render(request, 'messaging/list_scheduled_messages.html', {'scheduled_messages': scheduled_messages})


@login_required
def contact_statistics(request):
    contacts = Contact.objects.all().order_by('-messages_sent')
    return render(request, 'messaging/contact_statistics.html', {'contacts': contacts})


