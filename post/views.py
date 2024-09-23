from django.db.models import Q
from rest_framework.generics import ListAPIView, CreateAPIView, \
    RetrieveUpdateDestroyAPIView, DestroyAPIView, RetrieveAPIView
from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework.response import Response

from base_app.custom_pagination import CustomPagination
from .models import Post, PostComment, PostLike, CommentLike
from . import serializers
# Create your views here.

class PostListAPIView(ListAPIView):
    permission_classes = [permissions.AllowAny,]
    serializer_class = serializers.PostSerializer
    pagination_class = CustomPagination
    queryset = Post.objects.all()
    
    
class PostCreateAPIView(CreateAPIView):
    permission_classes = [permissions.IsAuthenticated,]
    serializer_class = serializers.PostSerializer
    
    def get_object(self):
        return self.request.user
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
        
        
class PostRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,]
    serializer_class = serializers.PostSerializer
    queryset = Post.objects.all()
    
    def put(self, request, *args, **kwargs):
        post = self.get_object()
        
        if post.author != self.request.user:
            raise PermissionDenied("You do not have permission to update this post")
        serializer = self.serializer_class(post,data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response({
            "success":True,
            "message":"Post successfuly updated",
            "data":serializer.data
        })
        
    def delete(self, request, *args, **kwargs):
        post = self.get_object()
        if post.author != self.request.user:
            raise PermissionDenied("You do not have permission to delete this post")
        post.delete()
        return Response({
            "success":True,
            "message":"Post successfuly deleted",
            
        })
        
        
class PostCommentListAPIView(ListAPIView):
    serializer_class = serializers.CommentSerializer
    permission_classes = [permissions.AllowAny,]
    
    def get_queryset(self):
        post_id = self.kwargs['pk']
        
        queryset = PostComment.objects.filter(post__id=post_id, parent=None)
        return queryset
    
    
class PostCommentCreateAPIView(CreateAPIView):
    serializer_class = serializers.CommentSerializer
    permission_classes = [permissions.IsAuthenticated,]
    pagination_class = CustomPagination
    
    def perform_create(self, serializer):
        post_id = self.kwargs['pk']
        serializer.save(author=self.request.user, post_id=post_id)
        
        
class PostCommentDeleteAPIView(DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated,]
    
    def get_queryset(self):
        return PostComment.objects.filter(author=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        try:
            like = self.get_object()  
            like.delete()
            return Response({
                "success": True,
                "message": "Comment successfully deleted"
            })
        except PostLike.DoesNotExist:
            return Response({
                "success": False,
                "message": "Comment not found or permission denied"
            }, status=404)
        
        
class PostCommentDetailAPIView(RetrieveAPIView):
    permission_classes = [permissions.AllowAny,]
    serializer_class = serializers.CommentSerializer
    queryset = PostComment.objects.all()
        
        
class PostLikeListAPIView(ListAPIView):
    serializer_class = serializers.PostLikeSerializer
    permission_classes = [permissions.AllowAny,]
    pagination_class = CustomPagination
    
    def get_queryset(self):
        post_id = self.kwargs['pk']
        return PostLike.objects.filter(post_id=post_id)


class PostLikeCreateAPIView(CreateAPIView):
    serializer_class = serializers.PostLikeSerializer
    permission_classes = [permissions.IsAuthenticated,]
    
    def perform_create(self, serializer):
        try:
            post = Post.objects.get(id=self.kwargs['pk'])
            if not PostLike.objects.filter(author=self.request.user, post=post).exists():
                serializer.save(author=self.request.user, post=post)
        except NotFound:
            raise NotFound("This post unavailable!")
    

class PostLikeDeleteAPIView(DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated,]
    
    def get_queryset(self):
        return PostLike.objects.filter(author=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        try:
            like = self.get_object()  # Automatically filtered by the current user in `get_queryset()`
            like.delete()
            return Response({
                "success": True,
                "message": "Like successfully deleted"
            })
        except PostLike.DoesNotExist:
            return Response({
                "success": False,
                "message": "Like not found or permission denied"
            }, status=404)


class PostCommentLikeListAPIView(ListAPIView):
    serializer_class = serializers.CommentLikeSerializer
    permission_classes = [permissions.AllowAny,]
    pagination_class = CustomPagination
    
    def get_queryset(self):
        comment_id = self.kwargs['pk']
        return CommentLike.objects.filter(comment_id=comment_id)
    

class PostCommentLikeCreateAPIView(CreateAPIView):
    serializer_class = serializers.CommentLikeSerializer
    permission_classes = [permissions.IsAuthenticated,]
    
    def perform_create(self, serializer):
        try:
            comment = PostComment.objects.get(id=self.kwargs['pk'])
            if not CommentLike.objects.filter(author=self.request.user, comment=comment).exists():
                serializer.save(author=self.request.user, comment=comment)
        except NotFound:
            raise NotFound("This comment unavailable!")
        

class PostCommentLikeDeleteAPIView(DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated,]
   
    def get_queryset(self):
        return CommentLike.objects.filter(author=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        try:
            like = self.get_object()
            like.delete()
            return Response({
                "success": True,
                "message": "Like successfully deleted"
            })
        except PostLike.DoesNotExist:
            return Response({
                "success": False,
                "message": "Like not found or permission denied"
            }, status=404)