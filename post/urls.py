from django.urls import path
from .views import PostListAPIView,  PostCreateAPIView, PostRetrieveUpdateDestroyAPIView,\
    PostCommentListAPIView, PostCommentCreateAPIView, PostCommentDeleteAPIView,\
        PostLikeListAPIView,PostCommentLikeListAPIView, PostCommentDetailAPIView,\
            PostLikeCreateAPIView, PostCommentLikeCreateAPIView, PostCommentLikeDeleteAPIView,\
                PostLikeDeleteAPIView


urlpatterns = [
    path('list/',PostListAPIView.as_view()),
    path('create/',PostCreateAPIView.as_view()),
    path('<uuid:pk>/',PostRetrieveUpdateDestroyAPIView.as_view()),
    path('<uuid:pk>/comments/',PostCommentListAPIView.as_view()),
    path('<uuid:pk>/comments/create/',PostCommentCreateAPIView.as_view()),
    path('comments/delete/<uuid:pk>/', PostCommentDeleteAPIView.as_view()),
    path('<uuid:pk>/likes/',PostLikeListAPIView.as_view()),
    path('<uuid:pk>/likes/create/',PostLikeCreateAPIView.as_view()), #pk is post-id
    path('<uuid:pk>/likes/delete/',PostLikeDeleteAPIView.as_view()), #pk is like_id
    path('comments/<uuid:pk>/',PostCommentDetailAPIView.as_view()),
    path('comments/<uuid:pk>/likes/',PostCommentLikeListAPIView.as_view()),
    path('comments/<uuid:pk>/likes/create/', PostCommentLikeCreateAPIView.as_view()), #pk is comment_id
    path('comments/<uuid:pk>/likes/delete/', PostCommentLikeDeleteAPIView.as_view()), #pk is like_id
]
