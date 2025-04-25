from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework import generics, permissions
from rest_framework.permissions import BasePermission
from .models import Task, Comment
from .serializers import TaskSerializer


class IsAdminUserJWT(BasePermission):
    """
    Allows access only to Admin users
    """
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == 'ADMIN'
        )


class IsAdminOrProjectAccess(BasePermission):
    """
    Admins can access all.
    Others can only access if they're in project.members or created_by.
    """
    def has_object_permission(self, request, view, obj):
        user = request.user

        if not user.is_authenticated:
            return False

        # Admin users can access all projects
        if user.role == 'ADMIN':
            return True

        # Allow read-only methods for Project Leads, Developers, and Clients assigned to the project
        if request.method in SAFE_METHODS:
            return user in obj.members.all() or obj.created_by == user

        # Only creator (typically PM) or user assigned to project can modify the project
        return obj.created_by == user or user in obj.members.all()


class IsProjectManagerOrAdmin(BasePermission):
    """
    Allows access to Project Managers and Admin users to perform create and update actions.
    """
    def has_permission(self, request, view):
        if request.method in ['POST', 'PUT', 'PATCH']:
            return request.user.role in ['ADMIN', 'PROJECT_MANAGER']
        return True  # Allow read-only methods for all authenticated users


class IsProjectLeadOrAssigned(BasePermission):
    """
    Allows access to the project lead and those assigned to the project.
    """
    def has_permission(self, request, view):
        project = view.get_object()
        return request.user in project.members.all() or request.user == project.created_by


class IsDeveloperAssigned(BasePermission):
    """
    Allows access to Developers only if they are assigned to the project.
    """
    def has_permission(self, request, view):
        project = view.get_object()
        return request.user in project.members.all()


class IsClientAssigned(BasePermission):
    """
    Allows access to Clients only if they are assigned to the project.
    """
    def has_permission(self, request, view):
        project = view.get_object()
        return request.user in project.members.all()


from rest_framework.permissions import BasePermission


class IsTechLeadAssigned(BasePermission):
    """
    Allows access to Tech Leads only if they are assigned to the project or task.
    """
    def has_permission(self, request, view):
        # Get the object being accessed (either a Task or a Project)
        if isinstance(view.get_object(), Comment):
            comment = view.get_object()
            # Check if the user is either the creator or assigned to the project or task related to the comment
            return request.user == comment.created_by or request.user in comment.project.members.all()
        return False


class IsAdminOrPMOrTL(BasePermission):
    def has_permission(self, request, view):
        return request.user.role in ['ADMIN', 'PROJECT_MANAGER', 'TECH_LEAD']


class IsDeveloperUpdatingOwnStatus(BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            request.user.role == 'DEVELOPER' and
            obj.assigned_to == request.user and
            request.method == 'PATCH' and
            'status' in request.data
        )
