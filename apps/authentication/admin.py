from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, MagicLink, UserSession


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'name', 'is_active', 'is_staff', 'date_joined']
    list_filter = ['is_active', 'is_staff', 'is_superuser', 'date_joined']
    search_fields = ['email', 'name']
    ordering = ['-date_joined']

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('name', 'phone', 'avatar', 'language')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'password1', 'password2'),
        }),
    )

    readonly_fields = ['date_joined', 'last_login']


@admin.register(MagicLink)
class MagicLinkAdmin(admin.ModelAdmin):
    list_display = ['email', 'user', 'is_used', 'created_at', 'expires_at', 'is_valid_display']
    list_filter = ['is_used', 'created_at']
    search_fields = ['email', 'user__email', 'token']
    readonly_fields = ['token', 'created_at', 'used_at']
    ordering = ['-created_at']

    def is_valid_display(self, obj):
        return obj.is_valid()
    is_valid_display.boolean = True
    is_valid_display.short_description = 'Valid'


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'device_type', 'ip_address', 'is_active', 'created_at', 'last_activity']
    list_filter = ['is_active', 'device_type', 'created_at']
    search_fields = ['user__email', 'ip_address']
    readonly_fields = ['token', 'created_at', 'last_activity']
    ordering = ['-last_activity']
