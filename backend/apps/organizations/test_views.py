"""
Test views for debugging authentication issues.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model

User = get_user_model()


class TestAuthView(APIView):
    """Test view to debug authentication."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Test authentication."""
        return Response({
            'message': 'Authentication successful!',
            'user': {
                'id': str(request.user.id),
                'email': request.user.email,
                'is_authenticated': request.user.is_authenticated,
            }
        })


class TestInviteView(APIView):
    """Test view to debug invite creation."""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Test invite creation without email sending."""
        from .models import Organization, Invite
        
        # Get the first organization
        org = Organization.objects.first()
        if not org:
            return Response({'error': 'No organization found'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create invite without sending email
        invite = Invite.objects.create(
            organization=org,
            email=request.data.get('email', 'test@example.com'),
            role=request.data.get('role', 'viewer'),
            invited_by=request.user
        )
        
        return Response({
            'message': 'Invite created successfully!',
            'invite': {
                'id': str(invite.id),
                'email': invite.email,
                'role': invite.role,
                'token': invite.token,
            }
        })
