from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from .models import Post, Tag, Comment, Reply
from django.contrib import messages
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from .forms import PostForm, CommentForm, ProfileUpdateForm, ReplyForm
import requests
import json
from django.db.models import Q
from django.utils import timezone

# Home view: Display all posts
def home(request):
    # Start with all posts
    posts = Post.objects.all().prefetch_related('tags')
    
    # Define size ranges
    size_ranges = {
        'Tiny': (0, 5),
        'Small': (5, 10),
        'Medium': (10, 30),
        'Large': (30, 100),
        'Very Large': (100, 999999)
    }
    
    # Debug print
    print("Search parameters:", request.GET)
    
    # Apply filters for each field if provided
    if request.GET.get('name'):
        posts = posts.filter(name__icontains=request.GET['name'])
        print(f"After name filter: {posts.count()} posts")

    if request.GET.get('material') and request.GET.get('material') != '':
        posts = posts.filter(material__iexact=request.GET['material'])
        print(f"After material filter: {posts.count()} posts")
        
    # Add status filter
    if request.GET.get('status') and request.GET.get('status') != '':
        posts = posts.filter(status=request.GET['status'])
        print(f"After status filter: {posts.count()} posts")
        
    # Handle all size dimensions
    if request.GET.get('size_x') and request.GET.get('size_x') != '':
        size_range = size_ranges.get(request.GET['size_x'])
        if size_range:
            posts = posts.filter(size_x__gte=size_range[0], size_x__lt=size_range[1])
            print(f"After length filter: {posts.count()} posts")
            
    if request.GET.get('size_y') and request.GET.get('size_y') != '':
        size_range = size_ranges.get(request.GET['size_y'])
        if size_range:
            posts = posts.filter(size_y__gte=size_range[0], size_y__lt=size_range[1])
            print(f"After width filter: {posts.count()} posts")
            
    if request.GET.get('size_z') and request.GET.get('size_z') != '':
        size_range = size_ranges.get(request.GET['size_z'])
        if size_range:
            posts = posts.filter(size_z__gte=size_range[0], size_z__lt=size_range[1])
            print(f"After height filter: {posts.count()} posts")
            
    if request.GET.get('shape') and request.GET.get('shape') != '':
        posts = posts.filter(shape__iexact=request.GET['shape'])
        print(f"After shape filter: {posts.count()} posts")

    if request.GET.get('text_and_language'):
        posts = posts.filter(text_and_language__icontains=request.GET['text_and_language'])
        print(f"After text filter: {posts.count()} posts")

    if request.GET.get('found_location'):
        posts = posts.filter(found_location__icontains=request.GET['found_location'])
        print(f"After location filter: {posts.count()} posts")

    if request.GET.get('color') and request.GET.get('color') != '':
        posts = posts.filter(color__iexact=request.GET['color'])
        print(f"After color filter: {posts.count()} posts")
    
    # Description search
    description_query = request.GET.get('description', '').strip()
    if description_query:
        posts = posts.filter(description__icontains=description_query)
        print(f"After description filter: {posts.count()} posts")

    # Print final query for debugging
    print("Final SQL:", posts.query)
    
    # Order posts by creation date
    posts = posts.order_by('-created_at')
    
    # Handle tag filtering
    tags_json = request.GET.get('tags', '')
    print("Received tags:", tags_json)  # Debug print
    
    if tags_json:
        try:
            # Parse the JSON string to get tag IDs
            tag_ids = json.loads(tags_json)
            print("Parsed tag IDs:", tag_ids)  # Debug print
            
            # Get all posts that have ANY of these tags
            if tag_ids:
                posts = posts.filter(tags__wikidata_id__in=tag_ids).distinct()
                print("Found posts:", posts.count())  # Debug print
                
                if not posts.exists():
                    messages.info(request, "No posts found with the specified tags.")
        except json.JSONDecodeError:
            print("Error parsing tags JSON")  # Debug print
            messages.error(request, "Error processing tag search")

    if request.user.is_authenticated:
        user_posts = Post.objects.filter(author=request.user)
        for post in posts:
            post.comment_list = Comment.objects.filter(post=post).order_by('-created_at')
        return render(request, 'whatisthis/user_dashboard.html', {
            'posts': posts,
            'comment_form': CommentForm(),
            'user_posts': user_posts,
            'all_tags': Tag.objects.all(),
        })
    else:
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
        tags = [
            {
                'wikidata_id': item['id'],
                'label': item['label'],
                'description': item.get('description', 'No description available')
            }
            for item in data.get('search', [])
        ]
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
    if request.method == 'POST' and request.user.is_authenticated:
        data = json.loads(request.body)
        content = data.get('content')
        post = get_object_or_404(Post, id=post_id)
        
        comment = Comment.objects.create(
            post=post,
            author=request.user,
            content=content
        )
        
        return JsonResponse({
            'success': True,
            'comment': {
                'id': comment.id,
                'content': comment.content,
                'author': comment.author.username,
                'created_at': comment.created_at.strftime('%b %d, %Y')
            }
        })
    
    return JsonResponse({'success': False}, status=400)

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

