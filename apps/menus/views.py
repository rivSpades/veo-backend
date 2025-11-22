"""
Menus app views
Handles digital menus, sections, items, QR codes, and analytics
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from django.utils import timezone

from apps.instances.models import Instance, InstanceMember
from .models import Menu, MenuSection, MenuItem, MenuView, QRCode, MenuTag, MenuAllergen
from .serializers import (
    MenuSerializer,
    MenuListSerializer,
    MenuCreateSerializer,
    MenuUpdateSerializer,
    MenuSectionSerializer,
    MenuSectionCreateSerializer,
    MenuItemSerializer,
    MenuItemCreateSerializer,
    QRCodeSerializer,
    MenuViewSerializer,
    MenuTagSerializer,
    MenuAllergenSerializer
)


class MenuViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing menus
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Get menus for instances where the user is a member
        """
        user_instances = Instance.objects.filter(
            members__user=self.request.user,
            members__is_active=True
        )
        return Menu.objects.filter(instance__in=user_instances)

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return MenuListSerializer
        elif self.action == 'create':
            return MenuCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return MenuUpdateSerializer
        return MenuSerializer

    def create(self, request, *args, **kwargs):
        """
        Create a new menu
        POST /api/menus/
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Verify user has permission to create menu for this instance
        instance_id = serializer.validated_data['instance'].id
        membership = InstanceMember.objects.filter(
            instance_id=instance_id,
            user=request.user,
            role__in=['owner', 'admin', 'manager']
        ).first()

        if not membership:
            return Response({
                'error': 'You do not have permission to create menus for this instance'
            }, status=status.HTTP_403_FORBIDDEN)

        menu = serializer.save()

        return Response({
            'message': 'Menu created successfully',
            'menu': MenuSerializer(menu).data
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], url_path='demo', permission_classes=[AllowAny])
    def demo(self, request):
        """
        Get demo menu for landing page (public endpoint, no auth required)
        GET /api/menus/demo/
        Returns the menu marked as demo from the database
        """
        # Get the demo menu from database
        demo_menu = Menu.objects.filter(is_demo=True, is_active=True).first()
        
        if not demo_menu:
            return Response({
                'error': 'No demo menu configured. Please mark a menu as demo in the admin panel.'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get all sections for this menu, ordered by order field
        sections = MenuSection.objects.filter(
            menu=demo_menu,
            is_active=True
        ).order_by('order', 'created_at')
        
        # Transform sections to match frontend format
        # Each MenuSection becomes a section with one subsection containing all items
        transformed_sections = []
        for section in sections:
            # Get all items for this section
            items = MenuItem.objects.filter(
                section=section,
                is_active=True
            ).order_by('order', 'created_at')
            
            # Transform items to match frontend format
            transformed_items = []
            for item in items:
                # Build tags list from item properties
                tags = []
                if item.is_vegetarian:
                    tags.append('vegetarian')
                if item.is_vegan:
                    tags.append('vegan')
                if item.is_gluten_free:
                    tags.append('gluten-free')
                if item.is_spicy:
                    tags.append('spicy')
                # Add any additional tags from JSON field
                if item.tags:
                    tags.extend(item.tags)
                
                # Get image URL if available
                image_url = None
                if item.image:
                    image_url = request.build_absolute_uri(item.image.url)
                
                transformed_item = {
                    'id': str(item.id),
                    'name': item.name.get('en', '') if isinstance(item.name, dict) else str(item.name),
                    'description': item.description.get('en', '') if isinstance(item.description, dict) else (str(item.description) if item.description else ''),
                    'fullDescription': item.description.get('en', '') if isinstance(item.description, dict) else (str(item.description) if item.description else ''),
                    'price': float(item.price),
                    'image': image_url,
                    'popular': item.is_featured,
                    'allergens': item.allergens if item.allergens else [],
                    'tags': tags,
                    'sortOrder': item.order,
                }
                transformed_items.append(transformed_item)
            
            # Each section becomes a section with one subsection
            # Use section name in default language
            section_name = section.name.get('en', 'Untitled Section') if isinstance(section.name, dict) else str(section.name)
            
            transformed_section = {
                'id': str(section.id),
                'name': section_name,
                'subSections': [
                    {
                        'id': str(section.id),  # Use section ID as subsection ID
                        'name': section_name,
                        'items': transformed_items,
                    }
                ],
            }
            transformed_sections.append(transformed_section)
        
        # Build translations object for all languages
        # Menu.name and Menu.description are CharField/TextField (not JSON), so use as-is for all languages
        translations = {}
        for lang in demo_menu.available_languages:
            translations[lang] = {
                'menu.name': demo_menu.name,
                'menu.description': demo_menu.description or '',
            }
            # Add section and item translations (these are JSON fields)
            for section in sections:
                section_id = str(section.id)
                section_name = section.name.get(lang, section.name.get('en', '')) if isinstance(section.name, dict) else str(section.name)
                translations[lang][f'section.{section_id}.name'] = section_name
                translations[lang][f'subsection.{section_id}.name'] = section_name
                
                for item in MenuItem.objects.filter(section=section, is_active=True):
                    item_id = str(item.id)
                    item_name = item.name.get(lang, item.name.get('en', '')) if isinstance(item.name, dict) else str(item.name)
                    item_desc = item.description.get(lang, item.description.get('en', '')) if isinstance(item.description, dict) else (str(item.description) if item.description else '')
                    translations[lang][f'item.{item_id}.name'] = item_name
                    translations[lang][f'item.{item_id}.description'] = item_desc
        
        # Build response data
        demo_data = {
            'id': str(demo_menu.id),
            'name': demo_menu.name,
            'description': demo_menu.description or '',
            'languages': demo_menu.available_languages,
            'default_language': demo_menu.default_language,
            'translations': translations,
            'sections': transformed_sections,
            'design': {
                'backgroundColor': '#FFFFFF',
                'fontColor': '#1F2937',
                'fontFamily': 'Inter',
                'fontSize': 14,
                'sectionBackgroundColor': '#F9FAFB',
                'sectionTextColor': '#111827',
                'sectionBorderColor': '#E5E7EB',
                'subsectionBackgroundColor': '#F3F4F6',
                'subsectionTextColor': '#6B7280',
                'tabActiveBackgroundColor': '#111827',
                'tabActiveTextColor': '#FFFFFF',
                'tabInactiveBackgroundColor': '#F9FAFB',
                'tabInactiveTextColor': '#111827',
            },
        }
        
        return Response(demo_data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], url_path='public', permission_classes=[AllowAny])
    def public_view(self, request, pk=None):
        """
        Public endpoint to view a menu (for customers)
        GET /api/menus/{id}/public/
        Query params: ?language=en
        """
        menu = self.get_object()

        if not menu.is_active:
            return Response({
                'error': 'This menu is not currently available'
            }, status=status.HTTP_404_NOT_FOUND)

        # Track menu view
        language = request.query_params.get('language', menu.default_language)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Better device detection
        if any(mobile in user_agent for mobile in ['Mobile', 'Android', 'iPhone', 'iPad']):
            device_type = 'mobile'
        elif 'Tablet' in user_agent or 'iPad' in user_agent:
            device_type = 'tablet'
        else:
            device_type = 'desktop'
        
        # Get IP address
        ip_address = None
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0].strip()
        else:
            ip_address = request.META.get('REMOTE_ADDR')

        MenuView.objects.create(
            menu=menu,
            language=language,
            device_type=device_type,
            ip_address=ip_address,
            user_agent=user_agent,
            referrer=request.META.get('HTTP_REFERER', '')
        )

        # Increment view count
        menu.increment_views()

        return Response(MenuSerializer(menu).data)

    @action(detail=True, methods=['get'], url_path='analytics')
    def analytics(self, request, pk=None):
        """
        Get analytics for a menu
        GET /api/menus/{id}/analytics/
        Query params: ?days=7
        """
        menu = self.get_object()

        # Check permission
        membership = InstanceMember.objects.filter(
            instance=menu.instance,
            user=request.user,
            role__in=['owner', 'admin', 'manager']
        ).first()

        if not membership:
            return Response({
                'error': 'You do not have permission to view analytics'
            }, status=status.HTTP_403_FORBIDDEN)

        # Get days parameter (default 7 days, max 365)
        try:
            days = int(request.query_params.get('days', 7))
            days = min(max(days, 1), 365)  # Clamp between 1 and 365
        except (ValueError, TypeError):
            days = 7
        
        since = timezone.now() - timezone.timedelta(days=days)

        views = MenuView.objects.filter(
            menu=menu,
            viewed_at__gte=since
        ).order_by('viewed_at')

        # Aggregate analytics
        total_views = views.count()
        language_breakdown = {}
        device_breakdown = {}

        for view in views:
            # Language breakdown
            lang = view.language or 'unknown'
            language_breakdown[lang] = language_breakdown.get(lang, 0) + 1

            # Device breakdown
            device = view.device_type or 'unknown'
            device_breakdown[device] = device_breakdown.get(device, 0) + 1

        return Response({
            'menu_id': str(menu.id),
            'menu_name': menu.name,
            'period_days': days,
            'total_views': total_views,
            'language_breakdown': language_breakdown,
            'device_breakdown': device_breakdown,
            'views_by_day': self._get_views_by_day(views, days),
            'has_data': total_views > 0
        })

    def _get_views_by_day(self, views, days):
        """Helper to get view counts by day"""
        from collections import defaultdict
        import datetime

        views_by_day = defaultdict(int)
        today = timezone.now().date()

        # Count views by day
        for view in views:
            if view.viewed_at:
                date = view.viewed_at.date()
                views_by_day[str(date)] += 1

        # Fill in missing days with 0 (going backwards from today)
        result = {}
        for i in range(days):
            date = today - datetime.timedelta(days=i)
            date_str = str(date)
            result[date_str] = views_by_day.get(date_str, 0)

        # Return sorted by date (oldest first)
        return dict(sorted(result.items()))

    @action(detail=True, methods=['post'], url_path='duplicate')
    def duplicate(self, request, pk=None):
        """
        Duplicate a menu
        POST /api/menus/{id}/duplicate/
        """
        menu = self.get_object()

        # Check permission
        membership = InstanceMember.objects.filter(
            instance=menu.instance,
            user=request.user,
            role__in=['owner', 'admin', 'manager']
        ).first()

        if not membership:
            return Response({
                'error': 'You do not have permission to duplicate this menu'
            }, status=status.HTTP_403_FORBIDDEN)

        # Create a copy of the menu
        new_menu = Menu.objects.create(
            instance=menu.instance,
            name=f"{menu.name} (Copy)",
            description=menu.description,
            default_language=menu.default_language,
            available_languages=menu.available_languages,
            is_active=False  # Set to inactive by default
        )

        # Copy all sections
        for section in menu.sections.all():
            new_section = MenuSection.objects.create(
                menu=new_menu,
                name=section.name,
                description=section.description,
                order=section.order,
                is_active=section.is_active
            )

            # Copy all items in this section
            for item in section.items.all():
                MenuItem.objects.create(
                    section=new_section,
                    name=item.name,
                    description=item.description,
                    price=item.price,
                    currency=item.currency,
                    image=item.image,
                    is_available=item.is_available,
                    is_featured=item.is_featured,
                    is_active=item.is_active,
                    is_vegetarian=item.is_vegetarian,
                    is_vegan=item.is_vegan,
                    is_gluten_free=item.is_gluten_free,
                    is_spicy=item.is_spicy,
                    spicy_level=item.spicy_level,
                    allergens=item.allergens,
                    ingredients=item.ingredients,
                    calories=item.calories,
                    order=item.order
                )

        return Response({
            'message': 'Menu duplicated successfully',
            'menu': MenuSerializer(new_menu).data
        }, status=status.HTTP_201_CREATED)


class MenuSectionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing menu sections
    """
    queryset = MenuSection.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return MenuSectionCreateSerializer
        return MenuSectionSerializer

    def get_queryset(self):
        """Filter sections by user's instances"""
        user_instances = Instance.objects.filter(
            members__user=self.request.user,
            members__is_active=True
        )
        return MenuSection.objects.filter(menu__instance__in=user_instances)

    def create(self, request, *args, **kwargs):
        """Create a new menu section"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Verify permission
        menu_id = serializer.validated_data['menu'].id
        menu = Menu.objects.get(id=menu_id)

        membership = InstanceMember.objects.filter(
            instance=menu.instance,
            user=request.user,
            role__in=['owner', 'admin', 'manager']
        ).first()

        if not membership:
            return Response({
                'error': 'You do not have permission to create sections for this menu'
            }, status=status.HTTP_403_FORBIDDEN)

        section = serializer.save()

        return Response({
            'message': 'Section created successfully',
            'section': MenuSectionSerializer(section).data
        }, status=status.HTTP_201_CREATED)


class MenuItemViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing menu items
    """
    queryset = MenuItem.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return MenuItemCreateSerializer
        return MenuItemSerializer

    def get_queryset(self):
        """Filter items by user's instances"""
        user_instances = Instance.objects.filter(
            members__user=self.request.user,
            members__is_active=True
        )
        return MenuItem.objects.filter(section__menu__instance__in=user_instances)

    def create(self, request, *args, **kwargs):
        """Create a new menu item"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Verify permission
        section_id = serializer.validated_data['section'].id
        section = MenuSection.objects.get(id=section_id)

        membership = InstanceMember.objects.filter(
            instance=section.menu.instance,
            user=request.user,
            role__in=['owner', 'admin', 'manager', 'staff']
        ).first()

        if not membership:
            return Response({
                'error': 'You do not have permission to create items for this menu'
            }, status=status.HTTP_403_FORBIDDEN)

        item = serializer.save()

        return Response({
            'message': 'Menu item created successfully',
            'item': MenuItemSerializer(item).data
        }, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['patch'], url_path='toggle-availability')
    def toggle_availability(self, request, pk=None):
        """
        Toggle item availability
        PATCH /api/menu-items/{id}/toggle-availability/
        """
        item = self.get_object()

        # Verify permission
        membership = InstanceMember.objects.filter(
            instance=item.section.menu.instance,
            user=request.user,
            role__in=['owner', 'admin', 'manager', 'staff']
        ).first()

        if not membership:
            return Response({
                'error': 'You do not have permission to update this item'
            }, status=status.HTTP_403_FORBIDDEN)

        item.is_available = not item.is_available
        item.save()

        return Response({
            'message': f'Item is now {"available" if item.is_available else "unavailable"}',
            'item': MenuItemSerializer(item).data
        })


class QRCodeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for managing QR codes
    """
    queryset = QRCode.objects.all()
    serializer_class = QRCodeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter QR codes by user's instances"""
        user_instances = Instance.objects.filter(
            members__user=self.request.user,
            members__is_active=True
        )
        return QRCode.objects.filter(menu__instance__in=user_instances)

    @action(detail=True, methods=['post'], url_path='scan', permission_classes=[AllowAny])
    def scan(self, request, pk=None):
        """
        Track QR code scan
        POST /api/qrcodes/{id}/scan/
        """
        qr_code = self.get_object()

        if not qr_code.is_active:
            return Response({
                'error': 'This QR code is no longer active'
            }, status=status.HTTP_404_NOT_FOUND)

        # Increment scan count
        qr_code.scan_count += 1
        qr_code.save()

        # Redirect to menu
        return Response({
            'menu_url': qr_code.url,
            'menu_id': qr_code.menu.id
        })


class MenuTagViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing menu tags (global configuration)
    """
    queryset = MenuTag.objects.filter(is_active=True)
    serializer_class = MenuTagSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return all active tags"""
        return MenuTag.objects.filter(is_active=True).order_by('order', 'id')


class MenuAllergenViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing menu allergens (global configuration)
    """
    queryset = MenuAllergen.objects.filter(is_active=True)
    serializer_class = MenuAllergenSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return all active allergens"""
        return MenuAllergen.objects.filter(is_active=True).order_by('order', 'id')
