import re
from rest_framework.exceptions import ValidationError
import threading
from django.core.mail import send_mail
from django.conf import settings


email_regex = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b')
phone_regex = re.compile(r'^\+?[1-9]\d{6,14}$')

def check_email_or_phone(email_or_phone):
    if re.fullmatch(email_regex, email_or_phone):
        return "email"
    elif re.fullmatch(phone_regex, email_or_phone):
        return "phone"
    else:
        raise ValidationError({
            "success":False,
            "message":"Email yoki Telefon raqam noto'g'ri"
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