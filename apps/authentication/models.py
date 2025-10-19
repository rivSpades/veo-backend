from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
import secrets
import random
import string


class UserManager(BaseUserManager):
    """Custom user manager for email-based authentication."""

    def create_user(self, email, name=None, password=None, **extra_fields):
        """Create and save a regular user with the given email."""
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name=None, password=None, **extra_fields):
        """Create and save a superuser with the given email."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, name, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model with email as the primary identifier."""

    email = models.EmailField(unique=True, db_index=True)
    name = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(null=True, blank=True)

    # Profile fields
    phone = models.CharField(max_length=20, blank=True)
    is_phone_verified = models.BooleanField(default=False)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    language = models.CharField(max_length=10, default='en')

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.email

    def get_full_name(self):
        return self.name or self.email

    def get_short_name(self):
        return self.name.split()[0] if self.name else self.email.split('@')[0]


class MagicLink(models.Model):
    """Magic link tokens for passwordless authentication."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='magic_links')
    token = models.CharField(max_length=100, unique=True, db_index=True)
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    used_at = models.DateTimeField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    class Meta:
        db_table = 'magic_links'
        verbose_name = 'Magic Link'
        verbose_name_plural = 'Magic Links'
        ordering = ['-created_at']

    def __str__(self):
        return f"Magic Link for {self.email} - {'Used' if self.is_used else 'Active'}"

    @staticmethod
    def generate_token():
        """Generate a secure random token."""
        return secrets.token_urlsafe(32)

    def is_valid(self):
        """Check if the magic link is still valid."""
        if self.is_used:
            return False
        if timezone.now() > self.expires_at:
            return False
        return True

    def mark_as_used(self):
        """Mark the magic link as used."""
        self.is_used = True
        self.used_at = timezone.now()
        self.save()


class UserSession(models.Model):
    """Track user sessions for security and analytics."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    token = models.CharField(max_length=255, unique=True)
    refresh_token = models.CharField(max_length=255, unique=True, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    device_type = models.CharField(max_length=50, blank=True)
    location = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'user_sessions'
        verbose_name = 'User Session'
        verbose_name_plural = 'User Sessions'
        ordering = ['-last_activity']

    def __str__(self):
        return f"{self.user.email} - {self.device_type} - {self.created_at}"

    def is_valid(self):
        """Check if session is still valid."""
        if not self.is_active:
            return False
        if timezone.now() > self.expires_at:
            return False
        return True


class PhoneVerification(models.Model):
    """Phone number verification for users."""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='phone_verifications')
    phone_number = models.CharField(max_length=20, db_index=True)
    verification_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)
    attempts = models.PositiveIntegerField(default=0)
    max_attempts = models.PositiveIntegerField(default=3)
    
    class Meta:
        db_table = 'phone_verifications'
        verbose_name = 'Phone Verification'
        verbose_name_plural = 'Phone Verifications'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Phone verification for {self.phone_number} - {'Verified' if self.is_verified else 'Pending'}"
    
    @staticmethod
    def generate_verification_code():
        """Generate a 6-digit verification code."""
        return ''.join(random.choices(string.digits, k=6))
    
    def is_valid(self):
        """Check if the verification code is still valid."""
        if self.is_verified:
            return False
        if timezone.now() > self.expires_at:
            return False
        if self.attempts >= self.max_attempts:
            return False
        return True
    
    def verify_code(self, code):
        """Verify the provided code."""
        if not self.is_valid():
            return False
        
        if self.verification_code == code:
            self.is_verified = True
            self.verified_at = timezone.now()
            self.save()
            return True
        else:
            self.attempts += 1
            self.save()
            return False
    
    def mark_as_verified(self):
        """Mark the phone number as verified."""
        self.is_verified = True
        self.verified_at = timezone.now()
        self.save()
