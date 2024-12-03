from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import Post
from .forms import PostForm, CommentForm
from django.http import JsonResponse
import requests
from .models import Tag,Comment
import json
from django.contrib import messages
from django.http import HttpResponse

# Home view: Display all posts
def home(request):
    # Get all posts for everyone, ordered by newest first
    posts = Post.objects.all().order_by('-created_at')
    
    if request.user.is_authenticated:
        user_posts = Post.objects.filter(author=request.user)
        # Get comments for each post
        for post in posts:
            post.comment_list = Comment.objects.filter(post=post).order_by('-created_at')
        return render(request, 'whatisthis/user_dashboard.html', {
            'posts': posts,
            'comment_form': CommentForm(),
            'user_posts': user_posts,
        })
    else:
        # Get comments for each post for non-authenticated users too
        for post in posts:
            post.comment_list = Comment.objects.filter(post=post).order_by('-created_at')
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
            if 'image' not in request.FILES:
                messages.error(request, 'Please upload an image for your post.')
                return render(request, 'whatisthis/create_post.html', {'form': form})
            
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            
            # Handle tags
            tags_data = request.POST.get('selected_tags')
            if tags_data:
                tags = json.loads(tags_data)
                for tag_data in tags:
                    tag, created = Tag.objects.get_or_create(
                        wikidata_id=tag_data['wikidata_id'],
                        defaults={'label': tag_data['label']}
                    )
                    post.tags.add(tag)
            
            messages.success(request, 'Post created successfully!')
            return redirect('home')
        else:
            # Form is invalid - it will be re-rendered with errors
            return render(request, 'whatisthis/create_post.html', {'form': form})
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

@login_required
def profile (request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=request.user.profile)
    
    context = {
        'form': form,
        'user_posts': Post.objects.filter(author=request.user)
    }
    return render(request, 'whatisthis/profile.html', context)

@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
            messages.success(request, 'Comment added successfully!')
        else:
            messages.error(request, 'Error adding comment.')
    return redirect('home')

