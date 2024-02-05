"""
Module containing serializers for model objects.

Authors:
    Kai Luedemann
    Shalomi Hron
Date: 2023-11-18

Copyright 2023 RESTless Clients
Licensed under the MIT License

Sources:
https://stackoverflow.com/questions/66340780/how-to-return-list-of-id-s-with-django-rest-framework-serializer
"""
from django.contrib.auth.models import User
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Author, FollowRequest, Post, Comment, PostLike, CommentLike, Node, Notification


class AuthorSerializer(serializers.ModelSerializer):
    """Serialize an author object.
    
    Fields:
        type - 'author'
        id - the author's UUID in URL form
        url - the author's URL
        host - the node that the author resides on
        displayName - the author's username
        github - the author's github link
        profileImage - a link to the author's externally hosted profile image
    
    Sources:
    https://stackoverflow.com/questions/66340780/how-to-return-list-of-id-s-with-django-rest-framework-serializer
    """
    id = serializers.SerializerMethodField('get_id_format')

    def get_id_format(self, obj):
        return obj.url

    class Meta:
        model = Author
        fields = ['type', 'id', 'url', 'host', 'displayName', 'github', 'profileImage']

    def create(self, validated_data):
        """
        Create and return a new `Author` instance, given the validated data
        """

        return Author.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `Author` instance, given the validated data
        """
        instance.user = validated_data.get('user', instance.user)
        instance.id = validated_data.get('id', instance.id)
        instance.url = validated_data.get('url', instance.url)
        instance.host = validated_data.get('host', instance.host)
        instance.displayName = validated_data.get('displayName', instance.displayName)
        instance.github = validated_data.get('github', instance.github)
        instance.profileImage = validated_data.get('profileImage', instance.profileImage)
        instance.save()
        return instance

    # def to_representation(self, instance):
    #     results = super().to_representation(instance)
    #     results['id'] = results['url']
    #     return results

    # def to_internal_value(self, data):
    #     data['id'] = data[]
    #     return super().to_internal_value(data)


class PostSerializer(serializers.ModelSerializer):
    """Serialize an author object.
    
    Fields:
        type - 'post'
        title - the post title
        id - the post's URL
        source - the link from where this Post was received
        origin - the link from which this Post originated
        description - a description of the post
        contentType - the content format of the post
            - can be plaintext, markdown or image?
        content - the post text
        author - the serialized author that created the post
        categories - list of categories that the post fits into
        count - the total number of comments on the post
        comments - the first page of up to 5 serialized comments on the post
            sorted in reverse chronological order
        published - the ISO 8601 timestamp when the post was published
        visibility - one of PUBLIC, PRIVATE, or FRIENDS ONLY; determines who can see the post
        unlisted - flag whether the post is discoverable by browsing

    Sources:
    https://stackoverflow.com/questions/68743630/how-to-serialize-the-foreign-key-field-in-django-rest-framework
    """

    class Meta:
        model = Post
        fields = ['type', 'title', 'id', 'source', 'origin', 'description', 'contentType', 'content', 'author',
                  'categories', 'count', 'published', 'visibility', 'unlisted']

    def create(self, validated_data):
        """
        Create and return a new `Post` instance, given the validated data
        """
        return Post.object.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `Post` instance, given the validated data
        """
        instance.title = validated_data.get('title', instance.title)
        instance.id = validated_data.get('id', instance.id)
        instance.source = validated_data.get('source', instance.source)
        instance.origin = validated_data.get('origin', instance.origin)
        instance.description = validated_data.get('description', instance.description)
        instance.contentType = validated_data.get('contentType', instance.contentType)
        instance.content = validated_data.get('content', instance.content)
        instance.author = validated_data.get('author', instance.author)
        instance.categories = validated_data.get('categories', instance.categories)
        instance.count = validated_data.get('count', instance.count)
        instance.published = validated_data.get('published', instance.published)
        instance.visibility = validated_data.get('visibility', instance.visibility)
        instance.unlisted = validated_data.get('unlisted', instance.unlisted)
        instance.save()
        return instance

    # https://stackoverflow.com/questions/68743630/how-to-serialize-the-foreign-key-field-in-django-rest-framework
    def to_representation(self, instance):
        representation = super().to_representation(instance)

        # author object
        author_field = representation["author"]
        author = Author.objects.get(id=author_field)
        representation["author"] = AuthorSerializer(author).data

        # id field
        representation['id'] = str(author.url) + '/posts/' + str(representation['id'])

        # comment objects
        if self.context.get("is_friend_only") and not self.context.get("user_is_author"):
            print("filtering comments on friends only post for", self.context.get("user"))
            comments = CommentSerializer(instance.comment_set.all().filter(author=self.context.get("user")).order_by("published"), many=True).data
        else:
            comments = CommentSerializer(instance.comment_set.all().order_by("published"), many=True).data

        representation["comments"] = representation["id"] + "/comments"
        representation["count"] = len(comments)
        comments = comments[:5]  # at most the top 5 most recent comments

        # commentsSrc is an optional field and can be missing if there are no comments
        if comments:
            representation["commentsSrc"] = {
                "type": "comments",
                "page": 1,
                "size": 5,
                "post": representation["id"],
                "id": representation["comments"],
                "comments": comments
            }
            
        # TODO do we need the private reciever field here?

        return representation


