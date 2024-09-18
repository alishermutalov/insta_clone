from django.urls import path
from .views import CreateUserAPIView, VerifyAPIView, GetNewVerificationCodeAPIView, \
    UpdateUserInfoAPIView

urlpatterns = [
    path('signup/', CreateUserAPIView.as_view()),
    path('verify/', VerifyAPIView.as_view()),
    path('verify/resend/', GetNewVerificationCodeAPIView.as_view()),
    path('update-user/', UpdateUserInfoAPIView.as_view()),
    
]
