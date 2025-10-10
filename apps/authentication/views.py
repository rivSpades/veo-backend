"""
Authentication app views
Handles user registration, magic link authentication, and profile management
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
import secrets

from .models import MagicLink, UserSession
from .serializers import (
    UserSerializer,
    UserRegistrationSerializer,
    LoginSerializer,
    MagicLinkRequestSerializer,
    MagicLinkVerifySerializer,
    UserSessionSerializer,
    UserProfileUpdateSerializer
)

User = get_user_model()


class AuthViewSet(viewsets.GenericViewSet):
    """
    ViewSet for authentication operations
    Handles registration, magic link login, and logout
    """
    permission_classes = [AllowAny]

    @action(detail=False, methods=['post'], url_path='register')
    def register(self, request):
        """
        Register a new user
        POST /api/auth/register/
        Body: {email, name, phone?, language?, password}
        """
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response({
            'message': 'Registration successful. Please log in.',
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], url_path='login')
    def login(self, request):
        """
        Login with email and password
        POST /api/auth/login/
        Body: {email, password}
        """
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)

        # Create user session
        user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')
        ip_address = request.META.get('REMOTE_ADDR', '')
        device_type = 'mobile' if 'Mobile' in user_agent else 'desktop'

        UserSession.objects.create(
            user=user,
            token=str(refresh.access_token),
            refresh_token=str(refresh),
            user_agent=user_agent,
            device_type=device_type,
            ip_address=ip_address,
            expires_at=timezone.now() + timezone.timedelta(days=7)
        )

        return Response({
            'message': 'Login successful',
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserSerializer(user).data
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='request-magic-link')
    def request_magic_link(self, request):
        """
        Request a magic link for passwordless login
        POST /api/auth/request-magic-link/
        Body: {email}
        """
        serializer = MagicLinkRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        user = User.objects.get(email=email)

        # Generate magic link token
        token = secrets.token_urlsafe(32)
        expires_at = timezone.now() + timezone.timedelta(minutes=15)

        # Create magic link
        magic_link = MagicLink.objects.create(
            user=user,
            token=token,
            expires_at=expires_at
        )

        # Send email with magic link
        magic_url = f"{settings.FRONTEND_URL}/auth/verify?token={token}"

        send_mail(
            subject='Your VEOmenu Login Link',
            message=f'Click here to log in: {magic_url}\n\nThis link expires in 15 minutes.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )

        return Response({
            'message': 'Magic link sent to your email. Please check your inbox.',
            'expires_in_minutes': 15
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='verify-magic-link')
    def verify_magic_link(self, request):
        """
        Verify magic link token and return JWT tokens
        POST /api/auth/verify-magic-link/
        Body: {token}
        """
        serializer = MagicLinkVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = serializer.validated_data['token']
        magic_link = MagicLink.objects.get(token=token)

        # Mark magic link as used
        magic_link.is_used = True
        magic_link.save()

        # Generate JWT tokens
        refresh = RefreshToken.for_user(magic_link.user)

        # Create user session
        user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')
        ip_address = request.META.get('REMOTE_ADDR', '')
        device_type = 'mobile' if 'Mobile' in user_agent else 'desktop'

        UserSession.objects.create(
            user=magic_link.user,
            token=str(refresh.access_token),
            refresh_token=str(refresh),
            user_agent=user_agent,
            device_type=device_type,
            ip_address=ip_address,
            expires_at=timezone.now() + timezone.timedelta(days=7)
        )

        return Response({
            'message': 'Login successful',
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserSerializer(magic_link.user).data
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='logout', permission_classes=[IsAuthenticated])
    def logout(self, request):
        """
        Logout user and deactivate session
        POST /api/auth/logout/
        Headers: Authorization: Bearer <token>
        """
        # Get authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]

            # Deactivate user session
            UserSession.objects.filter(
                user=request.user,
                token=token,
                is_active=True
            ).update(is_active=False)

        return Response({
            'message': 'Logout successful'
        }, status=status.HTTP_200_OK)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for user operations
    Handles user profile viewing and updating
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='me')
    def me(self, request):
        """
        Get current user profile
        GET /api/users/me/
        """
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['put', 'patch'], url_path='update-profile')
    def update_profile(self, request):
        """
        Update current user profile
        PUT/PATCH /api/users/update-profile/
        Body: {name?, phone?, avatar?, language?, timezone?}
        """
        serializer = UserProfileUpdateSerializer(
            request.user,
            data=request.data,
            partial=request.method == 'PATCH'
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            'message': 'Profile updated successfully',
            'user': UserSerializer(request.user).data
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='sessions')
    def sessions(self, request):
        """
        Get all active sessions for current user
        GET /api/users/sessions/
        """
        sessions = UserSession.objects.filter(
            user=request.user,
            is_active=True
        ).order_by('-last_activity')

        serializer = UserSessionSerializer(sessions, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='revoke-session')
    def revoke_session(self, request):
        """
        Revoke a specific session
        POST /api/users/revoke-session/
        Body: {session_id}
        """
        session_id = request.data.get('session_id')

        if not session_id:
            return Response({
                'error': 'session_id is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        session = UserSession.objects.filter(
            id=session_id,
            user=request.user,
            is_active=True
        ).first()

        if not session:
            return Response({
                'error': 'Session not found or already revoked'
            }, status=status.HTTP_404_NOT_FOUND)

        session.is_active = False
        session.save()

        return Response({
            'message': 'Session revoked successfully'
        }, status=status.HTTP_200_OK)
