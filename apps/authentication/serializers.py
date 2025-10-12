"""
Authentication app serializers
Handles user registration, login, and profile serialization
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from .models import MagicLink, UserSession

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    User serializer for user data
    Used for user profile display and updates
    """
    has_instances = serializers.SerializerMethodField()
    instances = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'name', 'phone', 'avatar',
            'language', 'is_active', 'is_staff', 'is_superuser',
            'date_joined', 'last_login', 'has_instances', 'instances'
        ]
        read_only_fields = ['id', 'is_staff', 'is_superuser', 'date_joined', 'last_login', 'has_instances', 'instances']
    
    def get_has_instances(self, obj):
        """Check if user has any instances (completed onboarding)"""
        return obj.instance_memberships.filter(is_active=True).exists()
    
    def get_instances(self, obj):
        """Get user's instances with minimal data"""
        from apps.instances.models import InstanceMember
        memberships = InstanceMember.objects.filter(user=obj, is_active=True).select_related('instance')
        return [{
            'id': str(m.instance.id),
            'name': m.instance.name,
            'role': m.role
        } for m in memberships]


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration
    Validates email uniqueness and creates new users
    """
    password = serializers.CharField(write_only=True, required=True, min_length=6)

    class Meta:
        model = User
        fields = ['email', 'name', 'phone', 'language', 'password']

    def validate_email(self, value):
        """Ensure email is unique"""
        if User.objects.filter(email=value.lower()).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value.lower()

    def create(self, validated_data):
        """Create new user with hashed password"""
        validated_data['email'] = validated_data['email'].lower()
        password = validated_data.pop('password')
        user = User.objects.create_user(
            password=password,
            **validated_data
        )
        return user


class LoginSerializer(serializers.Serializer):
    """
    Serializer for password-based login
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        """Validate credentials"""
        email = data.get('email', '').lower()
        password = data.get('password', '')

        if not email or not password:
            raise serializers.ValidationError("Email and password are required.")

        # Authenticate user
        user = authenticate(username=email, password=password)

        if not user:
            raise serializers.ValidationError("Invalid email or password.")

        if not user.is_active:
            raise serializers.ValidationError("This account has been disabled.")

        data['user'] = user
        return data


class MagicLinkRequestSerializer(serializers.Serializer):
    """
    Serializer for requesting a magic link
    Used when user wants to log in
    """
    email = serializers.EmailField()

    def validate_email(self, value):
        """Ensure email exists in the system"""
        if not User.objects.filter(email=value.lower()).exists():
            raise serializers.ValidationError(
                "No account found with this email address. Please register first."
            )
        return value.lower()


class MagicLinkVerifySerializer(serializers.Serializer):
    """
    Serializer for verifying a magic link token
    Returns JWT tokens on successful verification
    """
    token = serializers.CharField(max_length=100)

    def validate_token(self, value):
        """Verify the magic link token is valid"""
        try:
            magic_link = MagicLink.objects.get(token=value)
        except MagicLink.DoesNotExist:
            raise serializers.ValidationError("Invalid or expired token.")

        if not magic_link.is_valid():
            raise serializers.ValidationError("This token has expired or has already been used.")

        return value


class UserSessionSerializer(serializers.ModelSerializer):
    """
    Serializer for user sessions
    Used to track active sessions
    """
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserSession
        fields = [
            'id', 'user', 'token', 'refresh_token',
            'ip_address', 'user_agent', 'device_type', 'location',
            'is_active', 'created_at', 'last_activity', 'expires_at'
        ]
        read_only_fields = ['id', 'created_at', 'last_activity']


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user profile
    Allows partial updates
    """
    class Meta:
        model = User
        fields = ['name', 'phone', 'avatar', 'language']

    def update(self, instance, validated_data):
        """Update user profile"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
