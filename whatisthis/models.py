from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Tag(models.Model):
    wikidata_id = models.CharField(max_length=20, unique=True, verbose_name="Wikidata ID")
    label = models.CharField(max_length=100, blank=True, null=True, verbose_name="Tag Label")

    def __str__(self):
        return self.label or self.wikidata_id

class Post(models.Model):
    name = models.CharField(max_length=200, verbose_name="Object Name")
    description = models.TextField(verbose_name="Description")
    image = models.ImageField(upload_to='images/', blank=True, null=True, verbose_name="Main Image of the Object")  # Add this field
    material = models.CharField(max_length=100, blank=True, null=True, verbose_name="Material")
    size = models.CharField(max_length=100, blank=True, null=True, verbose_name="Size")
    shape = models.CharField(max_length=100, blank=True, null=True, verbose_name="Shape")
    text_and_language = models.CharField(max_length=200, blank=True, null=True, verbose_name="Text and Language")
    found_location = models.CharField(max_length=200, blank=True, null=True, verbose_name="Found Location")
    color = models.CharField(max_length=100, blank=True, null=True, verbose_name="Color")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts", null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    tags = models.ManyToManyField(Tag, related_name="posts", blank=True)

    def __str__(self):
        return self.name

class PostImage(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to='images/')

    def __str__(self):
        return f"Image for {self.post.name}"



class Comment(models.Model):
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(verbose_name="Comment Content")
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='comment_likes', blank=True)
    dislikes = models.ManyToManyField(User, related_name='comment_dislikes', blank=True)

    def total_likes(self):
        return self.likes.count()

    def total_dislikes(self):
        return self.dislikes.count()

    def __str__(self):
        return f"Comment by {self.author.username} on {self.post.name}"
    


    