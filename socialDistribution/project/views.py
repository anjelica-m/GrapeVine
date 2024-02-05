from typing import Any
from django.db import models
from django.db.models.query import QuerySet
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render
from django.views import generic
from django.views.generic import CreateView, UpdateView
from django.http import HttpResponseRedirect, Http404
"""
Module containing Django views that the client interacts with.

Authors:
    Kai Luedemann
    Anjelica Marianicz
    James Schaefer-Pham
    Sashreek Magan
    Shalomi Hron
Date: 2023-11-18

Copyright 2023 RESTless Clients
Licensed under the MIT License

Sources:
https://docs.djangoproject.com/en/4.2/ref/class-based-views/generic-editing/#django.views.generic.edit.UpdateView
"""

from django.contrib.auth.models import User


import base64
import json

from django.shortcuts import render
from django.views import generic
from django.views.generic import CreateView, UpdateView
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import AccessMixin, UserPassesTestMixin, LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView, ListAPIView
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser

import requests
from datetime import datetime
from operator import itemgetter

from .serializers import PostSerializer, AuthorSerializer, NodeSerializer, FollowRequestSerializer, \
    CommentLikeSerializer, CommentSerializer, PostLikeSerializer, UserSignUpSerializer, NotificationSerializer
from .models import Author, CommentLike, Post, Comment, PostLike, FollowRequest, Node, Notification
from .forms import AuthorCreationForm, EditProfileForm, CreatePostForm, EditPostForm
from .pagination import CommentPagination, AuthorPagination, PostPagination, InboxPagination
from .utils import *


class AuthorView(generic.DetailView):
    """Display the author page.
    
    Note: Superceded by ProfileView below
    """
    template_name = 'project/author.html'
    model = Author



class PostView(UserPassesTestMixin, generic.DetailView):
    """Display a post page."""
    template_name = 'project/post.html'
    model = Post

    # TODO delete prints
    def test_func(self):
        post = self.get_object()
        user = self.request.user.author

        if post.visibility == Post.VisibilityChoice.FRIENDS_ONLY:
            print("accessing friends post")
            return post.author == user or user in post.author.followers.all()
        elif post.visibility == Post.VisibilityChoice.PRIVATE:
            print("accessing private post")
            return post.author == user or post.private_reciever == user
        elif post.visibility == Post.VisibilityChoice.PUBLIC:
            print("accessing public post")
            return True
        else:
            raise Exception("Post has invalid visibility option")

    def get_object(self):
        post = get_object_or_404(Post, id=self.kwargs["pk"], author=self.kwargs["author_id"]) # Ensure the post belongs to this author
        pkvalue = self.kwargs['pk']
        aivalue = self.kwargs["author_id"]
        postLikesList = []

        if post.visibility != "PUBLIC":
            return post
        # otherwise try to fetch the comments on the public post
        elif post.author.host=="https://im-a-teapot-41db2c906820.herokuapp.com/":
            response = requests.get(f"https://im-a-teapot-41db2c906820.herokuapp.com/api/authors/{aivalue}/posts/{pkvalue}/comments", auth=("teapot", "rooibos"))
            commentsList = response.json()["comments"]
            # response2 = requests.get(f"https://im-a-teapot-41db2c906820.herokuapp.com/api/authors/{aivalue}/posts/{pkvalue}/likes/", auth=("teapot", "rooibos"))
            # postLikesList = response2.json()["likes"]

        elif post.author.host=="https://silk-cmput404-project-21e5c91727a7.herokuapp.com":
            response = requests.get(f"http://silk-cmput404-project-21e5c91727a7.herokuapp.com/api/authors/{aivalue}/posts/{pkvalue}/comments", auth=("RESTless Clients", "RESTlessClients1!"))
            commentsList = response.json()["comments"]
            response2 = requests.get(f"https://silk-cmput404-project-21e5c91727a7.herokuapp.com/api/authors/{aivalue}/posts/{pkvalue}/likes", auth=("RESTless Clients", "RESTlessClients1!"))
            postLikesList = response2.json()["items"]

        elif post.author.host=="https://cmput404-project-backend-tian-aaf1fa9b20e8.herokuapp.com/":
            response = requests.get(f"https://cmput404-project-backend-tian-aaf1fa9b20e8.herokuapp.com/authors/{aivalue}/posts/{pkvalue}/comments", auth=("cross-server", "password"))
            commentsList = response.json()["items"]
            # response2 = requests.get(f"https://cmput404-project-backend-tian-aaf1fa9b20e8.herokuapp.com/authors/{aivalue}/posts/{pkvalue}/likes", auth=("cross-server", "password"))
            # postLikesList = response2.json()["items"]

        else:
            return post
        for comment in commentsList:
            addOrGetRemoteComment(comment, post)
        for like in postLikesList:
            addOrGetRemotePostLike(like, post)
        return post


class StreamView(generic.ListView):
    """Display the stream view

    Note: Superceded by stream_view function below
    """
    template_name = 'project/stream.html'
    context_object_name = 'latest_posts'

    def get_queryset(self):
        self.author = get_object_or_404(Author, displayName=self.kwargs["username"])
        return self.author.streamPosts.order_by("-published")


def stream_view(request):
    return HttpResponse(open(settings.BASE_DIR.parent / "frontend/dist/index.html").read())

