from django.shortcuts import render, redirect, get_object_or_404
from .models import Post,Comment
from .forms import PostForm, CommentForm
from django.contrib.auth.decorators import login_required

#def post_list(request):
 #   posts = Post.objects.all()
  #  return render(request, 'posts/post_list.html', {'posts': posts})

#def post_list(request):
 #   posts = Post.objects.all()
  #  return render(request, 'posts/post_list.html', {'posts': posts})


#def post_list(request):
  #  posts = Post.objects.prefetch_related('comments').all()  # Fetch posts with related comments

    # Handle comment submission
   # if request.method == 'POST' and request.user.is_authenticated:
    #    post_id = request.POST.get('post_id')
     #   post = get_object_or_404(Post, id=post_id)
      #  form = CommentForm(request.POST)
       # if form.is_valid():
        #    comment = form.save(commit=False)
         #   comment.post = post
          #  comment.author = request.user
           # comment.save()
            #return redirect('post_list')  # Redirect to avoid resubmission on refresh
    #else:
     #   form = CommentForm()  # Empty form for new comments

   # return render(request, 'posts/post_list.html', {
    #    'posts': posts,
     #   'form': form
    #})




def post_list(request):
    posts = Post.objects.prefetch_related('comments').all()  # Fetch posts with related comments

    # Handle comment submission
    if request.method == 'POST' and request.user.is_authenticated:
        post_id = request.POST.get('post_id')
        post = get_object_or_404(Post, id=post_id)
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect('post_list')  # Redirect to avoid resubmission on refresh
    else:
        form = CommentForm()  # Empty form for new comments

    return render(request, 'posts/post_list.html', {
        'posts': posts,
        'form': form
    })






def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    comments = post.comments.all()

    if request.method == 'POST':
        if request.user.is_authenticated:
            form = CommentForm(request.POST)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.post = post
                comment.author = request.user
                comment.save()
                return redirect('post_detail', pk=post.pk)
        else:
            return redirect('login')
    else:
        form = CommentForm()

    return render(request, 'posts/post_detail.html', {'post': post, 'comments': comments, 'form': form})

@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'posts/create_post.html', {'form': form})
