from rest_framework import permissions

from project.models import Post


class PostPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj: Post):
        if view.action in ["destroy", "update", "partial_update"]:
            return obj.author == request.user.author
        return True