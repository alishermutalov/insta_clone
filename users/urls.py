from django.urls import path
from .views import CreateUserAPIView, VerifyAPIView, GetNewVerificationCodeAPIView, \
    UpdateUserInfoAPIView, SetOrUpdateUserPhotoAPIView, LoginAPIView, LoginRefreshAPIView,\
        LogoutAPIView, ForgotPasswordAPIView, ResetUserPasswordAPIView

urlpatterns = [
    path('login/', LoginAPIView.as_view()),
    path('login/refresh/', LoginRefreshAPIView.as_view()),
    path('logout/', LogoutAPIView.as_view()),
    path('signup/', CreateUserAPIView.as_view()),
    path('verify/', VerifyAPIView.as_view()),
    path('verify/resend/', GetNewVerificationCodeAPIView.as_view()),
    path('update-user/', UpdateUserInfoAPIView.as_view()),
    path('update-user-photo/', SetOrUpdateUserPhotoAPIView.as_view()),
    path('forgot-password/', ForgotPasswordAPIView.as_view()),
    path('reset-password/', ResetUserPasswordAPIView.as_view()),
]
