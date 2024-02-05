"""
Module containing pagination classes for API requests and views.

Authors:
    Kai Luedemann
    Shalomi Hron
Date: 2023-11-18

Copyright 2023 RESTless Clients
Licensed under the MIT License

Sources:
"""

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CommentPagination(PageNumberPagination):
    """Paginate a list of comments and return a response."""
    page_size = 100
    page_size_query_param = 'size'
    max_page_size = 1000

    def paginate_queryset(self, queryset, request, view=None):
        """Obtain the URL of the post that the comment belongs to."""
        self.post_id = view.post_obj.get_url()
        self.Error = view.Error
        return super().paginate_queryset(queryset, request, view)

    def get_paginated_response(self, data):
        """Return the paginated response with additional fields"""
        if self.Error:
            return Response({"detail": "Invalid authorization: access denied."}, status=401)
        else:
            return Response({
                'type': 'comments',
                'id': f"{self.post_id}/comments",
                'post': self.post_id,
                'page': int(self.get_page_number(self.request, self)),
                'size': self.get_page_size(self.request),
                'comments': data
                })


class AuthorPagination(PageNumberPagination):
    """Paginate a list of authors and return a response"""
    page_size = 100
    page_size_query_param = 'size'
    max_page_size = 1000
    
    def paginate_queryset(self, queryset, request, view=None):
        self.Error = view.Error
        return super().paginate_queryset(queryset, request, view)

    def get_paginated_response(self, data):
        """Return the paginated response with type field."""
        if self.Error:
            return Response({"detail": "Invalid authorization: access denied."}, status=401)
        else:
            return Response({
                'type': 'authors',
                # 'page': int(self.get_page_number(self.request, self)),
                # 'size': self.get_page_size(self.request),
                'items': data
                })


class PostPagination(PageNumberPagination):
    """Paginate a list of posts and return a response."""
    page_size = 100
    page_size_query_param = 'size'
    max_page_size = 1000
    
    def paginate_queryset(self, queryset, request, view=None):
        self.Error = view.Error
        return super().paginate_queryset(queryset, request, view)

    def get_paginated_response(self, data):
        """Return the paginated response with type field."""
        if self.Error:
            return Response({"detail": "Invalid authorization: access denied."}, status=401)
        else:
            return Response({
                'type': 'posts',
                'items': data
                })


class InboxPagination(PageNumberPagination):
    """Paginate the posts in the inbox."""
    page_size = 100
    page_size_query_param = 'size'
    max_page_size = 1000
    
    def paginate_queryset(self, queryset, request, view=None):
        """Obtain the author string from the view"""
        self.author_string = view.author_str
        self.Basic = view.Basic
        return super().paginate_queryset(queryset, request, view)

    def get_paginated_response(self, data):
        """Return the paginated response with additional fields if authenticated."""
        if self.Basic:
            return Response({"detail": "Invalid authorization: access denied."}, status=401)
        else:
            return Response({
                'type': 'inbox',
                'author': self.author_string,
                'items': data
                })
