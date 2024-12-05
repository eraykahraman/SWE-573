from django.urls import path
from . import views
from .views import home, create_post, fetch_tags

urlpatterns = [
    path('', home, name='home'),
    path('create/', create_post, name='create_post'),
    path('fetch-tags/', fetch_tags, name='fetch_tags'),
    path('post/<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path('toggle-status/<int:post_id>/', views.toggle_post_status, name='toggle_post_status'),
    path('profile/', views.profile, name='profile'),
    path('edit-post/<int:post_id>/', views.edit_post, name='edit_post'),
    path('comment/<int:comment_id>/upvote/', views.upvote_comment, name='upvote_comment'),
    path('comment/<int:comment_id>/downvote/', views.downvote_comment, name='downvote_comment'),
    path('search-tags/', views.search_tags, name='search_tags'),
    path('post/<int:post_id>/', views.post_detail, name='post_detail'),
]