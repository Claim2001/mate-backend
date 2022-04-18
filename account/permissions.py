from rest_framework.generics import get_object_or_404
from rest_framework.permissions import BasePermission

from account.models import ProfileModel


class BoughtPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.user == request.user.id and obj.status:
            return True
        else:
            return False


class AdminPermission(BasePermission):
    def has_permission(self, request, view):
        if get_object_or_404(ProfileModel, user=request.user.id, permission=3):
            return True
        elif request.user.is_superuser:
            return True
        else:
            return False


class MentorPermission(BasePermission):
    def has_permission(self, request, view):
        if get_object_or_404(ProfileModel, user=request.user.id, permission=2):
            return True
        else:
            return False


class SAMPermission(BasePermission):
    def has_permission(self, request, view):
        pm = get_object_or_404(ProfileModel, user=request.user.id)
        if pm.permission == 1 or pm.permission == 2 or pm.permission == 3 or request.user.is_superuser:
            return True
        else:
            return False


class StudentPermission(BasePermission):
    def has_permission(self, request, view):
        if get_object_or_404(ProfileModel, user=request.user.id, permission=1):
            return True
        else:
            return False


class HighPermission(BasePermission):
    def has_permission(self, request, view):
        if get_object_or_404(ProfileModel, user=request.user.id, permission__gt=1):
            return True
        elif request.user.is_superuser:
            return True
        else:
            return False
