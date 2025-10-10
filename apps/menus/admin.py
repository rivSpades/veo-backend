from django.contrib import admin
from .models import Menu, MenuSection, MenuItem, MenuView, QRCode, MenuTag, MenuAllergen


class MenuSectionInline(admin.TabularInline):
    model = MenuSection
    extra = 0
    fields = ['name', 'order', 'is_active']
    ordering = ['order']


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ['name', 'instance', 'is_published', 'is_active', 'view_count', 'created_at']
    list_filter = ['is_published', 'is_active', 'default_language', 'created_at']
    search_fields = ['name', 'instance__name']
    readonly_fields = ['id', 'view_count', 'last_viewed_at', 'created_at', 'updated_at']
    inlines = [MenuSectionInline]
    ordering = ['-created_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'instance', 'name', 'description')
        }),
        ('Languages', {
            'fields': ('default_language', 'available_languages')
        }),
        ('Status', {
            'fields': ('is_active', 'is_published')
        }),
        ('Analytics', {
            'fields': ('view_count', 'last_viewed_at'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class MenuItemInline(admin.TabularInline):
    model = MenuItem
    extra = 0
    fields = ['name', 'price', 'order', 'is_available', 'is_featured']
    ordering = ['order']


@admin.register(MenuSection)
class MenuSectionAdmin(admin.ModelAdmin):
    list_display = ['get_name', 'menu', 'order', 'is_active']
    list_filter = ['is_active', 'menu']
    search_fields = ['name', 'menu__name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    inlines = [MenuItemInline]
    ordering = ['menu', 'order']

    def get_name(self, obj):
        return obj.name.get('en', 'Untitled')
    get_name.short_description = 'Name'


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ['get_name', 'section', 'price', 'currency', 'is_available', 'is_featured', 'view_count']
    list_filter = ['is_available', 'is_featured', 'is_vegetarian', 'is_vegan', 'is_gluten_free', 'spicy_level']
    search_fields = ['name', 'section__name']
    readonly_fields = ['id', 'view_count', 'created_at', 'updated_at']
    ordering = ['section', 'order']

    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'section', 'name', 'description', 'image')
        }),
        ('Pricing', {
            'fields': ('price', 'currency')
        }),
        ('Properties', {
            'fields': ('is_vegetarian', 'is_vegan', 'is_gluten_free', 'is_spicy', 'spicy_level'),
            'classes': ('collapse',)
        }),
        ('Additional Information', {
            'fields': ('allergens', 'tags', 'ingredients', 'calories'),
            'classes': ('collapse',)
        }),
        ('Display', {
            'fields': ('order', 'is_active', 'is_available', 'is_featured')
        }),
        ('Analytics', {
            'fields': ('view_count',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_name(self, obj):
        return obj.name.get('en', 'Untitled')
    get_name.short_description = 'Name'


@admin.register(MenuTag)
class MenuTagAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_name', 'category', 'color', 'is_active', 'order']
    list_filter = ['is_active', 'category']
    search_fields = ['id', 'name']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['order', 'id']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'name', 'icon', 'color', 'category')
        }),
        ('Display', {
            'fields': ('order', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_name(self, obj):
        return obj.name.get('en', obj.id)
    get_name.short_description = 'Name'


@admin.register(MenuAllergen)
class MenuAllergenAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_name', 'color', 'is_active', 'order']
    list_filter = ['is_active']
    search_fields = ['id', 'name']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['order', 'id']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'name', 'color')
        }),
        ('Display', {
            'fields': ('order', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_name(self, obj):
        return obj.name.get('en', obj.id)
    get_name.short_description = 'Name'


@admin.register(MenuView)
class MenuViewAdmin(admin.ModelAdmin):
    list_display = ['menu', 'language', 'device_type', 'country', 'city', 'viewed_at']
    list_filter = ['language', 'device_type', 'country', 'viewed_at']
    search_fields = ['menu__name', 'ip_address']
    readonly_fields = ['viewed_at']
    ordering = ['-viewed_at']


@admin.register(QRCode)
class QRCodeAdmin(admin.ModelAdmin):
    list_display = ['menu', 'name', 'scan_count', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['menu__name', 'name']
    readonly_fields = ['id', 'scan_count', 'last_scanned_at', 'created_at', 'updated_at']
    ordering = ['-created_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'menu', 'name', 'code_image', 'url')
        }),
        ('Customization', {
            'fields': ('foreground_color', 'background_color', 'logo_enabled'),
            'classes': ('collapse',)
        }),
        ('Analytics', {
            'fields': ('scan_count', 'last_scanned_at'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
