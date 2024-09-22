from django.shortcuts import render
from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied
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