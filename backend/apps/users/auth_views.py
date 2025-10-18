from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.core.mail import send_mail
from django.conf import settings

from .models import User
from .auth_serializers import RegisterSerializer, LoginSerializer, UserSerializer
from .otp_models import OTP


class RegisterView(generics.CreateAPIView):
    """
    View for user registration.
    Creates user account but keeps it inactive until email verification.
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Keep user inactive until email verification
        user.is_active = False
        user.save()
        
        # Generate OTP for email verification
        otp = OTP.generate_otp(user)
        
        # Send OTP email
        self._send_otp_email(user, otp)
        
        return Response({
            'message': 'Registration successful! Please check your email for verification code.',
            'user': {
                'id': str(user.id),
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_active': user.is_active
            },
            'otp_expires_at': otp.expires_at,
            'time_remaining': otp.get_time_remaining()
        }, status=status.HTTP_201_CREATED)

    def _send_otp_email(self, user, otp):
        """
        Send OTP code to user's email.
        """
        subject = 'Verify Your Email - LinkNest'
        
        message = f"""
        Hello {user.first_name or 'User'},

        Thank you for registering with LinkNest! Please use the following code to verify your email address:

        Verification Code: {otp.code}

        This code will expire in 10 minutes.

        If you didn't request this verification, please ignore this email.

        Best regards,
        The LinkNest Team
        """
        
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
        except Exception as e:
            # Log the error but don't expose it to the user
            print(f"Failed to send OTP email: {e}")
            # Don't raise exception here as user is already created


class LoginView(TokenObtainPairView):
    """
    View for user login using JWT.
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }
        }, status=status.HTTP_200_OK)


class TokenRefreshView(TokenRefreshView):
    """
    View for refreshing JWT tokens.
    """
    permission_classes = [AllowAny]


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    View for user logout (blacklist refresh token).
    """
    try:
        refresh_token = request.data["refresh"]
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({'message': 'Successfully logged out.'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': 'Invalid token.'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    """
    View for getting user profile.
    """
    serializer = UserSerializer(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)
