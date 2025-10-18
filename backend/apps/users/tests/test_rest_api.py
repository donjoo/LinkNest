import pytest
from django.contrib.auth import get_user_model  # pylint: disable=ungrouped-imports
from django.test.client import Client
from django.urls import reverse

from apps.organizations.models import Organization, OrganizationMembership

pytestmark = pytest.mark.django_db
User = get_user_model()


def test_login_failed_email_validation(client: Client):
    payload = {
        'email': '',
        'password': 'thanks123',
    }
    resp = client.post(reverse('rest_login'), data=payload)
    assert resp.status_code == 400, resp.json()


def test_user_signup(client: Client):
    payload = {
        'email': 'testuser@gmail.com',
        'password': 'randompassword123',
        'password_confirm': 'randompassword123',
    }

    resp = client.post(reverse('auth:register'), data=payload, status_code=201)
    assert resp.status_code == 201, resp.json()
    assert User.objects.filter(email=payload['email']).exists()


def test_user_signup_creates_organization(client: Client):
    """Test that user signup automatically creates an organization and membership."""
    payload = {
        'email': 'testuser@gmail.com',
        'first_name': 'John',
        'last_name': 'Doe',
        'password': 'randompassword123',
        'password_confirm': 'randompassword123',
    }

    resp = client.post(reverse('auth:register'), data=payload, status_code=201)
    assert resp.status_code == 201, resp.json()
    
    # Check that user was created
    user = User.objects.get(email=payload['email'])
    assert user.first_name == 'John'
    
    # Check that organization was created
    organization = Organization.objects.get(owner=user)
    assert organization.name == "John's Organization"
    
    # Check that membership was created with ADMIN role
    membership = OrganizationMembership.objects.get(user=user, organization=organization)
    assert membership.role == OrganizationMembership.Role.ADMIN


def test_user_signup_creates_organization_without_first_name(client: Client):
    """Test organization creation when user has no first name (uses email prefix)."""
    payload = {
        'email': 'testuser@gmail.com',
        'password': 'randompassword123',
        'password_confirm': 'randompassword123',
    }

    resp = client.post(reverse('auth:register'), data=payload, status_code=201)
    assert resp.status_code == 201, resp.json()
    
    # Check that user was created
    user = User.objects.get(email=payload['email'])
    
    # Check that organization was created with email prefix
    organization = Organization.objects.get(owner=user)
    assert organization.name == "testuser's Organization"
    
    # Check that membership was created with ADMIN role
    membership = OrganizationMembership.objects.get(user=user, organization=organization)
    assert membership.role == OrganizationMembership.Role.ADMIN
