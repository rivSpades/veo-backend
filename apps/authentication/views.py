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
from datetime import timedelta
import secrets

from .models import MagicLink, UserSession, PhoneVerification
from .serializers import (
    UserSerializer,
    UserRegistrationSerializer,
    LoginSerializer,
    MagicLinkRequestSerializer,
    MagicLinkVerifySerializer,
    UserSessionSerializer,
    UserProfileUpdateSerializer,
    PhoneVerificationRequestSerializer,
    PhoneVerificationConfirmSerializer,
    PhoneVerificationSerializer
)
from .services import PhoneService, EmailService

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

        # Generate JWT tokens for automatic login
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        # Create user session
        UserSession.objects.create(
            user=user,
            token=access_token,
            refresh_token=refresh_token,
            expires_at=timezone.now() + timedelta(days=30),  # 30 days expiration
            is_active=True
        )

        # Send welcome email
        try:
            print(f"Attempting to send welcome email to {user.email}")
            email_service = EmailService()
            welcome_result = email_service.send_welcome_email(user.email, user.name)
            print(f"Welcome email result: {welcome_result}")
            
            # Log email result (don't fail registration if email fails)
            if not welcome_result['success']:
                print(f"Failed to send welcome email to {user.email}: {welcome_result.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"Error in welcome email sending: {str(e)}")
            # Don't fail registration for email issues

        return Response({
            'message': 'Registration successful. You are now logged in.',
            'user': UserSerializer(user).data,
            'access_token': access_token,
            'refresh_token': refresh_token
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

    @action(detail=False, methods=['post'], url_path='request-phone-verification', permission_classes=[IsAuthenticated])
    def request_phone_verification(self, request):
        """
        Request phone number verification via SMS
        POST /api/auth/request-phone-verification/
        Body: {phone_number}
        """
        serializer = PhoneVerificationRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        phone_service = PhoneService()
        result = phone_service.create_verification(request.user, serializer.validated_data['phone_number'])
        
        if result['success']:
            return Response({
                'message': 'Verification code sent to your phone number.',
                'verification_id': result['verification_id'],
                'phone_number': result['phone_number'],
                'expires_at': result['expires_at']
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': result['error'],
                'cooldown_remaining': result.get('cooldown_remaining', 0)
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='confirm-phone-verification', permission_classes=[IsAuthenticated])
    def confirm_phone_verification(self, request):
        """
        Confirm phone verification code
        POST /api/auth/confirm-phone-verification/
        Body: {verification_code}
        """
        serializer = PhoneVerificationConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        phone_service = PhoneService()
        result = phone_service.verify_code_for_user(
            request.user,
            serializer.validated_data['verification_code']
        )
        
        if result['success']:
            return Response({
                'message': result['message'],
                'user': UserSerializer(request.user).data
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': result['error']
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='phone-verification-cooldown', permission_classes=[IsAuthenticated])
    def phone_verification_cooldown(self, request):
        """
        Check phone verification cooldown status
        GET /api/auth/phone-verification-cooldown/
        """
        from .services import PhoneService
        
        phone_service = PhoneService()
        cooldown_minutes = 10
        
        # Check for recent verification (single entry per user)
        try:
            verification = PhoneVerification.objects.get(user=request.user)
            
            # If code has expired, mark it as verified to prevent it from being considered active
            if verification.expires_at < timezone.now() and not verification.is_verified:
                print(f"[COOLDOWN DEBUG] Code has expired, marking as verified to prevent reuse")
                verification.is_verified = True
                verification.save()
            
            time_remaining = (verification.created_at + timedelta(minutes=cooldown_minutes) - timezone.now()).total_seconds()
            
            print(f"[COOLDOWN DEBUG] User: {request.user.id}")
            print(f"[COOLDOWN DEBUG] Verification created_at: {verification.created_at}")
            print(f"[COOLDOWN DEBUG] Current time: {timezone.now()}")
            print(f"[COOLDOWN DEBUG] Time remaining: {time_remaining}")
            print(f"[COOLDOWN DEBUG] Is verified: {verification.is_verified}")
            print(f"[COOLDOWN DEBUG] Expires at: {verification.expires_at}")
            print(f"[COOLDOWN DEBUG] Code expired: {verification.expires_at < timezone.now()}")
            print(f"[COOLDOWN DEBUG] Has active code: {not verification.is_verified and verification.expires_at > timezone.now()}")
            
            if time_remaining > 0:
                print(f"[COOLDOWN DEBUG] Returning cooldown active: {int(time_remaining)} seconds")
                return Response({
                    'cooldown_active': True,
                    'cooldown_remaining': int(time_remaining),
                    'can_send': False,
                    'last_sent_at': verification.created_at,
                    'has_active_code': not verification.is_verified and verification.expires_at > timezone.now()
                }, status=status.HTTP_200_OK)
            else:
                # Cooldown expired but check if there's still an active code
                has_active_code = not verification.is_verified and verification.expires_at > timezone.now()
                print(f"[COOLDOWN DEBUG] Cooldown expired, has_active_code: {has_active_code}")
                return Response({
                    'cooldown_active': False,
                    'cooldown_remaining': 0,
                    'can_send': True,
                    'last_sent_at': verification.created_at,
                    'has_active_code': has_active_code
                }, status=status.HTTP_200_OK)
        except PhoneVerification.DoesNotExist:
            print(f"[COOLDOWN DEBUG] No verification found for user: {request.user.id}")
            return Response({
                'cooldown_active': False,
                'cooldown_remaining': 0,
                'can_send': True,
                'last_sent_at': None,
                'has_active_code': False
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