class ProfileAPIView(ListAPIView):
    # model = Post
    serializer_class = PostSerializer

    def get_queryset(self):
        author = get_object_or_404(Author, pk=self.kwargs['pk'])
        pkvalue = self.kwargs['pk']
        postsList = []

        if author.host=="https://im-a-teapot-41db2c906820.herokuapp.com/":
            response = requests.get(f"https://im-a-teapot-41db2c906820.herokuapp.com/api/authors/{pkvalue}/posts/", auth=("teapot", "rooibos"))
            postsList = response.json()["items"]
        elif author.host=="https://silk-cmput404-project-21e5c91727a7.herokuapp.com":
            response = requests.get(f"http://silk-cmput404-project-21e5c91727a7.herokuapp.com/api/authors/{pkvalue}/posts/", auth=("RESTless Clients", "RESTlessClients1!"))
            try:
                postsList = response.json()["data"]
            except:
                print("bad data, ignored")
        elif author.host=="https://cmput404-project-backend-tian-aaf1fa9b20e8.herokuapp.com/":
            response = requests.get(f"https://cmput404-project-backend-tian-aaf1fa9b20e8.herokuapp.com/authors/{pkvalue}/posts/", auth=("cross-server", "password"))
            postsList = response.json()["items"]

        for post in postsList:
            addOrGetRemotePost(post, author)
        
        query = author.post_set.all().order_by('-published')
        return query

class ProfileView(generic.DetailView):
    """Display an author's profile"""
    template_name = 'project/profile.html'
    model = Author

    def get_object(self):
        author = get_object_or_404(Author, pk=self.kwargs['pk'])
        pkvalue = self.kwargs['pk']
        postsList = []

        if author.host=="https://im-a-teapot-41db2c906820.herokuapp.com/":
            response = requests.get(f"https://im-a-teapot-41db2c906820.herokuapp.com/api/authors/{pkvalue}/posts/", auth=("teapot", "rooibos"))
            postsList = response.json()["items"]
        elif author.host=="https://silk-cmput404-project-21e5c91727a7.herokuapp.com":
            response = requests.get(f"http://silk-cmput404-project-21e5c91727a7.herokuapp.com/api/authors/{pkvalue}/posts/", auth=("RESTless Clients", "RESTlessClients1!"))
            try:
                postsList = response.json()["data"]
            except:
                print("bad data, ignored")
        elif author.host=="https://cmput404-project-backend-tian-aaf1fa9b20e8.herokuapp.com/":
            response = requests.get(f"https://cmput404-project-backend-tian-aaf1fa9b20e8.herokuapp.com/authors/{pkvalue}/posts/", auth=("cross-server", "password"))
            postsList = response.json()["items"]
        else:
            return author

        for post in postsList:
            addOrGetRemotePost(post, author)
        return author


@login_required
def profile_edit(request):
    """Edit the current user's profile"""
    logged_in_author = request.user.author
    if request.method == "GET":
        form = EditProfileForm(instance=logged_in_author)
        return render(request, 'project/edit_profile.html', {'form': form})
    elif request.method == "POST":
        form = EditProfileForm(request.POST, instance=logged_in_author)
        # Given the navigation bar, no redirection is needed.
        if form.is_valid():
            if form.has_changed():
                form.save()

                 # Only display notification if some changes were made
                messages.success(request, "Changes saved successfully")
            return HttpResponseRedirect(reverse('project:profile_edit'))
        else:
            # if the form input was not valid, try again
            messages.success(request, "Warning: not a valid Github link, changes discarded")
            return HttpResponseRedirect(reverse('project:profile_edit'))


class CreatePostView(LoginRequiredMixin, CreateView):
    """Create a post from user-submitted form and save."""

    model = Post
    template_name = "project/create-post.html"
    form_class = CreatePostForm
    login_url="login"

    def form_valid(self, form):
        """Return a response when the form is submitted.
        
        Parameters:
            form - the CreatePostForm that was submitted
        """
        author = get_object_or_404(Author, pk=self.request.user.author.id)
        form.instance.author = author
        
        form.instance.contentType = form.cleaned_data['contentType']
        

        if form.instance.contentType == 'image/png;base64':
            form.instance.content = 'data:image/png;base64,'+ str(base64.b64encode(form.cleaned_data['picture'].file.read()).decode('ascii'))


        elif form.instance.contentType == 'image/jpeg;base64':
            form.instance.content = 'data:image/jpeg;base64,'+ str(base64.b64encode(form.cleaned_data['picture'].file.read()).decode('ascii'))
        # TODO These are just placeholders. Need to figure out what to put here for part 2
        form.instance.source = "http://127.0.0.1:8000/"
        form.instance.origin = "http://127.0.0.1:8000/"

        # form.instance.contentType = "text/plain" # TODO Change when implementing Markdown
        form.instance.count = 0
        form.instance.published = datetime.now()

        return super(CreatePostView, self).form_valid(form)


class EditPostView(LoginRequiredMixin, UpdateView):
    """Update a post based on form-submission by a user.

    Source:
    https://docs.djangoproject.com/en/4.2/ref/class-based-views/generic-editing/#django.views.generic.edit.UpdateView
    """
    model = Post
    template_name = "project/edit-post.html"
    form_class = EditPostForm
    login_url = "login"

    # TODO check that the author is the current user    


