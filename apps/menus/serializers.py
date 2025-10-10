"""
Menus app serializers
Handles digital menus, sections, items, QR codes, and analytics
"""
from rest_framework import serializers
from .models import Menu, MenuSection, MenuItem, MenuView, QRCode, MenuTag, MenuAllergen


class MenuItemSerializer(serializers.ModelSerializer):
    """
    Serializer for menu items (dishes)
    """
    class Meta:
        model = MenuItem
        fields = [
            'id', 'section', 'name', 'description', 'price', 'currency',
            'image', 'is_available', 'is_featured', 'is_active',
            'is_vegetarian', 'is_vegan', 'is_gluten_free',
            'is_spicy', 'spicy_level', 'allergens', 'tags', 'ingredients',
            'calories', 'order', 'view_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'view_count', 'created_at', 'updated_at']

    def validate_name(self, value):
        """Ensure name is a valid JSON object with language keys"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Name must be a JSON object with language keys.")
        if not value:
            raise serializers.ValidationError("Name cannot be empty.")
        return value

    def validate_price(self, value):
        """Ensure price is positive"""
        if value < 0:
            raise serializers.ValidationError("Price cannot be negative.")
        return value


class MenuSectionSerializer(serializers.ModelSerializer):
    """
    Serializer for menu sections
    Includes all items in the section
    """
    items = MenuItemSerializer(many=True, read_only=True)
    item_count = serializers.SerializerMethodField()

    class Meta:
        model = MenuSection
        fields = [
            'id', 'menu', 'name', 'description',
            'order', 'is_active', 'created_at',
            'items', 'item_count'
        ]
        read_only_fields = ['id', 'created_at']

    def get_item_count(self, obj):
        """Get number of items in this section"""
        return obj.items.count()

    def validate_name(self, value):
        """Ensure name is a valid JSON object"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Name must be a JSON object with language keys.")
        if not value:
            raise serializers.ValidationError("Name cannot be empty.")
        return value


class MenuSerializer(serializers.ModelSerializer):
    """
    Full menu serializer with all sections and items
    """
    sections = MenuSectionSerializer(many=True, read_only=True)
    section_count = serializers.SerializerMethodField()
    total_items = serializers.SerializerMethodField()

    class Meta:
        model = Menu
        fields = [
            'id', 'instance', 'name', 'description', 'icon',
            'default_language', 'available_languages',
            'is_active', 'view_count', 'created_at',
            'updated_at', 'sections', 'section_count', 'total_items'
        ]
        read_only_fields = ['id', 'view_count', 'created_at', 'updated_at']

    def get_section_count(self, obj):
        """Get number of sections"""
        return obj.sections.count()

    def get_total_items(self, obj):
        """Get total number of items across all sections"""
        return MenuItem.objects.filter(section__menu=obj).count()


class MenuListSerializer(serializers.ModelSerializer):
    """
    Lightweight menu serializer for list views
    """
    section_count = serializers.SerializerMethodField()

    class Meta:
        model = Menu
        fields = [
            'id', 'instance', 'name', 'icon', 'default_language',
            'is_active', 'view_count', 'created_at', 'section_count'
        ]
        read_only_fields = ['id', 'view_count', 'created_at']

    def get_section_count(self, obj):
        """Get number of sections"""
        return obj.sections.count()


class MenuCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new menus
    """
    class Meta:
        model = Menu
        fields = [
            'instance', 'name', 'description', 'icon',
            'default_language', 'available_languages'
        ]

    def validate_available_languages(self, value):
        """Ensure at least one language is specified"""
        if not value or not isinstance(value, list):
            raise serializers.ValidationError("At least one language must be specified.")
        return value

    def validate(self, data):
        """Ensure default language is in available languages"""
        default_lang = data.get('default_language', 'en')
        available_langs = data.get('available_languages', [])

        if default_lang not in available_langs:
            raise serializers.ValidationError(
                f"Default language '{default_lang}' must be in available languages."
            )

        return data


class QRCodeSerializer(serializers.ModelSerializer):
    """
    Serializer for QR codes
    """
    menu_name = serializers.CharField(source='menu.name', read_only=True)

    class Meta:
        model = QRCode
        fields = [
            'id', 'menu', 'menu_name', 'code_image',
            'url', 'scan_count', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'code_image', 'scan_count', 'created_at', 'updated_at']


class MenuViewSerializer(serializers.ModelSerializer):
    """
    Serializer for menu view analytics
    """
    menu_name = serializers.CharField(source='menu.name', read_only=True)

    class Meta:
        model = MenuView
        fields = [
            'id', 'menu', 'menu_name', 'language',
            'device_type', 'viewed_at'
        ]
        read_only_fields = ['id', 'viewed_at']


class MenuItemCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating menu items
    """
    class Meta:
        model = MenuItem
        fields = [
            'section', 'name', 'description', 'price', 'currency',
            'image', 'is_available', 'is_featured', 'is_active',
            'is_vegetarian', 'is_vegan', 'is_gluten_free',
            'is_spicy', 'spicy_level', 'allergens', 'ingredients',
            'calories', 'order'
        ]

    def validate_allergens(self, value):
        """Ensure allergens is a list"""
        if not isinstance(value, list):
            raise serializers.ValidationError("Allergens must be a list.")
        return value


class MenuSectionCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating menu sections
    """
    class Meta:
        model = MenuSection
        fields = ['menu', 'name', 'description', 'order', 'is_active']

    def validate_name(self, value):
        """Validate that name is a non-empty dict"""
        if not value or not isinstance(value, dict):
            raise serializers.ValidationError("Name must be a non-empty dictionary with language keys")
        if not any(value.values()):
            raise serializers.ValidationError("Name must contain at least one non-empty value")
        return value


class MenuUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating menu details
    """
    class Meta:
        model = Menu
        fields = [
            'name', 'description', 'icon', 'default_language',
            'available_languages', 'is_active'
        ]

    def update(self, instance, validated_data):
        """Update menu details"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class MenuTagSerializer(serializers.ModelSerializer):
    """
    Serializer for menu tags
    """
    class Meta:
        model = MenuTag
        fields = ['id', 'name', 'icon', 'color', 'category', 'is_active', 'order', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class MenuAllergenSerializer(serializers.ModelSerializer):
    """
    Serializer for menu allergens
    """
    class Meta:
        model = MenuAllergen
        fields = ['id', 'name', 'color', 'is_active', 'order', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
