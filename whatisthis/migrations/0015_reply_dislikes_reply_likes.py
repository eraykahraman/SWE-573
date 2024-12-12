# Generated by Django 4.2.16 on 2024-12-05 17:44

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('whatisthis', '0014_reply_parent_alter_reply_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='reply',
            name='dislikes',
            field=models.ManyToManyField(blank=True, related_name='reply_dislikes', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='reply',
            name='likes',
            field=models.ManyToManyField(blank=True, related_name='reply_likes', to=settings.AUTH_USER_MODEL),
        ),
    ]