from django.shortcuts import render
from datetime import datetime
from rest_framework.generics import CreateAPIView, UpdateAPIView
from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from .serializers import SignUpSerializer, UpdateUserInfoSerializer, \
    SetUserPhotoSerializer, LoginSerializer, RefreshTokenSerializer,\
        LogoutSerializer, ForgotPasswordSerializer, ResetUserPasswordSerializer
from .models import User, DONE, CODE_VERIFIED, VIA_EMAIL, VIA_PHONE
from base_app.utils import send_async_mail, send_sms_verification_code, check_email_or_phone



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
        

class UpdateUserInfoAPIView(UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated,]
    serializer_class = UpdateUserInfoSerializer
    http_method_names = ['patch', 'put'] 
    
    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        super(UpdateUserInfoAPIView, self).update(request, *args, **kwargs)
        return Response({
            'succss':True,
            'message':'User information updated successfully!'
        })
        
    def partial_update(self, request, *args, **kwargs):
        super(UpdateUserInfoAPIView, self).partial_update(request, *args, **kwargs)
        return Response({
            'succss':True,
            'message':'User information updated successfully!'
        })
        
        
class SetOrUpdateUserPhotoAPIView(UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated,]
    serializer_class = SetUserPhotoSerializer
    
    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        return Response({
            'success':True,
            'message':'User Photo Set Successfully!'
        })
        
        
class LoginAPIView(TokenObtainPairView):
    serializer_class = LoginSerializer
    

class LoginRefreshAPIView(TokenRefreshView):
    serializer_class = RefreshTokenSerializer
    
class LogoutAPIView(APIView):
    serializer_class = LogoutSerializer
    permission_classes = [permissions.IsAuthenticated,]
    
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data = self.request.data)
        serializer.is_valid(raise_exception=True)
        try:
            refresh_token = self.request.data['refresh']
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({
                'success':True,
                'message':'You successfully logged out!'
            }, status=205)
        except TokenError:
            return Response(status=400)
        
    
class ForgotPasswordAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = ForgotPasswordSerializer
    
    def post(self, requst, *args, **kwargs):
        serializer = self.serializer_class(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data.get('user')
        email_or_phone = serializer.validated_data.get('email_or_phone')
        if check_email_or_phone(email_or_phone)=="email":
            code = user.create_verification_code(VIA_EMAIL)
            send_async_mail("Insta: Forgot Password",
                            f"Insta. Code: {code}",
                            [email_or_phone,])
        elif check_email_or_phone(email_or_phone)=="phone":
            code = user.create_verification_code(VIA_PHONE)
            # send_sms_verification_code(email_or_phone, code) #If you don't have twilio subscription this function doesn't works
            print(code)
            
        return Response({
            'Success':True,
            'message':'Verification code sent successfully',
            'access': user.token()['access'],
            'refresh': user.token()['refresh_token']
        }, status=200)
      
        
class ResetUserPasswordAPIView(UpdateAPIView):
    serializer_class = ResetUserPasswordSerializer
    permission_classes = [permissions.IsAuthenticated,]
    http_method_names = ['pot', 'patch']
    
    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        user = self.get_object()
        
        return Response({
            'success':True,
            'message':'Your Password Changed Successfully!',
            'access': user.token()['access'],
            'refresh': user.token()['refresh_token']
        })