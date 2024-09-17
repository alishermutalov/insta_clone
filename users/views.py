from django.shortcuts import render
from datetime import datetime
from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from .serializers import SignUpSerializer
from .models import User, DONE, CODE_VERIFIED, PHOTO_STEP



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