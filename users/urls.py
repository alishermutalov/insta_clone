from django.urls import path
from .views import CreateUserAPIView, VerifyAPIView

urlpatterns = [
    path('signup/', CreateUserAPIView.as_view()),
    path('verify/', VerifyAPIView.as_view()),
    
]
