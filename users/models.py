from datetime import datetime,timedelta
import random
import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
from base_app.models import BaseModel
from rest_framework_simplejwt.tokens import RefreshToken

ORDINARY_USER, MANAGER, ADMIN = "ordinary_user", "manager", "admin"
VIA_EMAIL, VIA_PHONE = "via_email", "via_phone"
NEW, CODE_VERIFIED, DONE, PHOTO_DONE= "new", "code_verified","done", "photo_done"


class User(AbstractUser, BaseModel):
    USER_ROLES = (
        (ORDINARY_USER, ORDINARY_USER),
        (MANAGER, MANAGER),
        (ADMIN, ADMIN),
    )
    
    AUTH_TYPES = (
        (VIA_EMAIL, VIA_EMAIL),
        (VIA_PHONE, VIA_PHONE),  
    )
    
    AUTH_STATE = (
        (NEW, NEW),
        (CODE_VERIFIED, CODE_VERIFIED),
        (DONE, DONE),
        (PHOTO_DONE, PHOTO_DONE),
    )
    user_role = models.CharField(max_length=30, choices=USER_ROLES, default=ORDINARY_USER)
    auth_type = models.CharField(max_length=30, choices=AUTH_TYPES)
    auth_status = models.CharField(max_length=30, choices=AUTH_STATE, default=NEW)
    email = models.EmailField(null=True, unique=True, blank=True)
    phone_number = models.CharField(max_length=16, null=True, blank=True, unique=True)
    photo = models.ImageField(upload_to="images/users/avatar/", null=True, blank=True, 
                              validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'heic'])])
    
    def __str__(self):
        return f"{self.username}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def create_verification_code(self, verification_type):
        verification_code = f"{random.randint(1000,9999)}"
        UserConfirmation.objects.create(
            user_id = self.id,
            verification_type = verification_type,
            verification_code = verification_code,
        )
        return verification_code
        
    def check_username(self):
        if not self.username:
            temp_username = f"insta-{ uuid.uuid4().__str__().split('-')[-1] }"
            while True:
                try:
                    if not User.objects.filter(username=temp_username).exists():
                        self.username = temp_username
                        break  
                    else:
                        temp_username += str(random.randint(0, 9))
                except Exception as e:
                    raise e
    
    def check_email(self):
        if self.email:
            email = self.email.lower()
            self.email = email
        
    def check_pass(self):
        if not self.password:
            password = f"password-{uuid.uuid4().__str__().split('-')[-1]}"
            self.password = password
            
    def hashing_password(self):
        if not self.password.startswith('pbkdf2_sha256'):
            self.set_password(self.password)
            
    def token(self):
        refresh = RefreshToken.for_user(self)
        return {
            "access":str(refresh.access_token),
            "refresh_token":str(refresh)
        }
    
    def clean(self) -> None:
        self.check_email()
        self.check_username()
        self.check_pass()
        self.hashing_password()
    
    def save(self, *args, **kwargs) -> None:
        
        self.clean()
        super(User, self).save(*args, **kwargs)
    
    
EMAIL_EXPIRE = 5
PHONE_EXPIRE = 2


class UserConfirmation(BaseModel):
    VERIFICATION_TYPES = (
        (VIA_EMAIL, VIA_EMAIL),
        (VIA_PHONE, VIA_PHONE)
    )
    
    verification_code = models.CharField(max_length=4, )
    verification_type = models.CharField(max_length=30, choices=VERIFICATION_TYPES)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_verification_codes')
    expiration_time = models.DateTimeField(null=True)
    is_confirmed = models.BooleanField(default=False)
    
    def __str__(self):
        return f"insta-{self.user}"
    
    def save(self, *args, **kwargs):
        if self.verification_type == VIA_EMAIL:
            self.expiration_time = datetime.now() + timedelta(minutes=EMAIL_EXPIRE)
        else:
            self.expiration_time = datetime.now() + timedelta(minutes=PHONE_EXPIRE)
        super(UserConfirmation, self).save(*args, **kwargs)
    