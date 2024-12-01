from django import forms
from .models import Post, Tag, Comment, Profile

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['name', 'description', 'image', 'material', 'size', 'shape', 
                 'text_and_language', 'found_location', 'color']
        exclude = ['tags']
        
        # Add error messages for required fields
        error_messages = {
            'name': {
                'required': "Please enter an object name.",
            },
            'description': {
                'required': "Please provide a description.",
            },
            'image': {
                'required': "Please upload an image for your post.",
                'invalid': "Please upload a valid image file.",
            },
        }

        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Write your comment here...'}),
        }

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['occupation', 'about_me', 'profile_picture']
        widgets = {
            'about_me': forms.Textarea(attrs={'rows': 4}),
        }



