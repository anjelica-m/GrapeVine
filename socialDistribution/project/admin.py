"""
Module for registering models with the admin interface.

Authors:
    Kai Luedemann
    Shalomi Hron
Date: 2023-11-18

Copyright 2023 RESTless Clients
Licensed under the MIT License

Sources:
"""

from django.contrib import admin
from .models import Author, FollowRequest, Post, Comment, PostLike, CommentLike, Node, Notification


# Register your models here.
admin.site.register(Author)
admin.site.register(FollowRequest)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(PostLike)
admin.site.register(CommentLike)
admin.site.register(Node)
admin.site.register(Notification)