from django.db import models
from django.contrib.auth.models import User

class Post(models.Model):
    title = models.CharField(max_length=200, blank=False, null=True)  # Mandatory field
    image = models.ImageField(upload_to='post_images/', blank=False,null=True)   # Mandatory field
    description = models.TextField(blank=False)                        # Mandatory field
    property1 = models.CharField(max_length=100, blank=True, null=True)
    property2 = models.CharField(max_length=100, blank=True, null=True)
    property3 = models.CharField(max_length=100, blank=True, null=True)
    property4 = models.CharField(max_length=100, blank=True, null=True)
    property5 = models.CharField(max_length=100, blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Comment(models.Model):
    post = models.ForeignKey(Post, related_name="comments", on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author} on {self.post}"
