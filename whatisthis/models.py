from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.
class Tag(models.Model):
    wikidata_id = models.CharField(max_length=20, unique=True, verbose_name="Wikidata ID")
    label = models.CharField(max_length=100, blank=True, null=True, verbose_name="Tag Label")

    def __str__(self):
        return self.label or self.wikidata_id

class Post(models.Model):
    STATUS_CHOICES = (
        ('open', 'Open'),
        ('solved', 'Solved'),
    )
    name = models.CharField(max_length=200, verbose_name="Object Name")
    description = models.TextField(verbose_name="Description")
    image = models.ImageField(upload_to='post_images/', null=True, blank=False)
    material = models.CharField(max_length=100, blank=True, null=True, verbose_name="Material")
    size_x = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Length (cm)")
    size_y = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Width (cm)")
    size_z = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Height (cm)")
    shape = models.CharField(max_length=100, blank=True, null=True, verbose_name="Shape")
    text_and_language = models.CharField(max_length=200, blank=True, null=True, verbose_name="Text and Language")
    found_location = models.CharField(max_length=200, blank=True, null=True, verbose_name="Found Location")
    color = models.CharField(max_length=100, blank=True, null=True, verbose_name="Color")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts", null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    tags = models.ManyToManyField(Tag, related_name="posts", blank=True)
    status = models.CharField(
        max_length=10, 
        choices=STATUS_CHOICES, 
        default='open',
        editable=False
    )

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
    

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    occupation = models.CharField(max_length=100, blank=True)
    about_me = models.TextField(max_length=500, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', default='profile_pics/default.jpg')

    def __str__(self):
        return f'{self.user.username} Profile'

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
    


    