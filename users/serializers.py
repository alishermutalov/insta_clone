from rest_framework import exceptions
from django.db.models import Q
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import User, VIA_EMAIL, VIA_PHONE, NEW, CODE_VERIFIED, DONE, PHOTO_STEP
from base_app.utils import check_email_or_phone, send_async_mail


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
                    'message': 'This email is already taken'
                })
            data = {
                'email':user_input,
                'auth_type': VIA_EMAIL
            }
        elif input_type=='phone':
            if User.objects.filter(phone_number=user_input).exists():
                raise ValidationError({
                    'success': False,
                    'message': 'This phone number is already taken'
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
    