class NodeSerializer(serializers.ModelSerializer):
    """Serialize a node object.
    
    Fields:
        id - the URL of the node
        nodeName - the name of the node
        apiURL - the address to access the API service
        host - the IP of the node
    """

    class Meta:
        model = Node
        fields = ['id', 'nodeName', 'nodeCred', 'apiURL', 'host']

    def create(self, validated_data):
        """
        Create and return a new `Node` instance, given the validated data
        """
        return Node.object.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `Node` instance, given the validated data
        """
        instance.id = validated_data.get('id', instance.id)
        instance.nodeName = validated_data.get('nodeName', instance.nodeName)
        instance.nodeCred = validated_data.get('nodeCred', instance.nodeCred)
        instance.apiURL = validated_data.get('apiURL', instance.apiURL)
        instance.host = validated_data.get('host', instance.host)


class FollowRequestSerializer(serializers.ModelSerializer):
    """Serialize a FollowRequest object.

    Fields:
        type - "Follow"
        id - the URL of the FollowRequest
        summary - a short note to be sent with the FollowRequest
        follower - the serialized author that sent the FollowRequest
        following - the serialized author that received the FollowRequest
    """
    follower = AuthorSerializer()
    following = AuthorSerializer()

    class Meta:
        model = FollowRequest
        fields = ["summary", "follower", "following"]

    def create(self, validated_data):
        follower = Author.objects.get(**validated_data["follower"])
        following = Author.objects.get(**validated_data["following"])

        summary = validated_data["summary"]
        return FollowRequest.objects.create(follower=follower, following=following, summary=summary)

    def to_representation(self, instance):
        results = super().to_representation(instance)
        results["type"] = "Follow"
        results["actor"] = results.pop("follower", {})
        results["object"] = results.pop("following", {})
        return results

    def to_internal_value(self, data):
        data["follower"] = data.pop("actor", {})
        data["following"] = data.pop("object", {})

        return super().to_internal_value(data)


class CommentSerializer(serializers.ModelSerializer):
    """Serialize a comment object.
    
    Attributes:
        type - "comment"
        author - the serialized author who wrote the comment
        comment - the content of the comment
        contentType - the format of the comment
            - can be plaintext or markdown
        published - the ISO 8601 timestamp when the comment was posted
        id - the URL of the comment
    """
    author = AuthorSerializer()

    class Meta:
        model = Comment
        fields = ['author', 'comment', 'contentType', 'published', 'post']

    def create(self, validated_data):
        id1 = validated_data['author']['url'].split('/')[-1]
        author_obj = get_object_or_404(Author, pk=id1, **validated_data["author"])
        data = {
            **validated_data,
            'author': author_obj,
        }
        return Comment.objects.create(**data)

    def to_representation(self, instance):
        results = super().to_representation(instance)
        results["type"] = "comment"
        results["id"] = instance.get_url()
        results.pop('post')
        return results


class PostLikeSerializer(serializers.ModelSerializer):
    """Serialize a PostLike object.

    Fields:
        type - "Like"
        @context - ??? (http://niem.github.io/json/reference/json-ld/context/)
        summary - a short note sent with the like
        author - the serialized author who liked the post
        object - the post that was liked
    """
    author = AuthorSerializer()

    class Meta:
        model = PostLike
        fields = ['author', 'post', 'summary', 'context']

    def create(self, validated_data):
        id1 = validated_data['author']['url'].split('/')[-1]
        author_obj = get_object_or_404(Author, pk=id1, **validated_data["author"])
        data = {
            **validated_data,
            'author': author_obj,
        }
        return PostLike.objects.create(**data)

    def to_representation(self, instance):
        results = super().to_representation(instance)
        results["type"] = "Like"
        results.pop('post')
        results['author'] = AuthorSerializer(instance.author).data
        results["object"] = instance.post.get_url()
        results["@context"] = results.pop('context', {})
        return results

    def to_internal_value(self, data):
        data["context"] = data.pop('@context', {})
        return super().to_internal_value(data)


class CommentLikeSerializer(serializers.ModelSerializer):
    """Serialize a CommentLike object.

    Fields:
        type - "Like"
        @context - ??? (http://niem.github.io/json/reference/json-ld/context/)
        summary - a short note sent with the like
        author - the serialized author who liked the post
        object - the comment that was liked
    """
    author = AuthorSerializer()

    class Meta:
        model = CommentLike
        fields = ['author', 'comment', 'summary', 'context']

    def create(self, validated_data):
        id1 = validated_data['author']['url'].split('/')[-1]
        author_obj = get_object_or_404(Author, pk=id1, **validated_data["author"])
        data = {
            **validated_data,
            'author': author_obj,
        }
        return CommentLike.objects.create(**data)

    def to_representation(self, instance):
        results = super().to_representation(instance)
        results["type"] = "Like"
        results.pop('comment')
        results['author'] = AuthorSerializer(instance.author).data
        results["object"] = instance.comment.get_url()
        results["@context"] = results.pop('context', {})
        return results

    def to_internal_value(self, data):
        data["context"] = data.pop('@context', {})
        return super().to_internal_value(data)


class UserSignUpSerializer(serializers.Serializer):
    username = serializers.CharField()
    github = serializers.CharField(required=False)
    password1 = serializers.CharField()
    password2 = serializers.CharField()

    def validate_github(self, value):
        if not value:
            return value
        if not value.startswith("https://github.com/"):
            raise serializers.ValidationError("Github must be URL")
        return value

    def validate(self, data):
        # Check if passwords match
        if data["password1"] != data["password2"]:
            raise serializers.ValidationError("Passwords must match.")
        return data

    def perform(self):
        vd = self.validated_data
        github = vd.pop("github", "")
        request = self.context["request"]
        host = request.get_host()
        with transaction.atomic():
            user = User.objects.create_user(
                username=vd["username"], password=vd["password1"], is_active=False
            )
            author = Author.objects.create(
                user=user,
                github=github,
                host='https://' + host + '/',
                displayName=user.username,
            )
            author.url = 'https://' + host + '/authors/' + str(author.id)
            author.save()
        return user

class NotificationSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Notification
        fields = ['message', 'link']