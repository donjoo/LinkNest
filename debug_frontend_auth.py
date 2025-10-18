#!/usr/bin/env python3
"""
Debug script to test frontend authentication and invite creation.
"""
import os
import sys
import django
import requests
import json

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
os.environ.setdefault('DATABASE_URL', 'sqlite:///db.sqlite3')
os.environ.setdefault('CELERY_BROKER_URL', 'redis://localhost:6379/0')
os.environ.setdefault('DJANGO_EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
os.environ.setdefault('FRONTEND_BASE_URL', 'http://localhost:3000')
os.environ.setdefault('DJANGO_ACCOUNT_ALLOW_REGISTRATION', 'True')
os.environ.setdefault('USE_DOCKER', 'no')

django.setup()

from apps.users.models import User
from apps.organizations.models import Organization
from rest_framework_simplejwt.tokens import RefreshToken

def test_frontend_auth():
    """Test the frontend authentication flow."""
    
    # Get user and organization
    user = User.objects.get(email='admin@example.com')
    org = Organization.objects.get(name='Test Organization')
    
    print(f"User: {user.email}")
    print(f"Organization: {org.name} (ID: {org.id})")
    
    # Create JWT token
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    
    print(f"Access Token: {access_token}")
    
    # Test API endpoint
    url = f"http://localhost:8000/api/organizations/{org.id}/create_invite/"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }
    data = {
        'email': 'debug-test@example.com',
        'role': 'viewer'
    }
    
    print(f"Testing API endpoint: {url}")
    print(f"Headers: {headers}")
    print(f"Data: {data}")
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        print(f"Response Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 201:
            print("✅ API call successful!")
            invite_data = response.json()
            print(f"Created invite: {invite_data}")
        else:
            print("❌ API call failed!")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    
    # Test token validation
    print("\n--- Testing Token Validation ---")
    try:
        from rest_framework_simplejwt.tokens import AccessToken
        token = AccessToken(access_token)
        print(f"Token is valid: {token}")
        print(f"Token payload: {token.payload}")
    except Exception as e:
        print(f"Token validation failed: {e}")

if __name__ == "__main__":
    test_frontend_auth()