class SignUpView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = UserSignUpSerializer(data=request.data, context={"request": self.request})
        if serializer.is_valid():
            serializer.perform()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AuthorAPIView(ListAPIView):
    """
    Get the list of authors on our website
    """
    # authentication_classes = [BasicAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    serializer_class = AuthorSerializer
    pagination_class = AuthorPagination

    def get_queryset(self):
        auth_header = self.request.META.get('HTTP_AUTHORIZATION', '')
        token_type, _, credentials = auth_header.partition(' ')

        self.Error = False
        if token_type == "Basic" and not (Node.objects.filter(user=self.request.user).exists()):
            self.Error = True
        #return Author.objects.all().order_by("id")
        return Author.objects.filter(host="https://restlessclients-7b4ebf6b9382.herokuapp.com/").order_by("id")


class CheckUsernameView(APIView):
    def get(self, request, *args, **kwargs):
        username = request.query_params.get('username', None)
        if username is not None:
            is_taken = User.objects.filter(username=username).exists()
            return Response({'is_taken': is_taken})
        return Response({'error': 'No username provided'}, status=status.HTTP_400_BAD_REQUEST)


class UpdateAuthorApiView(APIView):
    """
    Update or get a specific author
    """
    # authentication_classes = [BasicAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]


    def get(self, request, *args, pk=None, **kwargs):
        if pk == 'me':
            author = request.user.author
        else:
            author = get_object_or_404(Author, id=pk)

        serializer = AuthorSerializer(author, data=request.data, partial=True)
        if serializer.is_valid():
            return Response(serializer.data, status=200)
        return Response(status=400, data=serializer.errors)
    
    # Restricted to local access.
    def post(self, request, *args, **kwargs):
        # Reference: https://stackoverflow.com/questions/152248/can-i-use-http-basic-authentication-with-django/62028635#62028635
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        token_type, _, credentials = auth_header.partition(' ')
        if token_type == "Basic":
            return Response({"detail": "Invalid authorization: access denied."}, status=401)
        else:
            author = get_object_or_404(Author, id=self.kwargs["pk"])
            if author.user != request.user:
                return Response({"detail": "Invalid authorization: access denied."}, status=401)
            
            serializer = AuthorSerializer(author, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=200)
            return Response(status=400, data=serializer.errors)


class PostsAPIView(ListCreateAPIView):
    """
    Get the list of posts on our website
    """
    # authentication_classes = [BasicAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    serializer_class = PostSerializer
    pagination_class = PostPagination

    # TODO Visibility
    def get_queryset(self):
        auth_header = self.request.META.get('HTTP_AUTHORIZATION', '')
        token_type, _, credentials = auth_header.partition(' ')

        self.Error = False
        if token_type == "Basic" and not (Node.objects.filter(user=self.request.user).exists()):
            self.Error = True

        author = get_object_or_404(Author, pk=self.kwargs["pk"])
        self.posts = Post.objects.filter(author=self.kwargs["pk"])

        try:
            user = get_object_or_404(Author, user=self.request.user)
        except Http404:
            user = None

        if user == None:
            print("can'f find user for posts api")
            self.posts = self.posts.filter(unlisted=False)
            self.posts = self.posts.exclude(visibility=Post.VisibilityChoice.FRIENDS_ONLY)
            self.posts = self.posts.exclude(visibility=Post.VisibilityChoice.PRIVATE)            
        elif not user == author:
            print("user is not author for posts api")
            self.posts = self.posts.filter(unlisted=False)
            self.posts = self.posts.exclude(Q(visibility=Post.VisibilityChoice.FRIENDS_ONLY) & ~Q(author__followers=user))
            self.posts = self.posts.exclude(Q(visibility=Post.VisibilityChoice.PRIVATE) & ~Q(private_reciever=user))

        self.posts = self.posts.order_by('published')
        return self.posts

    # Restricted to local access.
    def post(self, request, *args, **kwargs):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        token_type, _, credentials = auth_header.partition(' ')
        if token_type == "Basic":
            return Response({"detail": "Invalid authorization: access denied."}, status=401)
        else:
            author = get_object_or_404(Author, pk=kwargs["pk"])
            if author.user != request.user:
                return Response({"detail": "Invalid authorization: access denied."}, status=401)

            post = Post.objects.create(author=author) # Create with at least the author
            serializer = PostSerializer(post, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=201)
            return Response(status=400, data=serializer.errors)


