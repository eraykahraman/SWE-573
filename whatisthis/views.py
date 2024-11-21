from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import Post
from .forms import PostForm, CommentForm
from django.http import JsonResponse
import requests
from .models import Tag,Comment
import json

# Home view: Display all posts
"""def home(request):
    posts = Post.objects.all()
    return render(request, 'whatisthis/home.html', {'posts': posts})"""

""" burdan devam et kaçarsa
def home(request):
    posts = Post.objects.all()

    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('login')  # Redirect non-logged-in users to the login page
        post_id = request.POST.get('post_id')
        post = get_object_or_404(Post, id=post_id)
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect('home')  # Reload the page

    return render(request, 'whatisthis/home.html', {
        'posts': posts,
        'comment_form': CommentForm()
    })
"""

# Home view: Display all posts and handle comment creation
def home(request):
    posts = Post.objects.all()

    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('login')  # Redirect non-logged-in users to the login page
        post_id = request.POST.get('post_id')
        post = get_object_or_404(Post, id=post_id)
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect('home')  # Reload the page

    for post in posts:
        for comment in post.comments.all():
            comment.like_count = comment.total_likes()
            comment.dislike_count = comment.total_dislikes()

    return render(request, 'whatisthis/home.html', {
        'posts': posts,
        'comment_form': CommentForm()
    })




@login_required
def like_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user in comment.likes.all():
        comment.likes.remove(request.user)
    else:
        comment.likes.add(request.user)
        comment.dislikes.remove(request.user)  # Ensure no conflict with dislikes

    return JsonResponse({
        'likes': comment.likes.count(),
        'dislikes': comment.dislikes.count()
    })

# Dislike a comment
@login_required
def dislike_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user in comment.dislikes.all():
        comment.dislikes.remove(request.user)
    else:
        comment.dislikes.add(request.user)
        comment.likes.remove(request.user)  # Ensure no conflict with likes

    return JsonResponse({
        'likes': comment.likes.count(),
        'dislikes': comment.dislikes.count()
    })
# Create Post view: Only accessible by logged-in users

""""
@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            form.save_m2m()  # Save Many-to-Many relationships like tags
            return redirect('home')
    else:
        form = PostForm()
    return render(request, 'whatisthis/create_post.html', {'form': form})"""

@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()

            # Process selected tags
            selected_tags = request.POST.get('selected_tags', '[]')
            selected_tags = json.loads(selected_tags)
            for tag_data in selected_tags:
                tag, created = Tag.objects.get_or_create(wikidata_id=tag_data['wikidata_id'], defaults={'label': tag_data['label']})
                post.tags.add(tag)

            return redirect('home')
    else:
        form = PostForm()
    return render(request, 'whatisthis/create_post.html', {'form': form})

def fetch_tags(request):
    query = request.GET.get('query', '')
    if not query:
        return JsonResponse([], safe=False)

    wikidata_url = f"https://www.wikidata.org/w/api.php?action=wbsearchentities&search={query}&language=en&format=json"
    response = requests.get(wikidata_url)
    if response.status_code == 200:
        data = response.json()
        tags = [{'wikidata_id': item['id'], 'label': item['label']} for item in data.get('search', [])]
        return JsonResponse(tags, safe=False)

    return JsonResponse([], safe=False)