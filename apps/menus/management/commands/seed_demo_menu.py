"""
Django management command to seed the database with demo menu data.

Usage:
    python manage.py seed_demo_menu
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.instances.models import Instance, BusinessHours
from apps.menus.models import Menu, MenuSection, MenuItem
from decimal import Decimal


class Command(BaseCommand):
    help = 'Seed the database with demo menu and instance data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting to seed demo menu data...'))

        # Unmark any existing demo instances/menus
        Instance.objects.filter(is_demo=True).update(is_demo=False)
        Menu.objects.filter(is_demo=True).update(is_demo=False)

        # Create or get demo instance
        demo_instance, created = Instance.objects.get_or_create(
            slug='veomenu-demo-restaurant',
            defaults={
                'name': 'Alpine Meadow',
                'description': 'Modern European cuisine with a cozy atmosphere',
                'country': 'Switzerland',
                'city': 'Alpine Valley',
                'address': '123 Mountain View, Alpine Valley, Switzerland',
                'phone': '+41 21 123 4567',
                'email': 'info@alpinemeadow.ch',
                'website': 'https://alpinemeadow.ch',
                'cuisine_type': 'European',
                'wifi_name': 'AlpineMeadow_Guest',
                'wifi_password': 'alpine2024',
                'show_wifi_on_menu': True,
                'show_hours_on_menu': True,
                'google_business_url': 'https://g.page/alpine-meadow',
                'google_rating': Decimal('4.8'),
                'google_review_count': 247,
                'show_google_rating': True,
                'is_active': True,
                'is_demo': True,
                'subscription_status': 'active',
            }
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f'Created demo instance: {demo_instance.name}'))
        else:
            # Update existing instance to be demo
            demo_instance.is_demo = True
            demo_instance.is_active = True
            demo_instance.save()
            self.stdout.write(self.style.SUCCESS(f'Updated existing instance to demo: {demo_instance.name}'))

        # Create business hours
        business_hours_data = [
            (0, '09:00', '22:00', False),  # Monday
            (1, '09:00', '22:00', False),  # Tuesday
            (2, '09:00', '22:00', False),  # Wednesday
            (3, '09:00', '22:00', False),  # Thursday
            (4, '09:00', '23:00', False),  # Friday
            (5, '10:00', '23:00', False),  # Saturday
            (6, '10:00', '21:00', False),  # Sunday
        ]

        for day, open_time, close_time, is_closed in business_hours_data:
            BusinessHours.objects.update_or_create(
                instance=demo_instance,
                day_of_week=day,
                defaults={
                    'opening_time': open_time,
                    'closing_time': close_time,
                    'is_closed': is_closed,
                }
            )

        self.stdout.write(self.style.SUCCESS('Created business hours for demo instance'))

        # Create or get demo menu
        demo_menu, created = Menu.objects.get_or_create(
            instance=demo_instance,
            name='Alpine Meadow Menu',
            defaults={
                'description': 'Modern European cuisine with a cozy atmosphere',
                'default_language': 'en',
                'available_languages': ['en', 'pt', 'es'],
                'is_active': True,
                'is_published': True,
                'is_demo': True,
            }
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f'Created demo menu: {demo_menu.name}'))
        else:
            # Update existing menu to be demo
            demo_menu.is_demo = True
            demo_menu.is_active = True
            demo_menu.save()
            self.stdout.write(self.style.SUCCESS(f'Updated existing menu to demo: {demo_menu.name}'))

        # Clear existing sections and items for demo menu
        MenuSection.objects.filter(menu=demo_menu).delete()

        # Create sections and items
        sections_data = [
            {
                'name': {
                    'en': 'Starters',
                    'pt': 'Entradas',
                    'es': 'Entrantes'
                },
                'description': {
                    'en': 'Delicious appetizers to start your meal',
                    'pt': 'Entradas deliciosas para começar a sua refeição',
                    'es': 'Deliciosos entrantes para comenzar su comida'
                },
                'order': 1,
                'items': [
                    {
                        'name': {
                            'en': 'Truffle Arancini',
                            'pt': 'Arancini de Trufa',
                            'es': 'Arancini de Trufa'
                        },
                        'description': {
                            'en': 'Crispy risotto balls with truffle oil and parmesan cheese',
                            'pt': 'Bolas de risotto crocantes com azeite de trufa e queijo parmesão',
                            'es': 'Bolas de risotto crujientes con aceite de trufa y queso parmesano'
                        },
                        'price': Decimal('14.00'),
                        'currency': 'EUR',
                        'is_vegetarian': True,
                        'is_gluten_free': False,
                        'allergens': ['gluten', 'dairy'],
                        'tags': ['vegetarian', 'popular'],
                        'is_featured': True,
                        'is_available': True,
                        'order': 0,
                    },
                    {
                        'name': {
                            'en': 'Burrata Caprese',
                            'pt': 'Burrata Caprese',
                            'es': 'Burrata Caprese'
                        },
                        'description': {
                            'en': 'Fresh burrata with heirloom tomatoes and basil from our garden',
                            'pt': 'Burrata fresca com tomates heirloom e manjericão da nossa horta',
                            'es': 'Burrata fresca con tomates de la huerta y albahaca de nuestro jardín'
                        },
                        'price': Decimal('16.00'),
                        'currency': 'EUR',
                        'is_vegetarian': True,
                        'is_gluten_free': True,
                        'allergens': ['dairy'],
                        'tags': ['vegetarian', 'gluten-free'],
                        'is_featured': False,
                        'is_available': True,
                        'order': 1,
                    },
                ]
            },
            {
                'name': {
                    'en': 'Main Courses',
                    'pt': 'Pratos Principais',
                    'es': 'Platos Principales'
                },
                'description': {
                    'en': 'Our signature dishes',
                    'pt': 'Os nossos pratos de assinatura',
                    'es': 'Nuestros platos estrella'
                },
                'order': 2,
                'items': [
                    {
                        'name': {
                            'en': 'Dry-Aged Ribeye',
                            'pt': 'Bife Maturado',
                            'es': 'Chuletón Madurado'
                        },
                        'description': {
                            'en': '28-day aged ribeye steak with roasted seasonal vegetables',
                            'pt': 'Bife maturado 28 dias com vegetais assados da época',
                            'es': 'Chuletón madurado 28 días con verduras de temporada asadas'
                        },
                        'price': Decimal('42.00'),
                        'currency': 'EUR',
                        'is_vegetarian': False,
                        'is_gluten_free': True,
                        'allergens': [],
                        'tags': ['gluten-free'],
                        'is_featured': True,
                        'is_available': True,
                        'order': 0,
                    },
                    {
                        'name': {
                            'en': 'Pan-Seared Salmon',
                            'pt': 'Salmão Grelhado',
                            'es': 'Salmón a la Plancha'
                        },
                        'description': {
                            'en': 'Atlantic salmon with herb butter and quinoa pilaf',
                            'pt': 'Salmão do Atlântico com manteiga de ervas e pilaf de quinoa',
                            'es': 'Salmón del Atlántico con mantequilla de hierbas y pilaf de quinoa'
                        },
                        'price': Decimal('32.00'),
                        'currency': 'EUR',
                        'is_vegetarian': False,
                        'is_gluten_free': True,
                        'allergens': ['fish', 'dairy'],
                        'tags': ['gluten-free', 'healthy'],
                        'is_featured': False,
                        'is_available': True,
                        'order': 1,
                    },
                ]
            },
            {
                'name': {
                    'en': 'Desserts',
                    'pt': 'Sobremesas',
                    'es': 'Postres'
                },
                'description': {
                    'en': 'Sweet endings to your meal',
                    'pt': 'Finais doces para a sua refeição',
                    'es': 'Finales dulces para su comida'
                },
                'order': 3,
                'items': [
                    {
                        'name': {
                            'en': 'Classic Tiramisu',
                            'pt': 'Tiramisu Clássico',
                            'es': 'Tiramisú Clásico'
                        },
                        'description': {
                            'en': 'Traditional Italian dessert with espresso and mascarpone',
                            'pt': 'Sobremesa italiana tradicional com café expresso e mascarpone',
                            'es': 'Postre italiano tradicional con café expreso y mascarpone'
                        },
                        'price': Decimal('12.00'),
                        'currency': 'EUR',
                        'is_vegetarian': True,
                        'is_gluten_free': False,
                        'allergens': ['dairy', 'eggs', 'gluten'],
                        'tags': ['vegetarian'],
                        'is_featured': False,
                        'is_available': True,
                        'order': 0,
                    },
                    {
                        'name': {
                            'en': 'Chocolate Lava Cake',
                            'pt': 'Bolo de Chocolate Derretido',
                            'es': 'Tarta de Chocolate Fundido'
                        },
                        'description': {
                            'en': 'Warm chocolate cake with a molten center, served with vanilla ice cream',
                            'pt': 'Bolo de chocolate quente com centro derretido, servido com gelado de baunilha',
                            'es': 'Tarta de chocolate caliente con centro fundido, servida con helado de vainilla'
                        },
                        'price': Decimal('13.00'),
                        'currency': 'EUR',
                        'is_vegetarian': True,
                        'is_gluten_free': False,
                        'allergens': ['dairy', 'eggs', 'gluten'],
                        'tags': ['vegetarian', 'popular'],
                        'is_featured': True,
                        'is_available': True,
                        'order': 1,
                    },
                ]
            },
        ]

        # Create sections and items
        for section_data in sections_data:
            items_data = section_data.pop('items')
            section = MenuSection.objects.create(
                menu=demo_menu,
                name=section_data['name'],
                description=section_data.get('description', {}),
                order=section_data['order'],
                is_active=True,
            )
            self.stdout.write(self.style.SUCCESS(f'  Created section: {section.name.get("en", "Untitled")}'))

            for item_data in items_data:
                MenuItem.objects.create(
                    section=section,
                    **item_data
                )
                self.stdout.write(self.style.SUCCESS(f'    Created item: {item_data["name"].get("en", "Untitled")}'))

        self.stdout.write(self.style.SUCCESS('\n✅ Successfully seeded demo menu data!'))
        self.stdout.write(self.style.SUCCESS(f'   Demo Instance: {demo_instance.name} (ID: {demo_instance.id})'))
        self.stdout.write(self.style.SUCCESS(f'   Demo Menu: {demo_menu.name} (ID: {demo_menu.id})'))
        self.stdout.write(self.style.SUCCESS(f'   Sections: {MenuSection.objects.filter(menu=demo_menu).count()}'))
        self.stdout.write(self.style.SUCCESS(f'   Items: {MenuItem.objects.filter(section__menu=demo_menu).count()}'))

