from django import forms
from .models import Contact, ScheduledMessage
from django.core.validators import RegexValidator
from django.utils import timezone 


# class ContactForm(forms.ModelForm):
#     class Meta:
#         model = Contact
#         fields = ['name', 'phone_number']

class ContactForm(forms.ModelForm):
    phone_number = forms.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                regex=r'^\+\d{10,15}$',
                message='Phone number must be entered in the format: "+1234567890". Up to 15 digits allowed.'
            ),
        ]
    )

    class Meta:
        model = Contact
        fields = ['name', 'phone_number']

class MessageForm(forms.Form):
    message = forms.CharField(widget=forms.Textarea, max_length=1000)

class CSVUploadForm(forms.Form):
    csv_file = forms.FileField()
    

class ScheduleMessageForm(forms.ModelForm):
    scheduled_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        help_text='Format: YYYY-MM-DD HH:MM'
    )
    contacts = forms.ModelMultipleChoiceField(
        queryset=Contact.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        help_text='Select contacts to send the message to.'
    )

    class Meta:
        model = ScheduledMessage
        fields = ['message', 'scheduled_time', 'contacts']

    def clean_scheduled_time(self):
        scheduled_time = self.cleaned_data['scheduled_time']
        if scheduled_time < timezone.now():
            raise forms.ValidationError("Scheduled time must be in the future.")
        return scheduled_time
    
