from django.urls import path
from .views import PostListAPIView,  PostCreateAPIView, PostRetrieveUpdateDestroyAPIView


urlpatterns = [
    path('posts/',PostListAPIView.as_view()),
    path('posts/create/',PostCreateAPIView.as_view()),
    path('posts/<uuid:pk>/',PostRetrieveUpdateDestroyAPIView.as_view()),
]
