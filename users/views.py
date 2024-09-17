from django.shortcuts import render
from datetime import datetime
from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from .serializers import SignUpSerializer
from .models import User, DONE, CODE_VERIFIED, PHOTO_STEP, VIA_EMAIL, VIA_PHONE
from base_app.utils import send_async_mail, send_sms_verification_code



class CreateUserAPIView(CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny, )
    serializer_class = SignUpSerializer
    
class VerifyAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, requset, *args, **kwargs):
        user = self.request.user
        code = self.request.data.get('verification_code')
        
        self.check_verification_code(user, code)
        return Response(
            {
                'success':True,
                'auth_status':user.auth_status,
                'access':user.token()['access'],
                'refresh_token':user.token()['refresh_token'],
            }
        )
        
        
    @staticmethod
    def check_verification_code(user, code):
        verifications = user.user_verification_codes.filter(
            expiration_time__gte = datetime.now(), verification_code=code, is_confirmed=False)
        if not verifications.exists():
            raise ValidationError({
                'message':'Your verification code is invalid or has expired!'
            })
        else:
            verifications.update(is_confirmed=True)
        if user.auth_status not in DONE:
            user.auth_status = CODE_VERIFIED
            user.save()
        return True
    
class GetNewVerificationCodeAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated,]
    
    def get(self, request, *args, **kwargs):
        user = self.request.user
        self.check_verification(user)
        if user.auth_type == VIA_EMAIL:
            code = user.create_verification_code(VIA_EMAIL)
            send_async_mail('Verification Code',
                                  f'Your verification code: {code}',
                                  [user.email])
        elif user.auth_type == VIA_PHONE:
            code = user.create_verification_code(VIA_PHONE)
            # send_sms_verification_code(user.phone_number, code) #It's not working if you don't have twilio subscription!
            print(code)
        else:
            raise ValidationError({
                'message':'Your phone number or email incorrect'
            })
            
        return Response({
            'success':True,
            'message':'Your verification code has been resent!'
        })
        
    @staticmethod
    def check_verification(user):
        verifications = user.user_verification_codes.filter(
            expiration_time__gte = datetime.now(),  is_confirmed=False)
        if verifications.exists():
            raise ValidationError({
                'message':'Your code has been sent, please wait!'
            })
        