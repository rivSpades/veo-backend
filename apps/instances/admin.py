from django.contrib import admin
from .models import Instance, InstanceMember, BusinessHours


class InstanceMemberInline(admin.TabularInline):
    model = InstanceMember
    extra = 0
    fields = ['user', 'role', 'is_active', 'joined_at']
    readonly_fields = ['joined_at']


class BusinessHoursInline(admin.TabularInline):
    model = BusinessHours
    extra = 0
    fields = ['day_of_week', 'opening_time', 'closing_time', 'is_closed']


@admin.register(Instance)
class InstanceAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'country', 'subscription_status', 'is_active', 'created_at']
    list_filter = ['subscription_status', 'is_active', 'country', 'created_at']
    search_fields = ['name', 'city', 'email', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['id', 'created_at', 'updated_at']
    inlines = [InstanceMemberInline, BusinessHoursInline]
    ordering = ['-created_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'name', 'slug', 'description', 'logo', 'cuisine_type')
        }),
        ('Location', {
            'fields': ('country', 'city', 'address')
        }),
        ('Contact', {
            'fields': ('phone', 'email', 'website', 'whatsapp')
        }),
        ('WiFi Settings', {
            'fields': ('wifi_name', 'wifi_password', 'show_wifi_on_menu'),
            'classes': ('collapse',)
        }),
        ('Business Hours', {
            'fields': ('show_hours_on_menu',),
        }),
        ('Google Integration', {
            'fields': ('google_business_url', 'google_rating', 'google_review_count', 'show_google_rating'),
            'classes': ('collapse',)
        }),
        ('Subscription', {
            'fields': ('subscription_status', 'trial_start_date', 'trial_end_date', 'subscription_start_date')
        }),
        ('Status', {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )


@admin.register(InstanceMember)
class InstanceMemberAdmin(admin.ModelAdmin):
    list_display = ['user', 'instance', 'role', 'is_active', 'joined_at']
    list_filter = ['role', 'is_active', 'joined_at']
    search_fields = ['user__email', 'instance__name']
    ordering = ['-joined_at']


@admin.register(BusinessHours)
class BusinessHoursAdmin(admin.ModelAdmin):
    list_display = ['instance', 'day_of_week', 'opening_time', 'closing_time', 'is_closed']
    list_filter = ['day_of_week', 'is_closed']
    search_fields = ['instance__name']
    ordering = ['instance', 'day_of_week']
