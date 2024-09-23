from django.contrib import admin
from .models import Post, PostComment, PostLike, CommentLike
# Register your models here.

class PostAdmin(admin.ModelAdmin):
    list_display = ['id','author','caption','created_at']
    search_fields = ['id','author__username','caption']
    

class PostCommentAdmin(admin.ModelAdmin):
    list_display = ['id','author','post','created_at']
    search_fields = ['id','author__username','post__caption']


class PostLikeAdmin(admin.ModelAdmin):
    list_display = ['id','author','post','created_at']
    search_fields = ['id','author__username']
    
    
class CommentLikeAdmin(admin.ModelAdmin):
    list_display = ['id','author','comment','created_at']
    search_fields = ['id','author__username']
    

admin.site.register(Post, PostAdmin)
admin.site.register(PostComment, PostCommentAdmin)
admin.site.register(PostLike, PostLikeAdmin)
admin.site.register(CommentLike, CommentLikeAdmin)
    