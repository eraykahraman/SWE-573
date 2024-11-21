
from django.contrib import admin
from .models import Post, PostImage, Tag,Comment

# Inline for managing PostImage directly within the Post admin
class PostImageInline(admin.TabularInline):
    model = PostImage
    extra = 1  # Number of empty image fields displayed by default

# Admin for Post
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'created_at')
    search_fields = ('name', 'description', 'material', 'size', 'shape', 'color', 'found_location')
    list_filter = ('created_at', 'author')
    filter_horizontal = ('tags',)  # Allow easy tag selection in the admin
    inlines = [PostImageInline]  # Add inline images to the Post admin

# Admin for Tag
@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('wikidata_id', 'label')
    search_fields = ('wikidata_id', 'label')

# Admin for PostImage
@admin.register(PostImage)
class PostImageAdmin(admin.ModelAdmin):
    list_display = ('post', 'image')
    list_filter = ('post',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('content', 'author', 'post', 'created_at', 'total_likes', 'total_dislikes')
    search_fields = ('content', 'author__username', 'post__name')
    list_filter = ('created_at', 'post')
    readonly_fields = ('created_at',)

    def total_likes(self, obj):
        return obj.likes.count()

    def total_dislikes(self, obj):
        return obj.dislikes.count()