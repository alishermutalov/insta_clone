from django.urls import path
from .views import CreateUserAPIView, VerifyAPIView, GetNewVerificationCodeAPIView, \
    UpdateUserInfoAPIView, SetOrUpdateUserPhotoAPIView, LoginAPIView,LoginRefreshAPIView

urlpatterns = [
    path('login/', LoginAPIView.as_view()),
    path('login/refresh/', LoginRefreshAPIView.as_view()),
    path('signup/', CreateUserAPIView.as_view()),
    path('verify/', VerifyAPIView.as_view()),
    path('verify/resend/', GetNewVerificationCodeAPIView.as_view()),
    path('update-user/', UpdateUserInfoAPIView.as_view()),
    path('update-user-photo/', SetOrUpdateUserPhotoAPIView.as_view()),
]
