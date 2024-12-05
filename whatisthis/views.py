from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from .models import Post, Tag, Comment
from django.contrib import messages
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from .forms import PostForm, CommentForm, ProfileUpdateForm
import requests
import json

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
        tags_data = request.POST.get('selected_tags')
        
        # Check if tags are provided
        if not tags_data:
            messages.error(request, 'Please add at least one tag to your post.')
            return render(request, 'whatisthis/create_post.html', {'form': form})

        if form.is_valid():
            if 'image' not in request.FILES:
                messages.error(request, 'Please upload an image for your post.')
                return render(request, 'whatisthis/create_post.html', {'form': form})
            
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            
            try:
                # Add tags
                tags = json.loads(tags_data)
                if not tags:  # Additional server-side validation
                    raise ValueError("No tags provided")
                    
                for tag_data in tags:
                    tag, created = Tag.objects.get_or_create(
                        wikidata_id=tag_data['wikidata_id'],
                        defaults={'label': tag_data['label']}
                    )
                    post.tags.add(tag)
                
                messages.success(request, 'Post created successfully!')
                return redirect('home')
            except (json.JSONDecodeError, ValueError) as e:
                post.delete()  # Delete the post if tag creation fails
                messages.error(request, 'Please add at least one tag to your post.')
                return render(request, 'whatisthis/create_post.html', {'form': form})
        else:
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
def profile(request):
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
        'user_posts': Post.objects.filter(author=request.user).order_by('-created_at')
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

@login_required
@require_POST
def toggle_post_status(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
        # Check if the user is the post owner
        if request.user == post.author:
            # Toggle the status
            post.status = 'solved' if post.status == 'open' else 'open'
            post.save()
            return JsonResponse({'status': post.status})
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    except Post.DoesNotExist:
        return JsonResponse({'error': 'Post not found'}, status=404)

@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    # Check if the user is the author of the post
    if request.user != post.author:
        return HttpResponseForbidden("You don't have permission to edit this post")
        
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        tags_data = request.POST.get('selected_tags')
        
        # Check if tags are provided
        if not tags_data:
            messages.error(request, 'Please add at least one tag to your post.')
            return render(request, 'whatisthis/edit_post.html', {
                'form': form,
                'post': post,
                'existing_tags': json.dumps([])
            })

        if form.is_valid():
            post = form.save()
            
            try:
                # Clear existing tags
                post.tags.clear()
                # Add new tags
                tags = json.loads(tags_data)
                if not tags:  # Additional server-side validation
                    raise ValueError("No tags provided")
                    
                for tag_data in tags:
                    tag, created = Tag.objects.get_or_create(
                        wikidata_id=tag_data['wikidata_id'],
                        defaults={'label': tag_data['label']}
                    )
                    post.tags.add(tag)
                
                messages.success(request, 'Post updated successfully!')
                return redirect('home')
            except (json.JSONDecodeError, ValueError) as e:
                messages.error(request, 'Please add at least one tag to your post.')
                return render(request, 'whatisthis/edit_post.html', {
                    'form': form,
                    'post': post,
                    'existing_tags': json.dumps([])
                })
        else:
            messages.error(request, 'There was an error updating your post.')
    else:
        form = PostForm(instance=post)
    
    # Convert existing tags to JSON format for the template
    existing_tags = [{'wikidata_id': tag.wikidata_id, 'label': tag.label} 
                    for tag in post.tags.all()]
    
    return render(request, 'whatisthis/edit_post.html', {
        'form': form,
        'post': post,
        'existing_tags': json.dumps(existing_tags)
    })

@login_required
def upvote_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    
    if request.user in comment.likes.all():
        comment.likes.remove(request.user)
    else:
        comment.likes.add(request.user)
        comment.dislikes.remove(request.user)
    
    return JsonResponse({
        'likes': comment.total_likes(),
        'dislikes': comment.total_dislikes()
    })

@login_required
def downvote_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    
    if request.user in comment.dislikes.all():
        comment.dislikes.remove(request.user)
    else:
        comment.dislikes.add(request.user)
        comment.likes.remove(request.user)
    
    return JsonResponse({
        'likes': comment.total_likes(),
        'dislikes': comment.total_dislikes()
    })