def search_tags(request):
    query = request.GET.get('q', '')
    tags = Tag.objects.filter(
        Q(label__icontains=query) | 
        Q(wikidata_id__icontains=query)
    )[:10]  # Limit to 10 results
    
    results = [{'id': tag.id, 'label': tag.label, 'wikidata_id': tag.wikidata_id} 
               for tag in tags]
    
    return JsonResponse({
        'results': results
    })

def post_detail(request, post_id):
    post = get_object_or_404(Post.objects.prefetch_related('tags'), id=post_id)
    post.comment_list = Comment.objects.filter(post=post).order_by('-created_at')
    
    return render(request, 'whatisthis/post_detail.html', {
        'post': post,
        'comment_form': CommentForm(),
    })

@login_required
def add_reply(request, comment_id):
    if request.method == 'POST':
        comment = get_object_or_404(Comment, id=comment_id)
        content = request.POST.get('content')
        
        reply = Reply.objects.create(
            comment=comment,
            author=request.user,
            content=content
        )
        
        return redirect('post_detail', post_id=comment.post.id)
    
    return redirect('home')

@login_required
@require_POST
def upvote_reply(request, reply_id):
    reply = get_object_or_404(Reply, id=reply_id)
    
    if request.user in reply.likes.all():
        reply.likes.remove(request.user)
    else:
        reply.likes.add(request.user)
        reply.dislikes.remove(request.user)
    
    return JsonResponse({
        'likes': reply.likes.count(),
        'dislikes': reply.dislikes.count()
    })

@login_required
@require_POST
def downvote_reply(request, reply_id):
    reply = get_object_or_404(Reply, id=reply_id)
    
    if request.user in reply.dislikes.all():
        reply.dislikes.remove(request.user)
    else:
        reply.dislikes.add(request.user)
        reply.likes.remove(request.user)
    
    return JsonResponse({
        'likes': reply.likes.count(),
        'dislikes': reply.dislikes.count()
    })

@login_required
def add_nested_reply(request, reply_id):
    parent_reply = get_object_or_404(Reply, id=reply_id)
    if request.method == 'POST':
        content = request.POST.get('content')
        
        # Create the nested reply
        nested_reply = Reply.objects.create(
            author=request.user,
            content=content,
            parent=parent_reply,
            comment=parent_reply.comment  # Keep the same root comment
        )
        
        # Redirect to the post detail page
        return redirect('post_detail', post_id=parent_reply.comment.post.id)
    
    return redirect('home')

@login_required
@require_POST
def vote_reply(request, reply_id, vote_type):
    reply = get_object_or_404(Reply, id=reply_id)
    if vote_type == 'upvote':
        # Logic to handle upvote
        pass
    elif vote_type == 'downvote':
        # Logic to handle downvote
        pass
    return JsonResponse({'likes': reply.total_likes, 'dislikes': reply.total_dislikes})

