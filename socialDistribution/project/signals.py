"""
Module containing signals to handle events.

Author: James Schaefer-Pham
Date: 2023-11-18

Copyright 2023 RESTless Clients
Licensed under the MIT License

Sources:
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from .models import Author, Post, PostLike, Comment

# stream update after post creation
@receiver(post_save, sender=Post)
def on_post_create(sender, instance, created, **kwargs):
    """Add a post to follower streams when created.
    
    Parameters:
        instance - the post object created
        created - boolean indicating if post created when saved
    """
    if created:  # TODO not if post unlisted or private
        if not instance.unlisted and (instance.visibility == Post.VisibilityChoice.PUBLIC or instance.visibility == Post.VisibilityChoice.FRIENDS_ONLY):
            post = instance
            author = instance.author

            followers = author.followers.all()

            #print("sending public/friends only post to inbox")

            for follower in followers:
                follower.streamPosts.add(post)
            
            #print("post sent to stream inboxes:", post.title)
        elif not instance.unlisted and instance.visibility == Post.VisibilityChoice.PRIVATE:
            post = instance
            reciever = instance.private_reciever

            if reciever:
                reciever.streamPosts.add(post)
                print("private post sent to", reciever.displayName, ":", post.title)
            else:
                print("error: invalid private reciever")
                

        else:
            print("post unlisted")


@receiver(post_save, sender=PostLike)
def on_post_liked(sender, instance, created, **kwargs):
    # TODO send post likes to inbox of the author who created the post
    # NOTE local only???
    pass

@receiver(post_save, sender=Comment)
def on_comment_create(sender, instance, created, **kwargs):
    # TODO send comments to inbox of the author who created the post
    # NOTE local only???
    pass