class SinglePostApiView(APIView):
    """
    Get or update a single post
    """
    # authentication_classes = [BasicAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        auth_header = self.request.META.get('HTTP_AUTHORIZATION', '')
        token_type, _, credentials = auth_header.partition(' ')
        if token_type == "Basic" and not (Node.objects.filter(user=self.request.user).exists()):
            return Response({"detail": "Invalid authorization: access denied."}, status=401)

        author = get_object_or_404(Author, id=self.kwargs["pk"])
        post = get_object_or_404(Post, id=self.kwargs["post_id"], author=self.kwargs["pk"]) # Ensure the post belongs to this author
        
        # TODO we may want to verify the host here
        try:
            user = get_object_or_404(Author, user=self.request.user)
        except Http404:
            user = None

        if post.visibility == Post.VisibilityChoice.FRIENDS_ONLY and not (user == post.author or user in post.author.followers.all()):
            return Response(status=403, data={"detail": "Friends only post. User does not have access"})
        elif post.visibility == Post.VisibilityChoice.PRIVATE and not (user == post.author or user == post.private_reciever):
            return Response(status=403, data={"detail": "Private post. User does not have access"})

        context = {
            "user": user,
            "is_friend_only": post.visibility == Post.VisibilityChoice.FRIENDS_ONLY,
            "user_is_author": user == post.author
        }

        serializer = PostSerializer(post, data=request.data, partial=True, context=context)
        if serializer.is_valid():
            return Response(serializer.data, 200)
        return Response(status=400, data=serializer.errors)
    
    # Restricted to local access.
    def post(self, request, *args, **kwargs):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        token_type, _, credentials = auth_header.partition(' ')
        if token_type == "Basic":
            return Response({"detail": "Invalid authorization: access denied."}, status=401)
        else:
            author = get_object_or_404(Author, id=self.kwargs["pk"])
            if author.user != request.user:
                return Response({"detail": "Invalid authorization: access denied."}, status=401)

            post = get_object_or_404(Post, id=self.kwargs["post_id"], author=self.kwargs["pk"]) # Ensure the post belongs to this author
            serializer = PostSerializer(post, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=200)
            return Response(status=400, data=serializer.errors)

    # Restricted to local access.
    def delete(self, request, *args, **kwargs):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        token_type, _, credentials = auth_header.partition(' ')
        if token_type == "Basic":
            return Response({"detail": "Invalid authorization: access denied."}, status=401)
        else:
            author = get_object_or_404(Author, id=self.kwargs["pk"])
            if author.user != request.user:
                return Response({"detail": "Invalid authorization: access denied."}, status=401)

            post = get_object_or_404(Post, id=self.kwargs["post_id"], author=self.kwargs["pk"]) # Ensure the post belongs to this author
            post.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    # Restricted to local access.
    def put(self, request, *args, **kwargs):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        token_type, _, credentials = auth_header.partition(' ')
        if token_type == "Basic":
            return Response({"detail": "Invalid authorization: access denied."}, status=401)
        else:
            author = get_object_or_404(Author, id=self.kwargs["pk"])
            if author.user != request.user:
                return Response({"detail": "Invalid authorization: access denied."}, status=401)

            post = Post.objects.create(author=author, id=self.kwargs["post_id"]) # Create with at least the author and post id
            serializer = PostSerializer(post, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=201)
            return Response(status=400, data=serializer.errors)


class InboxAPIView(ListCreateAPIView):
    """
    Update an inbox
    """
    # authentication_classes = [BasicAuthentication, SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    serializer_class = PostSerializer
    pagination_class = InboxPagination

    # Restricted to local access.
    def get_queryset(self):
        author = get_object_or_404(Author, id=self.kwargs["pk"])
        
        self.inbox = author.streamPosts.all()
        self.author_str = str(author.host) + "authors/" + str(author.id)

        auth_header = self.request.META.get('HTTP_AUTHORIZATION', '')
        token_type, _, credentials = auth_header.partition(' ')
        if (token_type == "Basic") or (author.user != self.request.user):
            self.Basic = True
        else:
            self.Basic = False
        return self.inbox
    
    def post(self, request, *args, **kwargs):
        auth_header = self.request.META.get('HTTP_AUTHORIZATION', '')
        token_type, _, credentials = auth_header.partition(' ')
        if token_type == "Basic" and not (Node.objects.filter(user=self.request.user).exists()):
            return Response({"detail": "Invalid authorization: access denied."}, status=401)

        author = get_object_or_404(Author, id=self.kwargs["pk"])

        data = {
            **request.data
        }

        # remote_author = addOrGetRemoteAuthor(request.data['author'])
        

        if request.data["type"] == "post":
            post_author = addOrGetRemoteAuthor(data['author'])
            # update the inbox, i.e. update streamPosts in the Author model
            post = get_object_or_404(Post, id=request.data["id"].split('/')[6])
            if post.visibility != post.VisibilityChoice.PRIVATE and not author.following.filter(id=post_author.id).count():
                # We have unfollowed the remote author, don't accept
                return Response(status=status.HTTP_204_NO_CONTENT)
            author.streamPosts.add(post)
            return Response(status=200)
        elif request.data["type"] == "Follow":
            follower = addOrGetRemoteAuthor(data['actor'])
            serializer = FollowRequestSerializer(data=request.data)
        elif request.data["type"] == "Like":
            like_author = addOrGetRemoteAuthor(data['author'])
            # data['author']['id'] = like_author.id
            if "comment" in request.data["object"]:
                message = f"{data['author']['displayName']} liked your comment"
                link = "/".join(data['object'].split('/')[:7])
                comment_id = request.data["object"].split('/')[8]
                data['comment'] = comment_id
                serializer = CommentLikeSerializer(data=data)
            else:
                message = f"{data['author']['displayName']} liked your post"
                link = data['object']
                data['post'] = request.data["object"].split('/')[6]
                serializer = PostLikeSerializer(data=data)
            Notification.objects.create(author=author, message=message, link=link)
        elif request.data["type"] == "comment":
            comment_author = addOrGetRemoteAuthor(request.data['author'])
            post_id = request.data["id"].split('/')[6]
            data['post'] = post_id
            
            serializer = CommentSerializer(data=data)
            link = f"{author.url}/posts/{post_id}"
            message = f"{data['author']['displayName']} commented on your post"
            Notification.objects.create(author=author, message=message, link=link)
        else:
            return Response(status=400) # Invalid type
    
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(status=400, data=serializer.errors)

    # Restricted to local access.
    def delete(self, request, *args, **kwargs):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        token_type, _, credentials = auth_header.partition(' ')
        if token_type == "Basic":
            return Response({"detail": "Invalid authorization: access denied."}, status=401)
        else:
            author = get_object_or_404(Author, id=self.kwargs["pk"])
            if author.user != request.user:
                return Response({"detail": "Invalid authorization: access denied."}, status=401)

            author.streamPosts.clear()
            return Response(status=status.HTTP_204_NO_CONTENT)


