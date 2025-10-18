"""
Organization permissions.

Role-based permissions for organization management, namespaces, and short URLs.
"""
from rest_framework import permissions
from django.shortcuts import get_object_or_404
from .models import Organization, OrganizationMembership
from apps.urls.models import Namespace, ShortURL


class IsOrganizationMember(permissions.BasePermission):
    """
    Permission to check if user is a member of the organization.
    """
    
    def has_permission(self, request, view):
        """Check if user is authenticated."""
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """Check if user is a member of the organization."""
        if isinstance(obj, Organization):
            organization = obj
        elif hasattr(obj, 'organization'):
            organization = obj.organization
        else:
            return False
        
        return (
            organization.owner == request.user or
            organization.memberships.filter(user=request.user).exists()
        )


class IsOrganizationAdmin(permissions.BasePermission):
    """
    Permission to check if user is an admin of the organization.
    """
    
    def has_permission(self, request, view):
        """Check if user is authenticated."""
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """Check if user is an admin of the organization."""
        if isinstance(obj, Organization):
            organization = obj
        elif hasattr(obj, 'organization'):
            organization = obj.organization
        else:
            return False
        
        return (
            organization.owner == request.user or
            organization.memberships.filter(
                user=request.user,
                role=OrganizationMembership.Role.ADMIN
            ).exists()
        )


class IsOrganizationEditorOrAdmin(permissions.BasePermission):
    """
    Permission to check if user is an editor or admin of the organization.
    """
    
    def has_permission(self, request, view):
        """Check if user is authenticated."""
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """Check if user is an editor or admin of the organization."""
        if isinstance(obj, Organization):
            organization = obj
        elif hasattr(obj, 'organization'):
            organization = obj.organization
        else:
            return False
        
        return (
            organization.owner == request.user or
            organization.memberships.filter(
                user=request.user,
                role__in=[
                    OrganizationMembership.Role.ADMIN,
                    OrganizationMembership.Role.EDITOR
                ]
            ).exists()
        )


class CanCreateNamespace(permissions.BasePermission):
    """
    Permission to check if user can create namespaces.
    Only admins can create namespaces.
    """
    
    def has_permission(self, request, view):
        """Check if user is authenticated."""
        return request.user and request.user.is_authenticated
    
    def has_permission_for_organization(self, request, organization):
        """Check if user can create namespaces in the organization."""
        return (
            organization.owner == request.user or
            organization.memberships.filter(
                user=request.user,
                role=OrganizationMembership.Role.ADMIN
            ).exists()
        )


class CanManageShortURL(permissions.BasePermission):
    """
    Permission to check if user can manage (create/edit/delete) short URLs.
    Admins and editors can manage short URLs.
    """
    
    def has_permission(self, request, view):
        """Check if user is authenticated."""
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """Check if user can manage the short URL."""
        if isinstance(obj, ShortURL):
            namespace = obj.namespace
        elif isinstance(obj, Namespace):
            namespace = obj
        else:
            return False
        
        organization = namespace.organization
        
        # Check if user is owner or has appropriate role
        if organization.owner == request.user:
            return True
        
        membership = organization.memberships.filter(user=request.user).first()
        if not membership:
            return False
        
        # Admins and editors can manage short URLs
        return membership.role in [
            OrganizationMembership.Role.ADMIN,
            OrganizationMembership.Role.EDITOR
        ]


class CanViewShortURL(permissions.BasePermission):
    """
    Permission to check if user can view short URLs.
    All organization members can view short URLs.
    """
    
    def has_permission(self, request, view):
        """Check if user is authenticated."""
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """Check if user can view the short URL."""
        if isinstance(obj, ShortURL):
            namespace = obj.namespace
        elif isinstance(obj, Namespace):
            namespace = obj
        else:
            return False
        
        organization = namespace.organization
        
        # All organization members can view short URLs
        return (
            organization.owner == request.user or
            organization.memberships.filter(user=request.user).exists()
        )


class CanInviteMembers(permissions.BasePermission):
    """
    Permission to check if user can invite members to the organization.
    Only admins can invite members.
    """
    
    def has_permission(self, request, view):
        """Check if user is authenticated."""
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """Check if user can invite members to the organization."""
        if isinstance(obj, Organization):
            organization = obj
        else:
            return False
        
        return (
            organization.owner == request.user or
            organization.memberships.filter(
                user=request.user,
                role=OrganizationMembership.Role.ADMIN
            ).exists()
        )


class CanManageMembers(permissions.BasePermission):
    """
    Permission to check if user can manage organization members.
    Only admins can manage members.
    """
    
    def has_permission(self, request, view):
        """Check if user is authenticated and has admin access to the organization."""
        if not (request.user and request.user.is_authenticated):
            return False
        
        # For list views, check if user is admin of the organization in the URL
        if hasattr(view, 'kwargs') and 'organization_pk' in view.kwargs:
            try:
                organization = Organization.objects.get(id=view.kwargs['organization_pk'])
                is_admin = (
                    organization.owner == request.user or
                    organization.memberships.filter(
                        user=request.user,
                        role=OrganizationMembership.Role.ADMIN
                    ).exists()
                )
                return is_admin
            except Organization.DoesNotExist:
                return False
        
        return True  # For other cases, let has_object_permission handle it
    
    def has_object_permission(self, request, view, obj):
        """Check if user can manage members of the organization."""
        if isinstance(obj, Organization):
            organization = obj
        elif hasattr(obj, 'organization'):
            organization = obj.organization
        else:
            return False
        
        return (
            organization.owner == request.user or
            organization.memberships.filter(
                user=request.user,
                role=OrganizationMembership.Role.ADMIN
            ).exists()
        )


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    
    def has_object_permission(self, request, view, obj):
        """Check if user is the owner of the object."""
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner of the object.
        return obj.created_by == request.user


class IsOrganizationOwnerOrAdmin(permissions.BasePermission):
    """
    Permission to check if user is the organization owner or an admin.
    """
    
    def has_permission(self, request, view):
        """Check if user is authenticated."""
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """Check if user is owner or admin of the organization."""
        if isinstance(obj, Organization):
            organization = obj
        elif hasattr(obj, 'organization'):
            organization = obj.organization
        else:
            return False
        
        return (
            organization.owner == request.user or
            organization.memberships.filter(
                user=request.user,
                role=OrganizationMembership.Role.ADMIN
            ).exists()
        )
