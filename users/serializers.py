from typing import Any, Dict
from django.db.models import Q
from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import PermissionDenied
from rest_framework import serializers
from rest_framework.generics import get_object_or_404
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.tokens import AccessToken

from .models import User, VIA_EMAIL, VIA_PHONE, NEW, CODE_VERIFIED, DONE, PHOTO_DONE
from base_app.utils import check_email_or_phone, send_async_mail, send_sms_verification_code, check_username


class SignUpSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    
    def __init__(self, *args, **kwargs):
        super(SignUpSerializer, self).__init__(*args, **kwargs)
        self.fields['email_or_phone_number'] = serializers.CharField(required=False)
    
    class Meta:
        model = User
        fields = (
            'id',
            'auth_type',
            'auth_status',
        )
        extra_kwargs = {
            'auth_type':{'read_only':True, 'required':False},
            'auth_status':{'read_only':True, 'required':False},
        }#it's same thing with id(on top of class ) parameter
    
    def create(self, validated_data):
        user = super(SignUpSerializer, self).create(validated_data)
        if user.auth_type == VIA_EMAIL:
            code = user.create_verification_code(VIA_EMAIL)
            print(code)
            send_async_mail(
                "Instagram authentication",
                f"Your confirmation code: {code}",
                [user.email,]
            )
        elif user.auth_type == VIA_PHONE:
            code = user.create_verification_code(VIA_EMAIL)
            #send_sms_verification_code(user.phone_number, code) #It's not working if you don't have twilio subscription!
            print(code)
        user.save()
        return user
        
    def validate(self, data):
        super(SignUpSerializer, self).validate(data)
        data = self.auth_validate(data)
        return data
    
    @staticmethod
    def auth_validate(data):
        print(data)
        user_input = str(data.get('email_or_phone_number')).lower()
        input_type = check_email_or_phone(user_input)
        if input_type=='email':
            if User.objects.filter(email=user_input).exists():
                raise ValidationError({
                    'success': False,
                    'message': 'This email is already taken!'
                })
            data = {
                'email':user_input,
                'auth_type': VIA_EMAIL
            }
        elif input_type=='phone':
            if User.objects.filter(phone_number=user_input).exists():
                raise ValidationError({
                    'success': False,
                    'message': 'This phone number is already taken!'
                })
            data = {
                'phone_number':user_input,
                'auth_type':VIA_PHONE
            }
        else:
            data = {
                'success':False,
                'message':'You must send email addres or phone number!'
            }
            raise ValidationError(data)
        
        return data
    
    def to_representation(self, instance):
        data = super(SignUpSerializer, self).to_representation(instance)
        data.update(instance.token())
        return data
    
    
class UpdateUserInfoSerializer(serializers.Serializer):
    first_name = serializers.CharField(write_only=True, required=True)
    last_name = serializers.CharField(write_only=True, required=True)
    username = serializers.CharField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)
    
    def validate(self, data):
        password = data.get('password', None)
        confirm_password = data.get('confirm_password', None)
        if password != confirm_password:
            raise ValidationError({
                'message':'Password and Confirmation password do not match'
            })
        if password:
           validate_password(password)
        
        return data
    
    def validate_username(self, username):
        if len(username)<4 or len(username)>32:
            raise ValidationError({
                'message':'Username must be more than 4 characters and less than 32 characters'
            })
        if username.isdigit():
            raise ValidationError({
                'message':'This username is entirely numeric'
            })
        
        return username
            
    def validate_first_name(self, first_name):
        if len(first_name)<1 or len(first_name)>50:
            raise ValidationError({
                'message':'First name must be more than 4 characters and less than 32 characters'
            })
        if first_name.isdigit():
            raise ValidationError({
                'message':'This first name is entirely numeric'
            })
        
        return first_name   
    
    def validate_last_name(self, last_name):
        if len(last_name)<1 or len(last_name)>50:
            raise ValidationError({
                'message':'last name must be more than 4 characters and less than 32 characters'
            })
        if last_name.isdigit():
            raise ValidationError({
                'message':'This last name is entirely numeric'
            })
        
        return last_name 
    
    def update(self, instance, validated_data):
        instance.username = validated_data.get('username',instance.username)
        instance.first_name = validated_data.get('first_name',instance.first_name)
        instance.last_name = validated_data.get('last_name',instance.last_name)
        instance.password = validated_data.get('password',instance.password)
        if validated_data.get('password'):
            instance.set_password(validated_data.get('password'))
        if instance.auth_status == CODE_VERIFIED:
            instance.auth_status = DONE
        instance.save()
        
        return instance