class NodeAPIView(APIView):
    """
    Get the list of nodes
    """
    # authentication_classes = [BasicAuthentication, SessionAuthentication]
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        nodes = Node.objects.all()
        serializer = NodeSerializer(nodes, many=True)
        return Response(serializer.data)


class AddCommentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        post = get_object_or_404(Post, pk=kwargs['post_id'])
        content = request.data['comment']
        comment = Comment.objects.create(author=request.user.author, post=post, comment=content, contentType="text/markdown")
        author = post.author
        notif = {
            'author': author,
            'message': f"{request.user.author.displayName} commented on your post",
            'link': f"{author.url}/posts/{post.id}"
        }
        comment = send_to_inbox(comment, author, CommentSerializer, notif)
        return Response(status=status.HTTP_201_CREATED, data=comment, content_type='application/json')
        


@login_required
def add_comment(request, **kwargs):
    """Add a comment to a post."""
    if request.method == 'POST':
        posts = Post.objects.filter(pk=kwargs['pk'])
        if posts.count() == 0:
            # Add the post  
            post = create_local_post(kwargs['author_id'], kwargs['pk'])     
        else:
            post = posts.first()
        if post is not None:
            content = request.POST.get('content')
            comment = Comment.objects.create(author=request.user.author, post=post, comment=content, contentType="text/plain")  # Assuming contentType is plain text for this example
            author = post.author
            if "restlessclients" not in author.host:
                # TODO: Bad url construction
                # if "restlessclients" in author.host:
                #     auth = ("webcrawlers", "socialwebsilk")
                #     url = f"https://restlessclients-7b4ebf6b9382.herokuapp.com/api/authors/{author.pk}/inbox"
                if "im-a-teapot" in author.host:
                    auth = ("teapot", "rooibos")
                    url = f"https://im-a-teapot-41db2c906820.herokuapp.com/authors/{author.pk}/inbox/"
                elif "silk-cmput404" in author.host:
                    auth = ("restlessclients", "django100")
                    url = f"https://silk-cmput404-project-21e5c91727a7.herokuapp.com/api/authors/{author.pk}/inbox/"
                
                comment_data = CommentSerializer(comment).data
                resp = requests.post(url, json=comment_data, auth=auth)
    return HttpResponseRedirect(reverse('project:post', kwargs=kwargs))

@login_required
def like_post(request, **kwargs):
    """Like/unlike a post."""
    pk = kwargs['pk']
    if request.method == 'POST':
        post = get_object_or_404(Post, pk=pk)
        # post = Post.objects.get_or_create(pk=pk)
        # Check if the user already liked the post
        liked = PostLike.objects.filter(author=request.user.author, post=post).exists()
        if not liked:
            posts = Post.objects.filter(pk=kwargs['pk'])
            if posts.count() == 0:
                # Add the post  
                post = create_local_post(kwargs['author_id'], kwargs['pk'])     
            else:
                post = posts.first()
            if post is not None:
                like = PostLike.objects.create(author=request.user.author, post=post, summary=f"{request.user.username} likes this", context=post.source)
                author = post.author
                if "restlessclients" not in author.host:
                    # TODO: Bad url construction
                    # if "restlessclients" in author.host:
                    #     auth = ("webcrawlers", "socialwebsilk")
                    #     url = f"https://restlessclients-7b4ebf6b9382.herokuapp.com/api/authors/{author.pk}/inbox"
                    if "im-a-teapot" in author.host:
                        auth = ("teapot", "rooibos")
                        url = f"https://im-a-teapot-41db2c906820.herokuapp.com/authors/{author.pk}/inbox/"
                    elif "silk-cmput404" in author.host:
                        auth = ("restlessclients", "django100")
                        url = f"https://silk-cmput404-project-21e5c91727a7.herokuapp.com/api/authors/{author.pk}/inbox/"
    
                    like_data = PostLikeSerializer(like).data
                    resp = requests.post(url, json=like_data, auth=auth)
    # else:
    #     PostLike.objects.filter(author=request.user.author, post=post).delete()
    return HttpResponseRedirect(reverse('project:post', args=[kwargs['author_id'], pk]))

@login_required
def like_comment(request, pk):
    """Like/unlike a comment."""
    comment = get_object_or_404(Comment, pk=pk)
    # Check if the user already liked the comment
    liked = CommentLike.objects.filter(author=request.user.author, comment=comment).exists()
    if not liked:
        CommentLike.objects.create(author=request.user.author, comment=comment, summary=f"{request.user.username} likes this")
    # else:
    #     CommentLike.objects.filter(author=request.user.author, comment=comment).delete()
    return redirect(reverse('project:post', args=[comment.post.author.id, comment.post.id]))


