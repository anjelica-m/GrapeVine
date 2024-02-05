from django.db.models import Count, Exists, OuterRef, Subquery, Func, F, IntegerField, Q
from django.shortcuts import get_object_or_404
from django.http import Http404
from rest_framework import viewsets, filters, response, status, permissions
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError

from . import models
from . import local_serializers as serializers
from .models import FollowRequest, PostLike, Comment, CommentLike, Post, Author
from .permissions import PostPermission
from .local_serializers import FollowRequestSerializer, CommentSerializer, AddCommentSerializer, PostRetrieveSerializer


class AuthorViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.AuthorSerializer
    queryset = models.Author.objects.all().order_by("displayName")
    filter_backends = [filters.SearchFilter]
    search_fields = ["user__username"]

    def get_object(self):
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        if self.kwargs[lookup_url_kwarg] == "me":
            return self.request.user.author

        return super().get_object()

    def get_queryset(self):
        qs = super().get_queryset()
        qs.prefetch_related("followers")
        return qs

    @action(detail=True, methods=["POST"])
    def follow_request(self, request, **kwargs):
        following = self.get_object()
        follower = self.request.user.author
        if following == follower:
            raise ValidationError("Authors cannot follow themselves")
        FollowRequest.objects.get_or_create(
            follower=follower, following=following, defaults={"summary": ""}
        )
        return response.Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["POST"])
    def unfollow(self, request, **kwargs):
        author = self.get_object()
        author.followers.remove(self.request.user.author)
        return response.Response(status=status.HTTP_204_NO_CONTENT)


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.UserSerializer
    queryset = models.User.objects.all()

    def get_object(self):
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        if self.kwargs[lookup_url_kwarg] == "me":
            return self.request.user

        return super().get_object()


class FollowRequestViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.FollowRequest.objects.all()
    serializer_class = FollowRequestSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(following=self.request.user.author)
        return qs

    @action(detail=True, methods=["POST"])
    def decline(self, *args, **kwargs):
        follow_request = self.get_object()
        follow_request.delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["POST"])
    def accept(self, *args, **kwargs):
        follow_request: FollowRequest = self.get_object()
        self.request.user.author.followers.add(follow_request.follower)
        follow_request.delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)


class PostViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.PostSerializer
    permission_classes = [permissions.IsAuthenticated, PostPermission]
    queryset = models.Post.objects.all().order_by("published")

    filterset_fields = ["author"]

    def get_queryset(self):
        qs = super().get_queryset()

        try:
            user = get_object_or_404(Author, user=self.request.user)
        except Http404:
            user = None

        if user == None:
            print("can'f find user for posts api")
            print("user", user)
            print("author", author)
            if self.action == "list":
                qs = qs.filter(unlisted=False)
            qs = qs.exclude(visibility=Post.VisibilityChoice.FRIENDS_ONLY)
            qs = qs.exclude(visibility=Post.VisibilityChoice.PRIVATE)            
        else:
            print("user is not author for posts api")
            if self.action == "list":
                qs = qs.filter(unlisted=False)
            qs = qs.exclude(Q(visibility=Post.VisibilityChoice.FRIENDS_ONLY) & ~(Q(author__followers=user) | Q(author=user)))
            qs = qs.exclude(Q(visibility=Post.VisibilityChoice.PRIVATE) & ~(Q(private_reciever=user) | Q(author=user)))

        like_count = PostLike.objects.filter(
            post=OuterRef("id")
        ).order_by().annotate(
            count=Func(F('id'), function='Count', output_field=IntegerField())
        ).values('count')

        comment_count = Comment.objects.filter(
            post=OuterRef("id")
        ).order_by().annotate(
            count=Func(F('id'), function='Count', output_field=IntegerField())
        ).values('count')

        qs = qs.annotate(
            like_count=Subquery(like_count),
            comment_count=Subquery(comment_count),
        )
        if self.action == 'retrieve':
            qs = qs.annotate(
                liked_by_me=Exists(PostLike.objects.filter(author=self.request.user.author, post=OuterRef("pk")))
            )
        return qs

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return PostRetrieveSerializer
        return super().get_serializer_class()

    @action(detail=True, methods=["POST"])
    def like(self, request, pk=None, **kwargs):
        PostLike.objects.get_or_create(author=request.user.author, post_id=pk)
        return response.Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["POST"])
    def unlike(self, request, pk=None, **kwargs):
        PostLike.objects.filter(author=request.user.author, post_id=pk).delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["GET"])
    def comments(self, request, pk=None, **kwargs):

        try:
            post = get_object_or_404(Post, pk=pk)
            post_author = post.author
            user = request.user.author
        except:
            post = None
            post_author = None
            user = request.user.author
    
        if post == None or (post.visibility == Post.VisibilityChoice.FRIENDS_ONLY and not post_author == user):
            # filter comments if friends only post or 
            like_count = CommentLike.objects.filter(
                comment=OuterRef("id")
            ).order_by().annotate(
                count=Func(F('id'), function='Count', output_field=IntegerField())
            ).values('count')

            comments = Comment.objects.filter(post_id=pk, author=user).annotate(
                like_count=Subquery(like_count),
                liked_by_me=Exists(CommentLike.objects.filter(author=request.user.author, comment=OuterRef("pk")))
            )
        else:
            like_count = CommentLike.objects.filter(
                comment=OuterRef("id")
            ).order_by().annotate(
                count=Func(F('id'), function='Count', output_field=IntegerField())
            ).values('count')
                    
            comments = Comment.objects.filter(post_id=pk).annotate(
                like_count=Subquery(like_count),
                liked_by_me=Exists(CommentLike.objects.filter(author=request.user.author, comment=OuterRef("pk")))
            )
    
        data = CommentSerializer(comments, many=True).data
        return response.Response(data=data)

    @action(detail=True, methods=["POST"])
    def comment(self, request, pk=None, **kwargs):
        serializer = AddCommentSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)
        instance = serializer.post_comment(post_id=pk, author_id=request.user.author.id)
        like_count = CommentLike.objects.filter(
            comment=OuterRef("id")
        ).order_by().annotate(
            count=Func(F('id'), function='Count', output_field=IntegerField())
        ).values('count')
        instance = Comment.objects.annotate(
            like_count=Subquery(like_count),
            liked_by_me=Exists(CommentLike.objects.filter(author=self.request.user.author, comment=OuterRef("pk")))
        ).get(pk=instance.pk)
        serializer = CommentSerializer(instance=instance)
        return response.Response(
            serializer.data, status=status.HTTP_201_CREATED
        )


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.CommentSerializer
    queryset = models.Comment.objects.all()

    @action(methods=["POST"], detail=True)
    def like(self, request, pk=None, **kwargs):
        CommentLike.objects.get_or_create(author=request.user.author, comment_id=pk)
        return response.Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=["POST"], detail=True)
    def unlike(self, request, pk=None, **kwargs):
        CommentLike.objects.filter(author=request.user.author, comment_id=pk).delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)
