from rest_framework import serializers
from users.models import User
from .models import Post, PostComment, CommentLike, PostLike


class UserSearchSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField() 

    class Meta:
        model = User
        fields = ['username', 'full_name', 'photo']


class PostSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['author', 'caption', 'media']


class UserSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    
    class Meta:
        model = User
        fields = ['id','username','photo']


class PostSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    author = UserSerializer(read_only=True)
    post_likes = serializers.SerializerMethodField('get_post_likes_count')
    post_comments = serializers.SerializerMethodField('get_post_comments_count')
    request_user_liked = serializers.SerializerMethodField('get_request_user_liked')
    
    class Meta:
        model = Post
        fields = ['id','author','media','caption','created_at','post_likes', 'post_comments','request_user_liked']
        
    def get_post_likes_count(self, obj):
        return obj.post_likes.count()
    
    def get_post_comments_count(self, obj):
        return obj.comments.count()
    
    def get_request_user_liked(self, obj):
        request = self.context.get('request', None)
        if request and request.user.is_authenticated:
            try:
                PostLike.objects.get(post=obj, author=request.user)
                return True
            except PostLike.DoesNotExist:
                return False
            

class CommentSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    author = UserSerializer(read_only=True)
    replies = serializers.SerializerMethodField('get_comment_replies')
    request_user_liked = serializers.SerializerMethodField('get_request_user_liked')
    comment_likes_count = serializers.SerializerMethodField('get_comment_likes_count')
    
    class Meta:
        model = PostComment
        fields = ['id','author','comment','parent','created_at','replies','request_user_liked','comment_likes_count']
        
    def get_comment_replies(self, obj):
        if obj.child.exists():
            serializers = self.__class__(obj.child.all(), many=True, context=self.context)
            return serializers.data
        else:
            return None
        
    def get_request_user_liked(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return obj.likes.filter(author=user).exists()
        else:
            return False
        
    def get_comment_likes_count(self,obj):
        return obj.likes.count()
    

class CommentLikeSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    author = UserSerializer(read_only=True)
    comment = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = CommentLike
        fields = ['id','author','comment']
        
        
class PostLikeSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    author = UserSerializer(read_only=True)
    post = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = PostLike
        fields = ['id','author','post']
               
               
