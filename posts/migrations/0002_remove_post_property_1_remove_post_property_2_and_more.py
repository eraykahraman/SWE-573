# Generated by Django 5.1.3 on 2024-11-09 21:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='property_1',
        ),
        migrations.RemoveField(
            model_name='post',
            name='property_2',
        ),
        migrations.RemoveField(
            model_name='post',
            name='property_3',
        ),
        migrations.RemoveField(
            model_name='post',
            name='property_4',
        ),
        migrations.RemoveField(
            model_name='post',
            name='property_5',
        ),
        migrations.AddField(
            model_name='post',
            name='property1',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='post',
            name='property2',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='post',
            name='property3',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='post',
            name='property4',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='post',
            name='property5',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='post',
            name='image',
            field=models.ImageField(null=True, upload_to='post_images/'),
        ),
        migrations.AlterField(
            model_name='post',
            name='title',
            field=models.CharField(max_length=200, null=True),
        ),
    ]