class FollowRequestSendView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """Send a follow request to another author."""
        pk = kwargs['pk']
        author = get_object_or_404(Author, pk=pk)
        request_exists = FollowRequest.objects.filter(follower=request.user.author, following=author).exists()
        if request.user.author.id != author.id and not request_exists:
            summary = f"{request.user.author.displayName} wants to follow {author.displayName}"
            fr = FollowRequest.objects.create(follower=request.user.author, following=author, summary=summary)
            if "restlessclients" not in author.host:
                # TODO: Bad url construction
                if "im-a-teapot" in author.host:
                    auth = ("teapot", "rooibos")
                    url = f"https://im-a-teapot-41db2c906820.herokuapp.com/authors/{author.pk}/inbox"
                elif "silk-cmput404" in author.host:
                    auth = ("restlessclients", "django100")
                    url = f"https://silk-cmput404-project-21e5c91727a7.herokuapp.com/api/authors/{author.pk}/inbox"
                
                fr_data = FollowRequestSerializer(fr).data
                resp = requests.post(url, json=fr_data, auth=auth)
                if resp.status_code >= 400:
                    fr.delete()
        # return redirect(reverse('project:profile', args=[pk]))
        return Response(status=status.HTTP_201_CREATED)


@login_required
def unfollow(request, pk):
    """Unfollow another author."""
    author = get_object_or_404(Author, pk=pk)
    if request.method == "POST":
        request.user.author.following.remove(author)
    return redirect(reverse('project:profile', args=[pk]))


@login_required
def decline_follow_request(request, pk):
    """Decline a follow request."""
    fr = get_object_or_404(FollowRequest, pk=pk)
    if request.method == "POST":
        fr.delete()
    return redirect(reverse('project:home'))


@login_required
def accept_follow_request(request, pk):
    """Accept a follow request."""
    fr = get_object_or_404(FollowRequest, pk=pk)
    if request.method == "POST":
        fr.follower.following.add(fr.following)
        fr.delete()
    return redirect(reverse('project:home'))


class SearchAuthors(APIView):
    """Search for an author by displayName."""

    #authentication_classes = [BasicAuthentication, SessionAuthentication]
    #permission_classes = [IsAuthenticated]

    def get_queryset(self):
        query = self.request.GET.get("username")
        try:
            response = requests.get("https://im-a-teapot-41db2c906820.herokuapp.com/api/authors/", auth=("teapot", "rooibos"))
            authorsList = response.json()["items"]
            for author in authorsList:
                if len(author["id"].split('/'))==5:
                    if not Author.objects.filter(id=author["id"].split('/')[4]).exists():
                        addOrGetRemoteAuthor(author)
                else:
                    if not Author.objects.filter(id=author["id"].split('/')[5]).exists():
                        addOrGetRemoteAuthor(author)
        except:
            # Catch in case of bad data
            print("im-a-teapot server is down")

        try:
            response2 = requests.get("https://silk-cmput404-project-21e5c91727a7.herokuapp.com/api/authors/", auth=("RESTless Clients", "RESTlessClients1!"))
            authorsList2 = response2.json()['data']

            for author in authorsList2:
                if not Author.objects.filter(id=author["id"].split('/')[5]).exists():
                    addOrGetRemoteAuthor(author)
        except:
            # Catch in case of bad data
            print("webcrawlers server is down")

        try:
            response3 = requests.get("https://cmput404-project-backend-tian-aaf1fa9b20e8.herokuapp.com/authors/", auth=("cross-server", "password"))
            authorsList3 = response3.json()['items']

            for author in authorsList3:
                if not Author.objects.filter(id=author["id"].split('/')[4]).exists():
                    addOrGetRemoteAuthor(author)
        except:
            # Catch in case of bad data
            print("ctrl+c and ctrl+v server is down")

        # TODO: remove example testcase for addOrGetRemoteCommentLike
        # resp = requests.get("https://restlessclients-7b4ebf6b9382.herokuapp.com/api/authors/a0cda9c8-5320-4757-acbb-3b7077820584/", auth=("grapevine", "socialwebgrape"))
        # print(resp.json())
        # author = addOrGetRemoteAuthor(resp.json())
        # print(author)
        # resp2 = requests.get("https://restlessclients-7b4ebf6b9382.herokuapp.com/api/authors/a0cda9c8-5320-4757-acbb-3b7077820584/posts/b06e75fb-868c-4dbe-9bf5-620397116625", auth=("grapevine", "socialwebgrape"))
        # post = addOrGetRemotePost(resp2.json(), author)
        # resp3 = requests.get("https://restlessclients-7b4ebf6b9382.herokuapp.com/api/authors/a0cda9c8-5320-4757-acbb-3b7077820584/posts/b06e75fb-868c-4dbe-9bf5-620397116625/comments/", auth=("grapevine", "socialwebgrape"))
        # commentsList = resp3.json()["comments"]
        # for comment in commentsList:
        #     comment = addOrGetRemoteComment(comment, post)
        #     resp4 = requests.get("https://restlessclients-7b4ebf6b9382.herokuapp.com/api/authors/a0cda9c8-5320-4757-acbb-3b7077820584/posts/b06e75fb-868c-4dbe-9bf5-620397116625/comments/396b79bb-0ce8-4803-9f69-02550829c1bf/likes", auth=("grapevine", "socialwebgrape"))
        #     for commentLike in resp4.json():
        #         commentLike = addOrGetRemoteCommentLike(commentLike, comment)

        
        if query == None:
            userlist = Author.objects.all().order_by('displayName')
            return userlist
        else:
            userlist = Author.objects.filter(displayName__icontains=query).order_by('displayName')
            return userlist


    def get(self, request, *args, **kwargs):
        """Return the serialized followers of the author."""
        auth_header = self.request.META.get('HTTP_AUTHORIZATION', '')
        token_type, _, credentials = auth_header.partition(' ')
        if token_type == "Basic" and not (Node.objects.filter(user=self.request.user).exists()):
            return Response({"detail": "Invalid authorization: access denied."}, status=401)

        query_set = self.get_queryset()
        serializer = AuthorSerializer(query_set, many=True)
        results = {
            "type": "authors",
            "items": serializer.data
        }
        return Response(results)


