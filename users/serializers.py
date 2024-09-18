from rest_framework import exceptions
from django.db.models import Q
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import User, VIA_EMAIL, VIA_PHONE, NEW, CODE_VERIFIED, DONE, PHOTO_STEP
from base_app.utils import check_email_or_phone, send_async_mail, send_sms_verification_code


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
        print('data: ', data)
        return data
    
    def to_representation(self, instance):
        print(instance)
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
    