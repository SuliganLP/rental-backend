from rest_framework import permissions


class BookingPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if view.action == "create":
            return request.user.role == "tenant"

        return True

    def has_object_permission(self, request, view, obj):
        user = request.user

        if view.action == "retrieve":
            return obj.tenant == user or obj.listing.owner == user

        if view.action in ("confirm", "reject"):
            return obj.listing.owner == user

        if view.action == "cancel":
            return obj.tenant == user

        return False