class FollowersAPIView(APIView):
    """Get the followers for a given author."""
    # authentication_classes = [BasicAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Get the followers for the author."""
        author = get_object_or_404(Author, pk=self.kwargs['pk'])
        return author.followers.all()
    
    def get(self, request, *args, **kwargs):
        """Return the serialized followers of the author."""
        auth_header = self.request.META.get('HTTP_AUTHORIZATION', '')
        token_type, _, credentials = auth_header.partition(' ')
        if token_type == "Basic" and not (Node.objects.filter(user=self.request.user).exists()):
            return Response({"detail": "Invalid authorization: access denied."}, status=401)

        query_set = self.get_queryset()
        serializer = AuthorSerializer(query_set, many=True)
        results = {
            "type": "followers",
            "items": serializer.data
        }
        return Response(results)


class FollowerAPIView(APIView):
    """API to access a single follower of an author"""
    # authentication_classes = [BasicAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        """Check if the author is a follower. 404 if not"""
        auth_header = self.request.META.get('HTTP_AUTHORIZATION', '')
        token_type, _, credentials = auth_header.partition(' ')
        if token_type == "Basic" and not (Node.objects.filter(user=self.request.user).exists()):
            return Response({"detail": "Invalid authorization: access denied."}, status=401)

        # Not sure what this should return in the response
        author = get_object_or_404(Author, pk=kwargs['pk'])
        follower = get_object_or_404(author.followers, pk=kwargs['follower_id'])
        serializer = AuthorSerializer(follower)
        return Response(serializer.data)
    
    # Restricted to local access.
    def put(self, request, *args, **kwargs):
        """Add a follower to the author if authenticated."""
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        token_type, _, credentials = auth_header.partition(' ')
        if token_type == "Basic":
            return Response({"detail": "Invalid authorization: access denied."}, status=401)
        else:
            author = get_object_or_404(Author, pk=kwargs['pk'])
            if author.user != request.user:
                return Response({"detail": "Invalid authorization: access denied."}, status=401)

            # Add to DB if necessary?
            follower = get_object_or_404(Author, pk=kwargs['follower_id'])
            author.followers.add(follower)
            return Response(status=status.HTTP_201_CREATED)

    # Restricted to local access.
    def delete(self, request, *args, **kwargs):
        """Remove an author from the followers of another if authenticated."""
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        token_type, _, credentials = auth_header.partition(' ')
        if token_type == "Basic":
            return Response({"detail": "Invalid authorization: access denied."}, status=401)
        else:
            author = get_object_or_404(Author, pk=kwargs['pk'])
            if author.user != request.user:
                return Response({"detail": "Invalid authorization: access denied."}, status=401)

            follower = get_object_or_404(author.followers, pk=kwargs['follower_id'])
            author.followers.remove(follower)
            return Response(status=status.HTTP_204_NO_CONTENT)
        

