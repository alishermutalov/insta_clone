from django.db import models 
from django.db.models import UniqueConstraint
from django.core.validators import FileExtensionValidator, MaxLengthValidator
from users.models import User
from base_app.models import BaseModel



class Post(BaseModel):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    media = models.FileField(upload_to=f'posts/', 
                             validators=[FileExtensionValidator(
                                 allowed_extensions=['png', 'jpg', 'jpeg', 'gif', 'mp4', 'avi', 'mov', 'mkv','heic'])])
    caption = models.TextField(MaxLengthValidator(2000))
    
    def __str__(self) -> str:
        return f"{self.author} about: {self.caption}"

class PostComment(BaseModel):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    comment = models.TextField(MaxLengthValidator(2000))
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='child',
        null=True,
        blank=True                               
                               )
    """
    'parent' field is used for reply to comment.
    It works like this: 
            comment-1)  id=1                            
                        author_id = 1
                        post_id = 1
                        comment = Who is it?
                        parent = null
            reply to the comment-1 -> comment-2)
                        id=2
                        author_id = 2
                        post_id = 1
                        comment = He is popular actor in Uzbekistan
                        parent = 1 #The replied comment ID
    """
    
    def __str__(self) -> str:
        return f"{self.author} commented {self.comment}"

class PostLike(BaseModel):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_likes')
    
    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['author','post'],
                name='post_like'
            )
        ]
    
    def __str__(self) -> str:
        return f"{self.author}"    

    
class CommentLike(BaseModel):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.ForeignKey(PostComment, on_delete=models.CASCADE, related_name='likes')
    
    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['author','comment'],
                name='comment_like'
            )
        ]
    
    def __str__(self) -> str:
        return f"{self.author}"    
