from django import forms
from .models import Post, Tag, Comment, Profile

class PostForm(forms.ModelForm):
    # Define choices for dimensions (1-1000 cm)
    DIMENSION_CHOICES = [(i, f"{i} cm") for i in range(1, 1001)]
    
    # Define color choices with None as default
    COLOR_CHOICES = [
        ('none', 'None'),  # Added default None option
        ('black', 'Black'),
        ('white', 'White'),
        ('gray', 'Gray'),
        ('red', 'Red'),
        ('blue', 'Blue'),
        ('green', 'Green'),
        ('yellow', 'Yellow'),
        ('purple', 'Purple'),
        ('orange', 'Orange'),
        ('brown', 'Brown'),
        ('pink', 'Pink'),
        ('gold', 'Gold'),
        ('silver', 'Silver'),
        ('bronze', 'Bronze'),
        ('multicolor', 'Multicolor'),
        ('other', 'Other'),
    ]

    size_x = forms.ChoiceField(choices=DIMENSION_CHOICES, required=False, label="Length")
    size_y = forms.ChoiceField(choices=DIMENSION_CHOICES, required=False, label="Width")
    size_z = forms.ChoiceField(choices=DIMENSION_CHOICES, required=False, label="Height")
    color = forms.ChoiceField(choices=COLOR_CHOICES, required=False, label="Color", initial='none')  # Set initial value to 'none'

    class Meta:
        model = Post
        fields = ['name', 'description', 'image', 
                 'size_x', 'size_y', 'size_z',
                 'material', 'shape', 'text_and_language', 
                 'found_location', 'color']
        exclude = ['tags']
        
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['size_x'].group_header = "Object Dimensions"

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