class SetUserPhotoSerializer(serializers.Serializer):
    photo = serializers.ImageField()
    
    def validate_photo(self, data):
        file_size = data.size
        max_size = 10 * 1024 * 1024 #10MB
        if file_size>max_size:
            ValidationError({
                'success':False,
                'message':'Image file is too large. Maximum allowed size is 10MB.'
            })
        return data
    
    def update(self, instance, validated_data):
        instance.photo = validated_data.get('photo', instance.photo)
        if instance.auth_status == DONE and instance.photo:
            instance.auth_status = PHOTO_DONE
        instance.save()
        return instance
    

class LoginSerializer(TokenObtainPairSerializer):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fields['user_input'] = serializers.CharField(required=True)
        self.fields['username'] = serializers.CharField(required=False, read_only=True)
        
    def auth_validate(self, data):
        user_input = data.get('user_input')
        
        if check_email_or_phone(user_input)=="email":
            try:
                user = User.objects.get(email__iexact=user_input)
                username = user.username
            except:
                raise ValidationError({
                    'message':'No user found for this email'
                })
        elif check_email_or_phone(user_input)=="phone":
            try:
                user = User.objects.get(phone_number=user_input)
                username = user.username
            except Exception as e:
                raise ValidationError({
                    'message':'No user found for this phone number'
                })
        elif check_email_or_phone(user_input)=="username":
            try:
                user = User.objects.get(username=user_input)
                username = user.username
            except:
                raise ValidationError({
                    'message':'No user found for this username'
                })
        else:
                raise ValidationError({
                    'message':'No user found. Check your login data or Register now!'
                })
        
        authentication_kwargs = {
            self.username_field : username,
            "password":data["password"]
        }    
        
        if user is not None and user.auth_status in [CODE_VERIFIED, NEW]:
            raise ValidationError({
                'message': 'You are not fully registered yet!'
            })
        user = authenticate(**authentication_kwargs)
        if user is not None:
            self.user = user
        else:
            raise ValidationError({
                'message':'Sorry, your username or password incorrect, please try again!'
            })
        
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, str]:
        self.auth_validate(attrs)
        if self.user.auth_status not in [DONE, PHOTO_DONE]:
            raise PermissionDenied("You can't login. You don't have permission.")
        attrs = self.user.token()
        attrs['auth_status'] = self.user.auth_status
        attrs['full_name'] = self.user.full_name
        return attrs
        
        
class RefreshTokenSerializer(TokenRefreshSerializer):
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, str]:
        data = super().validate(attrs)
        acces_token_instance = AccessToken(data["access"])
        user_id = acces_token_instance['user_id']
        user = get_object_or_404(User, id=user_id)
        update_last_login(None, user)
        return data
    
class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    
    
class ForgotPasswordSerializer(serializers.Serializer):
    email_or_phone = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        
        email_or_phone = attrs.get('email_or_phone')
        if email_or_phone is None:
            raise ValidationError({
                'message':'You must enter email or phone number'
            })
        user = User.objects.filter(Q(phone_number=email_or_phone) | Q(email__iexact=email_or_phone))
        if not user.exists():
            raise NotFound(detail="User not found")
        
        attrs['user'] = user.first()
        return attrs
    
    
class ResetUserPasswordSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    password = serializers.CharField(min_length=8, required=True, write_only=True)
    confirm_password = serializers.CharField(min_length=8, required=True, write_only=True)
    
    class Meta:
        model = User
        fields = [
            'id',
            'password',
            'confirm_password'
        ]
    
    def validate(self, attrs):
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')
        if password != confirm_password:
            raise ValidationError({
                'message':'Your password and confirmation password are not same'
            })
        if password:
            validate_password(password)
        return attrs
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password') # .pop() Retrieves and removes 'password' from validated_data
        instance.set_password(password)
        instance.save()
        return super().update(instance, validated_data)