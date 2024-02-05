"""
Module containing Django model declarations

Authors:
    Shalomi Hron
    James Schaefer-Pham
    Kai Luedemann
Date: 2023-11-16

Copyright 2023 RESTless Clients
Licensed under the MIT License

Sources:
"""

from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

import uuid


class Author(models.Model):
    """
    A class representing a user of the social network.
    Can create posts, comments, and likes, and interact with (follow) other authors.

    Attributes:
        type - the type field to use for serialization
        user - the Django user that the author is associated with
        id - the UUID primary key for the author
        url - a link to the author's profile
        host - the address of the node hosting the author
        displayName - the author's username
        github - the author's GitHub profile
        profileImage - a link to a profile image to use
        bio - a short description of the author
        streamPosts - the posts that appear in the authors inbox
        following - the authors that this user is following
    """

    type = models.CharField(max_length=20, default="author")
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    url = models.URLField(max_length=200, blank=True, null=True)
    host = models.CharField(max_length=200, default="127.0.0.1")  # TODO add conditional for localhost if not deployed
    displayName = models.CharField(max_length=50)
    github = models.URLField(max_length=200, blank=True, null=True)
    profileImage = models.URLField(max_length=200, default="https://i.imgur.com/k7XVwpB.jpeg")

    bio = models.CharField(max_length=1000, blank=True)

    streamPosts = models.ManyToManyField("Post", related_name="inboxes", blank=True)  # TODO wwe need to refactor this to add likes and comments
    following = models.ManyToManyField("Author", related_name='followers', symmetrical=False, blank=True)

    def get_url(self):
        return self.url
    
    def __str__(self):
        return self.displayName

class Notification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    message = models.CharField(max_length=500)
    link = models.URLField(max_length=500)
    timestamp = models.DateTimeField(default=timezone.now, blank=True)

class FollowRequest(models.Model):
    """
    A class representing a follow request sent by one author to another.

    Attributes:
        id - the UUID primary key of the FollowRequest
        summary - a short note to be sent with the FollowRequest
        follower - the sender of the FollowRequest
        following - the recipient of the FollowRequest
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    summary = models.CharField(max_length=200)
    follower = models.ForeignKey(Author, related_name='outgoing_follow_requests', on_delete=models.CASCADE)
    following = models.ForeignKey(Author, related_name='incoming_follow_requests', on_delete=models.CASCADE)


class Post(models.Model):
    """
    A class representing a post made by an author.
    Can be viewed, liked, commented on, or shared.

    Attributes:
        title - the title of the Post
        id - the UUID primary key of the Post
        source - the link from where this Post was received
        origin - the link from which this Post originated
        description - a description of the post
        contentType - the content format of the post
            - can be plaintext, markdown or image?
        content - the post text
        author - the author that created the post
        categories - list of categories that the post fits into
        count - the total number of comments on the post
        published - the ISO 8601 timestamp when the post was published
        visibility - one of PUBLIC, PRIVATE, or FRIENDS ONLY; determines who can see the post
        unlisted - flag whether the post is discoverable by browsing
    """

    class VisibilityChoice(models.TextChoices):
        PUBLIC = "PUBLIC", "PUBLIC"
        PRIVATE = "PRIVATE", "PRIVATE"
        FRIENDS_ONLY = "FRIENDS_ONLY", "FRIENDS_ONLY"

    class TypeChoice(models.TextChoices):
        TEXT = "text/plain", "Text"
        COMMON = "text/markdown", "CommonMark"
        IMAGE = "image/png;base64", "PNG"
        IMAGE2 = "image/jpeg;base64", "JPEG"
    
    type = models.CharField(max_length=20, default="post")
    title = models.CharField(max_length=50, default="Untitled")
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    source = models.URLField(max_length=200, blank=True)
    origin = models.URLField(max_length=200, blank=True)
    description = models.CharField(max_length=50, default="")
    private_reciever = models.ForeignKey(Author, related_name="reciever", blank=True, null=True, default=None, on_delete=models.CASCADE)  # TODO should we allow post to remain if reciever author is deleted? if not, what else do we do?
    contentType = models.CharField(max_length=200, choices=TypeChoice.choices)
    content = models.TextField(default="")
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    categories = models.CharField(max_length=200, default="") # TODO Change to list
    count = models.IntegerField(default=0)
    published = models.DateTimeField(default=timezone.now, blank=True)
    visibility = models.CharField(max_length=50, choices=VisibilityChoice.choices, default=VisibilityChoice.PUBLIC)
    unlisted = models.BooleanField(default=False)


    def get_absolute_url(self):
        return reverse("project:post", kwargs={"author_id": self.author,"pk": self.pk})
    
    def get_url(self):
        return f"{self.author.get_url()}/posts/{self.id}"
    

class Comment(models.Model):
    """
    Class representing a comment on a post.

    Attributes:
        author - the author who wrote the comment
        comment - the content of the comment
        contentType - the format of the comment
            - can be plaintext or markdown
        published - the ISO 8601 timestamp when the comment was posted
        id - the UUID primary key of the comment
        post - the post that the comment was added too
    """

    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    comment = models.TextField(max_length=600)
    contentType = models.CharField(max_length=200)
    published = models.DateTimeField(default=timezone.now, blank=True)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    def get_url(self):
        return f"{self.post.get_url()}/comments/{self.id}"

class PostLike(models.Model):
    """
    Class representing a like on a post.

    Attributes:
        context - ??? (http://niem.github.io/json/reference/json-ld/context/)
        summary - a short note sent with the like
        author - the author who liked the post
        post - the post that was liked
        id - the UUID primary key of the like
    """
    context = models.URLField(max_length=200)
    summary = models.CharField(max_length=50)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)


class CommentLike(models.Model):
    """
    Class representing a like on a comment.

    Attributes:
        context - ??? (http://niem.github.io/json/reference/json-ld/context/)
        summary - a short note sent with the like
        author - the author who liked the comment
        comment - the comment that was liked
        id - the UUID primary key of the like
    """
    context = models.URLField(max_length=200)
    summary = models.CharField(max_length=50)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)


class Node(models.Model):
    """
    A class representing a node running the distributed social network.

    Attributes:
        id - the UUID primary key of the node
        nodeName - the name of the node
        apiURL - the address to access the API service
        host - the IP of the node
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nodeName = models.CharField(max_length=50, blank=True)
    nodeCred = models.CharField(max_length=50, blank=True)
    apiURL = models.URLField(max_length=200, blank=True)
    host = models.CharField(max_length=200, default="127.0.0.1:8000")
