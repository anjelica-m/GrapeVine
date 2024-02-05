from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

# Add your serializers here.
from .models import Author, FollowRequest, Post, Node, Comment


class CommentAuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ["id", "url", "host", "displayName", "github", "profileImage"]


class FollowerUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username"]


class FollowerAuthorSerializer(serializers.ModelSerializer):
    user = FollowerUserSerializer()

    class Meta:
        model = Author
        fields = ["id", "user", "profileImage", "displayName"]




class AuthorSerializer(serializers.ModelSerializer):
    followers = FollowerAuthorSerializer(many=True)
    user = FollowerUserSerializer()

    class Meta:
        model = Author
        fields = ["id", "url", "host", "displayName", "github", "profileImage", "followers", "user"]


class PostSerializer(serializers.ModelSerializer):
    like_count = serializers.IntegerField(required=False)
    comment_count = serializers.IntegerField(required=False)
    author = AuthorSerializer(required=False)

    max_content_length = 600

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "description",
            "content",
            "categories",
            "visibility",
            "unlisted",
            "source",
            "origin",
            "contentType",
            "count",
            "published",
            "author",
            "like_count",
            "comment_count",
        ]
        read_only_fields = [
            "author",
            "origin",
            "source",
            "published",
            "like_count",
            "comment_count",
        ]

    def validate(self, attrs):
        if attrs["contentType"].startswith("text/"):
            if len(attrs["content"]) > self.max_content_length:
                raise ValidationError(f"Text content cannot exceed {self.max_content_length}")
        return attrs

    def create(self, validated_data):
        validated_data["author"] = self.context["request"].user.author
        validated_data["source"] = "http://127.0.0.1:8000/"
        validated_data["origin"] = "http://127.0.0.1:8000/"
        validated_data["count"] = 0
        validated_data["published"] = timezone.now()
        return super().create(validated_data)


class PostRetrieveSerializer(PostSerializer):
    liked_by_me = serializers.BooleanField(required=False)

    class Meta(PostSerializer.Meta):
        fields = [
            *PostSerializer.Meta.fields,
            "liked_by_me",
        ]
        read_only_fields = [
            *PostSerializer.Meta.fields,
            "liked_by_me"
        ]


class CommentSerializer(serializers.ModelSerializer):
    author = CommentAuthorSerializer()
    like_count = serializers.IntegerField(required=False)
    liked_by_me = serializers.BooleanField(required=False)
    class Meta:
        model = Comment
        fields = [
            'author',
            'comment',
            'contentType',
            'published',
            'id',
            'post',
            'like_count',
            'liked_by_me'
        ]


class AddCommentSerializer(serializers.Serializer):
    comment = serializers.CharField()

    def post_comment(self, post_id, author_id):
        return Comment.objects.create(
            author_id=author_id,
            post_id=post_id,
            contentType="text/markdown",
            comment=self.validated_data["comment"]
        )


class NodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Node
        fields = ["id", "nodeName", "apiURL", "host"]

    def create(self, validated_data):
        """
        Create and return a new `Node` instance, given the validated data
        """
        return Node.object.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `Node` instance, given the validated data
        """
        instance.id = validated_data.get("id", instance.id)
        instance.nodeName = validated_data.get("nodeName", instance.nodeName)
        instance.apiURL = validated_data.get("apiURL", instance.apiURL)
        instance.host = validated_data.get("host", instance.host)


class FollowRequestSerializer(serializers.ModelSerializer):
    follower = FollowerAuthorSerializer()

    class Meta:
        model = FollowRequest
        fields = ["summary", "follower", "id"]


class UserSerializer(serializers.ModelSerializer):
    author = AuthorSerializer()

    class Meta:
        model = User
        fields = ["author", "username", "first_name", "last_name", "id"]


class UserSignUpSerializer(serializers.Serializer):
    username = serializers.CharField()
    github = serializers.CharField(required=False)
    password1 = serializers.CharField()
    password2 = serializers.CharField()

    def validate_github(self, value):
        if not value:
            return value
        if not value.startswith("https://github.com/"):
            raise ValidationError("Github must be URL")
        return value

    def validate(self, data):
        # Check if passwords match
        if data["password1"] != data["password2"]:
            raise serializers.ValidationError("Passwords must match.")
        return data

    def perform(self):
        vd = self.validated_data
        github = vd.pop("github", "")
        with transaction.atomic():
            user = User.objects.create_user(
                username=vd["username"], password=vd["password1"]
            )
            Author.objects.create(user=user, github=github)
        return user
