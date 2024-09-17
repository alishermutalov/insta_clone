import re
import threading
import phonenumbers
import decouple
from twilio.rest import Client

from rest_framework.exceptions import ValidationError
from django.core.mail import send_mail
from django.conf import settings


email_regex = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b')

def check_email_or_phone(email_or_phone):
    if re.fullmatch(email_regex, email_or_phone):
        return "email"
    try:
        phone_number = phonenumbers.parse(email_or_phone) 
        if phonenumbers.is_valid_number(phone_number):
            return "phone"
    except phonenumbers.NumberParseException as e:
        raise ValidationError({
            "success": False,
            "message": "Email or Phone number invalid",
            "details": str(e)
        })
    raise ValidationError({
            "success":False,
            "message":"Email or Phone number invalid"
        })
        
class EmailThread(threading.Thread):
    def __init__(self, subject, message, recipient_list) :
        self.subject = subject
        self.message = message
        self.recipient_list = recipient_list
        threading.Thread.__init__(self)
        
    def run(self) -> None:
        send_mail(
            self.subject,
            self.message,
            settings.DEFAULT_FROM_EMAIL,
            self.recipient_list
        )
        
def send_async_mail(subject:str, message:str, recipient_list:list[str]):
    EmailThread(subject, message, recipient_list).start()

def send_sms_verification_code(phone_number, code):
    account_sid = decouple.config('TWILIO_ACCOUNT_SID')
    auth_token = decouple.config('TWILIO_AUTH_TOKEN')
    from_user = decouple.config('FROM_USER_PHONE_NUMBER')
    client = Client(account_sid, auth_token)
    client.messages.create(
        body=f"Your verification code: {code}",
        from_= from_user,
        to = str(phone_number)
    )