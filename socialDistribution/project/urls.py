"""
Module containing URL patterns for the project app.

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
"""
from django.conf.urls.static import static
from django.urls import path, include
from rest_framework.routers import SimpleRouter

from . import views, viewsets
from rest_framework import permissions, routers
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from .viewsets import AuthorViewSet, PostViewSet

app_name = 'project'

# Reference: https://www.jasonmars.org/2020/04/22/add-swagger-to-django-rest-api-quickly-4-mins-without-hiccups/
schema_view = get_schema_view(
    openapi.Info(
        title="Grapevine API",
        default_version='v1',
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

router = routers.SimpleRouter()
router.register("users", viewsets.UserViewSet, basename="user")
router.register("authors", viewsets.AuthorViewSet, basename="author")
router.register("posts", viewsets.PostViewSet, basename="post")
router.register("follow-requests", viewsets.FollowRequestViewSet, basename="follow-request")
router.register("comments", viewsets.CommentViewSet, basename="comment")


urlpatterns = [
  # Swagger OpenAPI documentation
  path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
  path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
  # Stream
  path('<str:username>/stream', views.StreamView.as_view(), name='stream'),
  # Author
#   path('authors/<str:pk>', views.AuthorView.as_view(), name="author"),
  # Post

  # path('posts/<str:pk>', views.PostView.as_view(), name="post"),

  path('create-post', views.CreatePostView.as_view(), name='create-post'),
  path('edit-post/<str:pk>', views.EditPostView.as_view(), name='edit-post'),
  # Profile
  path('authors/<str:pk>', views.ProfileView.as_view(), name='profile'),
  # Edit Profile
  path('edit/', views.profile_edit, name='profile_edit'),
  # Homepage
  path('', views.stream_view, name='home'),
  # Signup


  # Author APIs
  path('api/authors/', views.AuthorAPIView.as_view(), name='get_authors'),
  path('api/authors/<str:pk>/', views.UpdateAuthorApiView.as_view(), name='author_api'),
  # Post APIs
  path('api/authors/<str:pk>/posts/', views.PostsAPIView.as_view(), name='posts_api'),
  path('api/authors/<str:pk>/posts/<str:post_id>', views.SinglePostApiView.as_view(), name='single_post_api'),
  # Inbox API
  path('api/authors/<str:pk>/inbox', views.InboxAPIView.as_view(), name='inbox_api'),
  # Node API
  path('api/nodes/', views.NodeAPIView.as_view(), name='node_api'),

  # Likes
  path('authors/<str:author_id>/posts/<str:pk>/like/', views.like_post, name='like_post'),
  path('post/<str:pk>/likeCom/', views.like_comment, name='like_comment'),
  # Comments
  path('authors/<str:author_id>/posts/<str:pk>/comment/', views.add_comment, name='add_comment'),
  # Follow
  path('authors/<str:pk>/follow/', views.FollowRequestSendView.as_view(), name='follow'),
  # Accept follow request
  path('followrequest/<str:pk>/accept/', views.accept_follow_request, name="accept_follow"),
  # Decline follow request
  path('followrequest/<str:pk>/decline/', views.decline_follow_request, name="decline_follow"),
  # Decline follow request
  path('author/<str:pk>/unfollow/', views.unfollow, name="unfollow"),
  #path('search/', views.SearchAuthors.as_view(), name='search'),
  # Follow API
  path('api/authors/<str:pk>/followers/', views.FollowersAPIView.as_view(), name="get_followers"),
  path('api/authors/<str:pk>/followers/<str:follower_id>', views.FollowerAPIView.as_view(), name="api_follower"),
  path('api/authors/<str:pk>/inbox/followrequest', views.FollowRequestAPIView.as_view(), name="api_follow_request"),
  # Comment API
  path('api/authors/<str:author_id>/posts/<str:post_id>/comments/', views.CommentAPIView.as_view(), name="comment_api"),
  # Like API
  path('api/authors/<str:author_id>/posts/<str:post_id>/likes', views.PostLikeAPIView.as_view(), name="api_post_likes"),
  path('api/authors/<str:author_id>/posts/<str:post_id>/comments/<str:comment_id>/likes', views.CommentLikeAPIView.as_view(), name="api_comment_likes"),
  path('api/authors/<str:author_id>/liked', views.UserLikedAPIView.as_view(), name="api_user_liked"),
  # Delete post
  path('post/<str:pk>/delete', views.delete_post, name="post_delete"),
  path('api/local/', include(router.urls)),
  path("api/local/signup/", views.SignUpView.as_view(), name="signup"),
  # Share post
  path('api/posts/<str:post_id>/share', views.SharePostView.as_view(), name="share_post"),
  # Notifications API
  path('api/authors/<str:author_id>/notifications', views.NotificationAPIView.as_view(), name="notifications_api"),
  
  path('api/search', views.SearchAuthors.as_view(), name="search_authors"),
  path('api/authors/<str:pk>/profile', views.ProfileAPIView.as_view(), name="profile_api"),
  path('api/authors/<str:author_id>/posts/<str:post_id>/create_comment', views.AddCommentView.as_view(), name="create_comment")
]
