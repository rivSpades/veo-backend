from django.db import models
from django.utils import timezone
from apps.instances.models import Instance
import uuid


class Menu(models.Model):
    """Digital menu for a restaurant instance."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    instance = models.ForeignKey(Instance, on_delete=models.CASCADE, related_name='menus')

    # Basic info
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, default='Utensils')  # Menu icon name

    # Languages
    default_language = models.CharField(max_length=10, default='en')
    available_languages = models.JSONField(default=list)  # ['en', 'pt', 'es']

    # Status
    is_active = models.BooleanField(default=True)
    is_published = models.BooleanField(default=False)
    is_demo = models.BooleanField(default=False, help_text="Mark this menu as the demo menu for the landing page")

    # Analytics
    view_count = models.IntegerField(default=0)
    last_viewed_at = models.DateTimeField(null=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'menus'
        verbose_name = 'Menu'
        verbose_name_plural = 'Menus'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.instance.name} - {self.name}"

    def increment_views(self):
        """Increment view count and update last viewed timestamp."""
        self.view_count += 1
        self.last_viewed_at = timezone.now()
        self.save(update_fields=['view_count', 'last_viewed_at'])


class MenuSection(models.Model):
    """Section within a menu (e.g., Appetizers, Main Courses, Desserts)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, related_name='sections')

    # Basic info
    name = models.JSONField()  # {'en': 'Appetizers', 'pt': 'Entradas', 'es': 'Entrantes'}
    description = models.JSONField(default=dict, blank=True)  # Multilingual descriptions

    # Display
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    icon = models.CharField(max_length=50, blank=True)  # Icon name/emoji

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'menu_sections'
        verbose_name = 'Menu Section'
        verbose_name_plural = 'Menu Sections'
        ordering = ['menu', 'order']

    def __str__(self):
        name_en = self.name.get('en', 'Untitled Section')
        return f"{self.menu.name} - {name_en}"


class MenuItem(models.Model):
    """Individual item within a menu section."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    section = models.ForeignKey(MenuSection, on_delete=models.CASCADE, related_name='items')

    # Basic info (multilingual)
    name = models.JSONField()  # {'en': 'Pasta Carbonara', 'pt': 'Massa Carbonara'}
    description = models.JSONField(default=dict, blank=True)

    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='EUR')

    # Media
    image = models.ImageField(upload_to='menu_items/', null=True, blank=True)

    # Properties
    is_vegetarian = models.BooleanField(default=False)
    is_vegan = models.BooleanField(default=False)
    is_gluten_free = models.BooleanField(default=False)
    is_spicy = models.BooleanField(default=False)
    spicy_level = models.IntegerField(default=0, choices=[(0, 'Not Spicy'), (1, 'Mild'), (2, 'Medium'), (3, 'Hot')])

    # Additional info
    allergens = models.JSONField(default=list, blank=True)  # ['gluten', 'dairy', 'nuts']
    tags = models.JSONField(default=list, blank=True)  # ['popular', 'chef-special', 'new', etc.]
    ingredients = models.JSONField(default=dict, blank=True)  # Multilingual ingredients
    calories = models.IntegerField(null=True, blank=True)

    # Display
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    is_available = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)

    # Analytics
    view_count = models.IntegerField(default=0)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'menu_items'
        verbose_name = 'Menu Item'
        verbose_name_plural = 'Menu Items'
        ordering = ['section', 'order']

    def __str__(self):
        name_en = self.name.get('en', 'Untitled Item')
        return f"{name_en} - €{self.price}"


class MenuTag(models.Model):
    """Configurable tags for menu items (e.g., Popular, Chef's Special, New)."""
    
    id = models.CharField(max_length=50, primary_key=True)  # e.g., 'popular', 'chef-special'
    name = models.JSONField()  # Multilingual: {'en': 'Popular', 'pt': 'Popular', 'es': 'Popular'}
    icon = models.CharField(max_length=50, blank=True)  # Icon name
    color = models.CharField(max_length=50, default='bg-gray-100 text-gray-800')  # Tailwind classes
    category = models.CharField(max_length=50, blank=True)  # 'Dietary', 'Special', 'Taste', etc.
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'menu_tags'
        verbose_name = 'Menu Tag'
        verbose_name_plural = 'Menu Tags'
        ordering = ['order', 'id']
    
    def __str__(self):
        name_en = self.name.get('en', self.id)
        return f"{name_en} ({self.id})"


class MenuAllergen(models.Model):
    """Configurable allergens for menu items."""
    
    id = models.CharField(max_length=50, primary_key=True)  # e.g., 'gluten', 'dairy'
    name = models.JSONField()  # Multilingual: {'en': 'Gluten', 'pt': 'Glúten', 'es': 'Gluten'}
    color = models.CharField(max_length=50, default='bg-orange-100 text-orange-800')
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'menu_allergens'
        verbose_name = 'Menu Allergen'
        verbose_name_plural = 'Menu Allergens'
        ordering = ['order', 'id']
    
    def __str__(self):
        name_en = self.name.get('en', self.id)
        return f"{name_en} ({self.id})"


class MenuView(models.Model):
    """Track menu views for analytics."""

    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, related_name='views')

    # Visitor info
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    device_type = models.CharField(max_length=50, blank=True)  # mobile, tablet, desktop

    # Location (if available)
    country = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)

    # Language preference
    language = models.CharField(max_length=10, default='en')

    # Referrer
    referrer = models.URLField(blank=True)

    # Timestamp
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'menu_views'
        verbose_name = 'Menu View'
        verbose_name_plural = 'Menu Views'
        ordering = ['-viewed_at']

    def __str__(self):
        return f"{self.menu.name} viewed at {self.viewed_at}"


class QRCode(models.Model):
    """QR Code generated for menus."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, related_name='qr_codes')

    # QR Code details
    name = models.CharField(max_length=255, blank=True)  # e.g., "Table 5", "Counter"
    code_image = models.ImageField(upload_to='qr_codes/', null=True, blank=True)
    url = models.URLField()  # Public URL to the menu

    # Customization
    foreground_color = models.CharField(max_length=7, default='#000000')
    background_color = models.CharField(max_length=7, default='#FFFFFF')
    logo_enabled = models.BooleanField(default=False)

    # Analytics
    scan_count = models.IntegerField(default=0)
    last_scanned_at = models.DateTimeField(null=True, blank=True)

    # Status
    is_active = models.BooleanField(default=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'qr_codes'
        verbose_name = 'QR Code'
        verbose_name_plural = 'QR Codes'
        ordering = ['-created_at']

    def __str__(self):
        return f"QR Code for {self.menu.name}" + (f" - {self.name}" if self.name else "")

    def increment_scans(self):
        """Increment scan count."""
        self.scan_count += 1
        self.last_scanned_at = timezone.now()
        self.save(update_fields=['scan_count', 'last_scanned_at'])