class FollowRequestAPIView(APIView):
    """Send or get the follow requests for an author"""
    # authentication_classes = [BasicAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """Retrieve the follow requests for an author"""
        auth_header = self.request.META.get('HTTP_AUTHORIZATION', '')
        token_type, _, credentials = auth_header.partition(' ')
        if token_type == "Basic" and not (Node.objects.filter(user=self.request.user).exists()):
            return Response({"detail": "Invalid authorization: access denied."}, status=401)

        author = get_object_or_404(Author, pk=kwargs['pk'])
        if author.user != request.user:
                return Response({"detail": "Invalid authorization: access denied."}, status=401)

        serializer = FollowRequestSerializer(FollowRequest.objects.filter(following=author), many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        """Create the follow request"""
        auth_header = self.request.META.get('HTTP_AUTHORIZATION', '')
        token_type, _, credentials = auth_header.partition(' ')
        if token_type == "Basic" and not (Node.objects.filter(user=self.request.user).exists()):
            return Response({"detail": "Invalid authorization: access denied."}, status=401)
        
        # Make sure author exists?
        author = get_object_or_404(Author, pk=kwargs['pk'])
        # Assumes other author is in the database?
        serializer = FollowRequestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(status=400, data=serializer.errors)


class CommentAPIView(ListCreateAPIView):
    """Get a list of comments for a post or add a comment."""
    # authentication_classes = [BasicAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    serializer_class = CommentSerializer
    pagination_class = CommentPagination

    # TODO test visibility
    def get_queryset(self):
        """Check that author and post exist and get comments
        in reverse chronological order.
        """
        auth_header = self.request.META.get('HTTP_AUTHORIZATION', '')
        token_type, _, credentials = auth_header.partition(' ')
        
        
        self.Error = False
        if token_type == "Basic" and not (Node.objects.filter(user=self.request.user).exists()):
            self.Error = True
    
    
    
    
    
        author = get_object_or_404(Author, pk=self.kwargs['author_id'])
        try:
            user = get_object_or_404(Author, user=self.request.user)
        except Http404:
            user = None

        self.post_obj = get_object_or_404(Post, pk=self.kwargs["post_id"])

        if self.post_obj.visibility == Post.VisibilityChoice.FRIENDS_ONLY and not author == user:
            # users can only see their own comments on friends only
            return self.post_obj.comment_set.all().filter(author=user).order_by('-published')
        else:
            return self.post_obj.comment_set.all().order_by('-published')






   
    # Restricted to local access.
    def post(self, request, *args, **kwargs):
        """Add a comment to a post if authenticated"""
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        token_type, _, credentials = auth_header.partition(' ')
        if token_type == "Basic":
            return Response({"detail": "Invalid authorization: access denied."}, status=401)
        else:
            data = {
                **request.data,
                'post': kwargs['post_id']
            }
            serializer = CommentSerializer(data=data)
            
            # TODO: Move validation responsibility to serializer
            if serializer.is_valid() and data['type'] == 'comment':
                serializer.save()
                return Response(serializer.data, status=201)
            return Response(status=400, data=serializer.errors)


class PostLikeAPIView(ListAPIView):
    """Get the likes on a specific post."""
    # authentication_classes = [BasicAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    serializer_class = PostLikeSerializer

    def get_queryset(self):
        """Check author and post exist and get likes"""
        auth_header = self.request.META.get('HTTP_AUTHORIZATION', '')
        token_type, _, credentials = auth_header.partition(' ')
        if token_type == "Basic" and not (Node.objects.filter(user=self.request.user).exists()):
            return Response({"detail": "Invalid authorization: access denied."}, status=401)

        author = get_object_or_404(Author, pk=self.kwargs['author_id'])
        post = get_object_or_404(Post, pk=self.kwargs["post_id"])
        return post.postlike_set.all()
    

class CommentLikeAPIView(ListAPIView):
    """Get the likes on a specific comment"""
    # authentication_classes = [BasicAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    serializer_class = CommentLikeSerializer

    def get_queryset(self):
        """Check author, post, and comment exist and get likes."""
        auth_header = self.request.META.get('HTTP_AUTHORIZATION', '')
        token_type, _, credentials = auth_header.partition(' ')
        if token_type == "Basic" and not (Node.objects.filter(user=self.request.user).exists()):
            return Response({"detail": "Invalid authorization: access denied."}, status=401)

        author = get_object_or_404(Author, pk=self.kwargs['author_id'])
        post = get_object_or_404(Post, pk=self.kwargs["post_id"])
        comment = get_object_or_404(Comment, pk=self.kwargs["comment_id"])
        return comment.commentlike_set.all()


class UserLikedAPIView(APIView):
    """Get the posts and comments that a specific user liked."""
    # authentication_classes = [BasicAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """Concatenate the liked posts and liked comments from the author."""
        auth_header = self.request.META.get('HTTP_AUTHORIZATION', '')
        token_type, _, credentials = auth_header.partition(' ')
        if token_type == "Basic" and not (Node.objects.filter(user=self.request.user).exists()):
            return Response({"detail": "Invalid authorization: access denied."}, status=401)

        author = get_object_or_404(Author, pk=kwargs['author_id'])
        if author.user != request.user:
                return Response({"detail": "Invalid authorization: access denied."}, status=401)

        postlikeserializer = PostLikeSerializer(author.postlike_set.filter(post__visibility=Post.VisibilityChoice.PUBLIC), many=True)
        commentlikeserializer = CommentLikeSerializer(author.commentlike_set.filter(comment__post__visibility=Post.VisibilityChoice.PUBLIC), many=True)
        results = {
            "type": "liked",
            "items": postlikeserializer.data + commentlikeserializer.data
        }
        return Response(results)


@login_required
def delete_post(request, **kwargs):
    """Delete a specific post."""
    post = get_object_or_404(Post, pk=kwargs['pk'])
    if request.method == 'POST' and post.author.id == request.user.author.id:
        print("DELETED!")
        post.delete()
    return redirect(reverse('project:home'))


class SharePostView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        token_type, _, credentials = auth_header.partition(' ')
        if token_type == "Basic":
            return Response({"detail": "Invalid authorization: access denied."}, status=401)
        new_post = {
            **request.data,
        }
        author = addOrGetRemoteAuthor(request.data['author'])
        new_post["source"] = f"{author.url}/posts/{new_post.pop('id')}"
        new_post["title"] = f"{new_post['author']['displayName']} posted: {new_post['title']}"
        new_post['author'] = request.user.author
        new_post.pop('like_count')
        new_post.pop('comment_count')
        new_post.pop('liked_by_me')
        post = create_post(new_post)
        return Response(status=status.HTTP_201_CREATED)

    
class NotificationAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer

    def get_queryset(self):
        auth_header = self.request.META.get('HTTP_AUTHORIZATION', '')
        token_type, _, credentials = auth_header.partition(' ')

        self.Error = False
        if token_type == "Basic" and not (Node.objects.filter(user=self.request.user).exists()):
            self.Error = True

        # 404 if invalid author
        author = get_object_or_404(Author, pk=self.kwargs['author_id'])
        return author.notification_set.all().order_by('-timestamp')
