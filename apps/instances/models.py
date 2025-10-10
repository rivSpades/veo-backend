from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from apps.authentication.models import User
import uuid


class Instance(models.Model):
    """
    Represents a restaurant/bar/cafe instance in the multi-tenant system.
    Each instance has its own menus, settings, and analytics.
    """

    # Instance identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, db_index=True)

    # Location
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    address = models.TextField(blank=True)

    # Contact info
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    whatsapp = models.CharField(max_length=20, blank=True)

    # Business details
    description = models.TextField(blank=True)
    cuisine_type = models.CharField(max_length=100, blank=True)
    logo = models.ImageField(upload_to='logos/', null=True, blank=True)

    # WiFi Information
    wifi_name = models.CharField(max_length=100, blank=True)
    wifi_password = models.CharField(max_length=100, blank=True)
    show_wifi_on_menu = models.BooleanField(default=False)

    # Business Hours
    show_hours_on_menu = models.BooleanField(default=False)

    # Google Integration
    google_business_url = models.URLField(blank=True)
    google_rating = models.DecimalField(max_digits=2, decimal_places=1, null=True, blank=True)
    google_review_count = models.IntegerField(default=0)
    show_google_rating = models.BooleanField(default=False)

    # Subscription
    subscription_status = models.CharField(
        max_length=20,
        choices=[
            ('trial', 'Trial'),
            ('active', 'Active'),
            ('expired', 'Expired'),
            ('cancelled', 'Cancelled'),
        ],
        default='trial'
    )
    trial_start_date = models.DateTimeField(null=True, blank=True)
    trial_end_date = models.DateTimeField(null=True, blank=True)
    subscription_start_date = models.DateTimeField(null=True, blank=True)

    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'instances'
        verbose_name = 'Instance'
        verbose_name_plural = 'Instances'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1

            # Handle slug collisions by appending a number
            while Instance.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug
        super().save(*args, **kwargs)

    def is_trial_active(self):
        """Check if trial period is still active."""
        if self.subscription_status != 'trial':
            return False
        if not self.trial_end_date:
            return False
        return timezone.now() < self.trial_end_date

    def days_remaining_in_trial(self):
        """Calculate days remaining in trial."""
        if not self.is_trial_active():
            return 0
        delta = self.trial_end_date - timezone.now()
        return max(0, delta.days)


class InstanceMember(models.Model):
    """
    Represents membership of a user in an instance.
    Users can belong to multiple instances with different roles.
    """

    ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('staff', 'Staff'),
    ]

    instance = models.ForeignKey(Instance, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='instance_memberships')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='staff')
    is_active = models.BooleanField(default=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'instance_members'
        verbose_name = 'Instance Member'
        verbose_name_plural = 'Instance Members'
        unique_together = ('instance', 'user')
        ordering = ['-joined_at']

    def __str__(self):
        return f"{self.user.email} - {self.instance.name} ({self.role})"

    def is_owner(self):
        return self.role == 'owner'

    def is_admin(self):
        return self.role in ['owner', 'admin']

    def can_manage_menus(self):
        return self.role in ['owner', 'admin', 'manager']


class BusinessHours(models.Model):
    """Opening hours for each day of the week."""

    DAY_CHOICES = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]

    instance = models.ForeignKey(Instance, on_delete=models.CASCADE, related_name='business_hours')
    day_of_week = models.IntegerField(choices=DAY_CHOICES)
    opening_time = models.TimeField()
    closing_time = models.TimeField()
    is_closed = models.BooleanField(default=False)

    class Meta:
        db_table = 'business_hours'
        verbose_name = 'Business Hours'
        verbose_name_plural = 'Business Hours'
        unique_together = ('instance', 'day_of_week')
        ordering = ['day_of_week']

    def __str__(self):
        day_name = dict(self.DAY_CHOICES)[self.day_of_week]
        if self.is_closed:
            return f"{self.instance.name} - {day_name}: Closed"
        return f"{self.instance.name} - {day_name}: {self.opening_time} - {self.closing_time}"
