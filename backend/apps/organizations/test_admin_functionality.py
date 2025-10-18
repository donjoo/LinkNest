"""
Test Admin Role Functionality.

Comprehensive tests for the admin role implementation.
"""
import json
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Organization, OrganizationMembership, Invite
from apps.urls.models import Namespace, ShortURL

User = get_user_model()


class AdminRoleFunctionalityTest(APITestCase):
    """Test cases for admin role functionality."""

    def setUp(self):
        """Set up test data."""
        # Create users
        self.admin_user = User.objects.create_user(
            email='admin@example.com',
            password='testpass123',
            first_name='Admin',
            last_name='User'
        )
        
        self.editor_user = User.objects.create_user(
            email='editor@example.com',
            password='testpass123',
            first_name='Editor',
            last_name='User'
        )
        
        self.viewer_user = User.objects.create_user(
            email='viewer@example.com',
            password='testpass123',
            first_name='Viewer',
            last_name='User'
        )
        
        self.regular_user = User.objects.create_user(
            email='regular@example.com',
            password='testpass123',
            first_name='Regular',
            last_name='User'
        )
        
        # Create organization
        self.organization = Organization.objects.create(
            name='Test Organization',
            owner=self.admin_user
        )
        
        # Create memberships
        OrganizationMembership.objects.create(
            user=self.admin_user,
            organization=self.organization,
            role=OrganizationMembership.Role.ADMIN
        )
        
        OrganizationMembership.objects.create(
            user=self.editor_user,
            organization=self.organization,
            role=OrganizationMembership.Role.EDITOR
        )
        
        OrganizationMembership.objects.create(
            user=self.viewer_user,
            organization=self.organization,
            role=OrganizationMembership.Role.VIEWER
        )
        
        # Create namespace
        self.namespace = Namespace.objects.create(
            organization=self.organization,
            name='test-namespace',
            description='Test namespace'
        )
        
        # Create short URL
        self.short_url = ShortURL.objects.create(
            namespace=self.namespace,
            original_url='https://example.com',
            short_code='test123',
            created_by=self.admin_user,
            title='Test URL'
        )

    def get_auth_headers(self, user):
        """Get authentication headers for a user."""
        refresh = RefreshToken.for_user(user)
        return {
            'HTTP_AUTHORIZATION': f'Bearer {refresh.access_token}'
        }

    def test_admin_can_create_namespace(self):
        """Test that admin can create namespaces."""
        url = reverse('api:namespace-list')
        data = {
            'organization': str(self.organization.id),
            'name': 'admin-namespace',
            'description': 'Admin created namespace'
        }
        
        response = self.client.post(
            url, 
            data, 
            **self.get_auth_headers(self.admin_user)
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Namespace.objects.filter(name='admin-namespace').exists()
        )

    def test_editor_cannot_create_namespace(self):
        """Test that editor cannot create namespaces."""
        url = reverse('api:namespace-list')
        data = {
            'organization': str(self.organization.id),
            'name': 'editor-namespace',
            'description': 'Editor created namespace'
        }
        
        response = self.client.post(
            url, 
            data, 
            **self.get_auth_headers(self.editor_user)
        )
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_viewer_cannot_create_namespace(self):
        """Test that viewer cannot create namespaces."""
        url = reverse('api:namespace-list')
        data = {
            'organization': str(self.organization.id),
            'name': 'viewer-namespace',
            'description': 'Viewer created namespace'
        }
        
        response = self.client.post(
            url, 
            data, 
            **self.get_auth_headers(self.viewer_user)
        )
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_invite_members(self):
        """Test that admin can invite members."""
        url = reverse('api:organization-create-invite', kwargs={'pk': self.organization.id})
        data = {
            'email': 'newuser@example.com',
            'role': 'editor'
        }
        
        response = self.client.post(
            url, 
            data, 
            **self.get_auth_headers(self.admin_user)
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Invite.objects.filter(
                email='newuser@example.com',
                organization=self.organization
            ).exists()
        )

    def test_editor_cannot_invite_members(self):
        """Test that editor cannot invite members."""
        url = reverse('api:organization-create-invite', kwargs={'pk': self.organization.id})
        data = {
            'email': 'newuser@example.com',
            'role': 'viewer'
        }
        
        response = self.client.post(
            url, 
            data, 
            **self.get_auth_headers(self.editor_user)
        )
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_create_short_urls(self):
        """Test that admin can create short URLs."""
        url = reverse('api:shorturl-list')
        data = {
            'namespace': str(self.namespace.id),
            'original_url': 'https://admin-example.com',
            'short_code': 'admin123',
            'title': 'Admin URL'
        }
        
        response = self.client.post(
            url, 
            data, 
            **self.get_auth_headers(self.admin_user)
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            ShortURL.objects.filter(short_code='admin123').exists()
        )

    def test_editor_can_create_short_urls(self):
        """Test that editor can create short URLs."""
        url = reverse('api:shorturl-list')
        data = {
            'namespace': str(self.namespace.id),
            'original_url': 'https://editor-example.com',
            'short_code': 'editor123',
            'title': 'Editor URL'
        }
        
        response = self.client.post(
            url, 
            data, 
            **self.get_auth_headers(self.editor_user)
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            ShortURL.objects.filter(short_code='editor123').exists()
        )

    def test_viewer_cannot_create_short_urls(self):
        """Test that viewer cannot create short URLs."""
        url = reverse('api:shorturl-list')
        data = {
            'namespace': str(self.namespace.id),
            'original_url': 'https://viewer-example.com',
            'short_code': 'viewer123',
            'title': 'Viewer URL'
        }
        
        response = self.client.post(
            url, 
            data, 
            **self.get_auth_headers(self.viewer_user)
        )
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_view_all_short_urls(self):
        """Test that admin can view all short URLs in organization."""
        # Create another short URL by editor
        ShortURL.objects.create(
            namespace=self.namespace,
            original_url='https://editor-example.com',
            short_code='editor456',
            created_by=self.editor_user,
            title='Editor URL 2'
        )
        
        url = reverse('api:organization-short-urls', kwargs={'pk': self.organization.id})
        
        response = self.client.get(
            url, 
            **self.get_auth_headers(self.admin_user)
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Admin should see both URLs
        self.assertEqual(len(response.data), 2)

    def test_editor_can_only_view_own_short_urls(self):
        """Test that editor can only view their own short URLs."""
        # Create another short URL by admin
        ShortURL.objects.create(
            namespace=self.namespace,
            original_url='https://admin-example.com',
            short_code='admin456',
            created_by=self.admin_user,
            title='Admin URL 2'
        )
        
        url = reverse('api:organization-short-urls', kwargs={'pk': self.organization.id})
        
        response = self.client.get(
            url, 
            **self.get_auth_headers(self.editor_user)
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Editor should only see their own URL (none in this case)
        self.assertEqual(len(response.data), 0)

    def test_admin_can_manage_members(self):
        """Test that admin can manage organization members."""
        url = reverse('api:organizations:organization-members-list', kwargs={'organization_pk': self.organization.id})
        
        response = self.client.get(
            url, 
            **self.get_auth_headers(self.admin_user)
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)  # admin, editor, viewer

    def test_editor_cannot_manage_members(self):
        """Test that editor cannot manage organization members."""
        url = reverse('api:organizations:organization-members-list', kwargs={'organization_pk': self.organization.id})
        
        response = self.client.get(
            url, 
            **self.get_auth_headers(self.editor_user)
        )
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_update_member_role(self):
        """Test that admin can update member roles."""
        membership = OrganizationMembership.objects.get(
            user=self.editor_user,
            organization=self.organization
        )
        
        url = reverse('api:organizations:organization-members-detail', kwargs={
            'organization_pk': self.organization.id,
            'pk': membership.id
        })
        data = {'role': 'viewer'}
        
        response = self.client.patch(
            url, 
            data, 
            **self.get_auth_headers(self.admin_user)
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        membership.refresh_from_db()
        self.assertEqual(membership.role, 'viewer')

    def test_admin_cannot_change_owner_role(self):
        """Test that admin cannot change organization owner's role."""
        membership = OrganizationMembership.objects.get(
            user=self.admin_user,
            organization=self.organization
        )
        
        url = reverse('api:organizations:organization-members-detail', kwargs={
            'organization_pk': self.organization.id,
            'pk': membership.id
        })
        data = {'role': 'viewer'}
        
        response = self.client.patch(
            url, 
            data, 
            **self.get_auth_headers(self.admin_user)
        )
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_remove_members(self):
        """Test that admin can remove members from organization."""
        membership = OrganizationMembership.objects.get(
            user=self.viewer_user,
            organization=self.organization
        )
        
        url = reverse('api:organizations:organization-members-detail', kwargs={
            'organization_pk': self.organization.id,
            'pk': membership.id
        })
        
        response = self.client.delete(
            url, 
            **self.get_auth_headers(self.admin_user)
        )
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            OrganizationMembership.objects.filter(
                user=self.viewer_user,
                organization=self.organization
            ).exists()
        )

    def test_admin_cannot_remove_owner(self):
        """Test that admin cannot remove organization owner."""
        membership = OrganizationMembership.objects.get(
            user=self.admin_user,
            organization=self.organization
        )
        
        url = reverse('api:organizations:organization-members-detail', kwargs={
            'organization_pk': self.organization.id,
            'pk': membership.id
        })
        
        response = self.client.delete(
            url, 
            **self.get_auth_headers(self.admin_user)
        )
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_view_organization_namespaces(self):
        """Test that admin can view all organization namespaces."""
        url = reverse('api:organization-namespaces', kwargs={'pk': self.organization.id})
        
        response = self.client.get(
            url, 
            **self.get_auth_headers(self.admin_user)
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'test-namespace')

    def test_regular_user_cannot_access_organization(self):
        """Test that regular user cannot access organization they're not a member of."""
        url = reverse('api:organization-detail', kwargs={'pk': self.organization.id})
        
        response = self.client.get(
            url, 
            **self.get_auth_headers(self.regular_user)
        )
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
