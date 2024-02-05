"""
Module containing HTML form classes.

Authors:
    James Schaefer-Pham
    Shalomi Hron
Date: 2023-11-18

Copyright 2023 RESTless Clients
Licensed under the MIT License

Sources:
https://stackoverflow.com/questions/22567320/django-edit-user-profile
https://www.javatpoint.com/django-usercreationform
"""

from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm

from .models import Post, Author

class CreatePostForm(forms.ModelForm):
    """Form for creating a new post.
    
    Fields:
        title - text (50)
        description - text (200)
        content - text (600)
        categories - text (200)
        visibility - drop-down (PUBLIC, FRIENDS-ONLY, PRIVATE)
        unlisted - boolean
    """
    
    # NOTE Code almost identical to EditPostForm. Changes made there should probably be made here
    # TODO Handle validation errors, eg when required field is empty

    title = forms.CharField(
        max_length=50, 
        label="Title", 
        required=True
    )
    
    description = forms.CharField(
        max_length=200, 
        label="Description", 
        required=True
    )
    contentType = forms.ChoiceField(
        initial = Post.TypeChoice.TEXT,
        label="Content Type",
        choices=Post.TypeChoice.choices,
        required=True 
    )
    content = forms.CharField(
        label="Content", 
        required=False
    )
    picture = forms.ImageField(label="Upload an Image:", required=False)
    
    # TODO Modify this and the Post model field to be a list of str.
    categories = forms.CharField(
        max_length=200, 
        label="Categories"
    ) 
    
    visibility = forms.ChoiceField(
        label="Visibility",
        choices=Post.VisibilityChoice.choices
    )
    
    # TODO make hidden when not creating private message
    private_reciever = forms.ModelChoiceField(
        queryset=Author.objects.all().order_by("displayName"),
        label="Private Post Reciever",
        required=False
    )

    unlisted = forms.BooleanField(
        label="Unlisted?",
        required=False
    )
    
    
    class Meta:
        model = Post
        fields = ["title", "description", "content", "categories", "visibility", "private_reciever", "unlisted"]

    #https://docs.djangoproject.com/en/dev/ref/forms/validation/#cleaning-and-validating-fields-that-depend-on-each-other
    def clean(self):
        clean_data = super().clean()
        visibility = clean_data.get("visibility")
        reciever = clean_data.get("private_reciever")

        if visibility and reciever == None and visibility == Post.VisibilityChoice.PRIVATE:
            self.add_error("private_reciever", "Select a reciever when sending private post")




    def clean(self):
        # https://stackoverflow.com/questions/73705283/how-to-make-one-form-field-compulsory-to-select-or-fill-in-other-in-django-model

        cleaned = super().clean()
        content = cleaned.get('content')
        picture = cleaned.get('picture')

        if not content and not picture:
            raise ValidationError("You must add a photo for type PNG/JPEG, or fill out content field otherwise.")


# TODO delete?
class EditPostForm(forms.ModelForm):
    """Form for editing posts.
    
    Fields:
        title - text (50)
        description - text (200)
        content - text (600)
        categories - text (200)
        visibility - drop-down (PUBLIC, FRIENDS-ONLY, PRIVATE)
        unlisted - boolean
    """
    
    # NOTE Code almost identical to CreatePostForm. Changes made there should probably be made here
    # TODO Handle validation errors, eg when required field is empty

    title = forms.CharField(
        max_length=50, 
        label="Title", 
        required=True
    )
    
    description = forms.CharField(
        max_length=200, 
        label="Description", 
        required=True
    )
    
    content = forms.CharField(
        max_length=600, 
        label="Content", 
        required=True
    )
    
    # TODO Modify this and the Post model field to be a list of str.
    categories = forms.CharField(
        max_length=200, 
        label="Categories"
    ) 
    
    class Meta:
        model = Post
        fields = ["title", "description", "content", "categories"]


class AuthorCreationForm(UserCreationForm):
    """Form for creating a new author.
    
    Fields:
        username - text
        github - text
        password - password

    Sources:
    https://stackoverflow.com/questions/22567320/django-edit-user-profile
    https://www.javatpoint.com/django-usercreationform
    https://stackoverflow.com/questions/48049247/how-to-set-is-active-false-in-django-usercreationform
    """

    username = forms.CharField(help_text='Enter a unique username') # required for the user, copy for displayName below
    github = forms.CharField(required=False, help_text='Optional')
    class Meta: 
        model = User
        fields = ('username', 'github', 'password1', 'password2')
    
    def clean(self):
        """Check for valid data."""
        cleaned_data = self.cleaned_data
        username = cleaned_data.get('username')

        # implement the uniqueness and correct password checking by hand
        # automatically checks for strong passwords
        if User.objects.filter(username=username).exists():
            raise ValidationError('Username already exists.')
        if cleaned_data.get('password1') != cleaned_data.get('password2'):
            raise ValidationError('Passwords do not match!')
    
    def save(self, commit=True):
        """Save the new author and corresponding user."""
        user = super(AuthorCreationForm, self).save(commit=False)

        # https://stackoverflow.com/questions/48049247/how-to-set-is-active-false-in-django-usercreationform
        user.is_active = False # Admin must activate new users
        
        if commit:
            user.save()
            author = Author.objects.create(user=user,
                    displayName = self.cleaned_data.get('username'),
                    github = self.cleaned_data.get('github'))
            author.save()    
        return user


# The author can only update their github link and bio
class EditProfileForm(forms.ModelForm):
    """Form for editing a user profile.

    Fields:
        github - text
        bio - text
    """
    github = forms.CharField(required=False)
    bio = forms.CharField(required=False)
    class Meta:
        model = Author
        fields = ['github', 'bio']
