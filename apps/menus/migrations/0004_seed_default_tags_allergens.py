# Seed default tags and allergens

from django.db import migrations


def seed_default_tags(apps, schema_editor):
    """Create default menu tags"""
    MenuTag = apps.get_model('menus', 'MenuTag')
    
    default_tags = [
        {
            'id': 'vegetarian',
            'name': {'en': 'Vegetarian', 'pt': 'Vegetariano', 'es': 'Vegetariano'},
            'icon': 'Leaf',
            'color': 'bg-green-100 text-green-800',
            'category': 'Dietary',
            'order': 1,
        },
        {
            'id': 'vegan',
            'name': {'en': 'Vegan', 'pt': 'Vegano', 'es': 'Vegano'},
            'icon': 'Leaf',
            'color': 'bg-green-100 text-green-800',
            'category': 'Dietary',
            'order': 2,
        },
        {
            'id': 'gluten-free',
            'name': {'en': 'Gluten Free', 'pt': 'Sem Glúten', 'es': 'Sin Gluten'},
            'icon': 'GlassWater',
            'color': 'bg-blue-100 text-blue-800',
            'category': 'Dietary',
            'order': 3,
        },
        {
            'id': 'dairy-free',
            'name': {'en': 'Dairy Free', 'pt': 'Sem Laticínios', 'es': 'Sin Lácteos'},
            'icon': 'GlassWater',
            'color': 'bg-cyan-100 text-cyan-800',
            'category': 'Dietary',
            'order': 4,
        },
        {
            'id': 'spicy',
            'name': {'en': 'Spicy', 'pt': 'Picante', 'es': 'Picante'},
            'icon': 'Flame',
            'color': 'bg-red-100 text-red-800',
            'category': 'Taste',
            'order': 5,
        },
        {
            'id': 'popular',
            'name': {'en': 'Popular', 'pt': 'Popular', 'es': 'Popular'},
            'icon': 'Star',
            'color': 'bg-yellow-100 text-yellow-800',
            'category': 'Special',
            'order': 6,
        },
        {
            'id': 'chef-special',
            'name': {'en': "Chef's Special", 'pt': 'Especial do Chef', 'es': 'Especial del Chef'},
            'icon': 'ChefHat',
            'color': 'bg-purple-100 text-purple-800',
            'category': 'Special',
            'order': 7,
        },
        {
            'id': 'new',
            'name': {'en': 'New', 'pt': 'Novo', 'es': 'Nuevo'},
            'icon': 'Sparkles',
            'color': 'bg-pink-100 text-pink-800',
            'category': 'Special',
            'order': 8,
        },
        {
            'id': 'signature',
            'name': {'en': 'Signature', 'pt': 'Assinatura', 'es': 'Firma'},
            'icon': 'Crown',
            'color': 'bg-amber-100 text-amber-800',
            'category': 'Special',
            'order': 9,
        },
        {
            'id': 'healthy',
            'name': {'en': 'Healthy', 'pt': 'Saudável', 'es': 'Saludable'},
            'icon': 'Heart',
            'color': 'bg-emerald-100 text-emerald-800',
            'category': 'Dietary',
            'order': 10,
        },
    ]
    
    for tag_data in default_tags:
        MenuTag.objects.get_or_create(
            id=tag_data['id'],
            defaults=tag_data
        )


def seed_default_allergens(apps, schema_editor):
    """Create default allergens"""
    MenuAllergen = apps.get_model('menus', 'MenuAllergen')
    
    default_allergens = [
        {
            'id': 'gluten',
            'name': {'en': 'Gluten', 'pt': 'Glúten', 'es': 'Gluten'},
            'color': 'bg-orange-100 text-orange-800',
            'order': 1,
        },
        {
            'id': 'dairy',
            'name': {'en': 'Dairy', 'pt': 'Laticínios', 'es': 'Lácteos'},
            'color': 'bg-blue-100 text-blue-800',
            'order': 2,
        },
        {
            'id': 'nuts',
            'name': {'en': 'Nuts', 'pt': 'Nozes', 'es': 'Nueces'},
            'color': 'bg-yellow-100 text-yellow-800',
            'order': 3,
        },
        {
            'id': 'eggs',
            'name': {'en': 'Eggs', 'pt': 'Ovos', 'es': 'Huevos'},
            'color': 'bg-purple-100 text-purple-800',
            'order': 4,
        },
        {
            'id': 'fish',
            'name': {'en': 'Fish', 'pt': 'Peixe', 'es': 'Pescado'},
            'color': 'bg-cyan-100 text-cyan-800',
            'order': 5,
        },
        {
            'id': 'shellfish',
            'name': {'en': 'Shellfish', 'pt': 'Marisco', 'es': 'Mariscos'},
            'color': 'bg-red-100 text-red-800',
            'order': 6,
        },
        {
            'id': 'soy',
            'name': {'en': 'Soy', 'pt': 'Soja', 'es': 'Soja'},
            'color': 'bg-green-100 text-green-800',
            'order': 7,
        },
        {
            'id': 'sesame',
            'name': {'en': 'Sesame', 'pt': 'Sésamo', 'es': 'Sésamo'},
            'color': 'bg-amber-100 text-amber-800',
            'order': 8,
        },
        {
            'id': 'sulfites',
            'name': {'en': 'Sulfites', 'pt': 'Sulfitos', 'es': 'Sulfitos'},
            'color': 'bg-pink-100 text-pink-800',
            'order': 9,
        },
        {
            'id': 'pork',
            'name': {'en': 'Pork', 'pt': 'Porco', 'es': 'Cerdo'},
            'color': 'bg-rose-100 text-rose-800',
            'order': 10,
        },
    ]
    
    for allergen_data in default_allergens:
        MenuAllergen.objects.get_or_create(
            id=allergen_data['id'],
            defaults=allergen_data
        )


class Migration(migrations.Migration):

    dependencies = [
        ('menus', '0003_add_tags_and_allergens'),
    ]

    operations = [
        migrations.RunPython(seed_default_tags),
        migrations.RunPython(seed_default_allergens),
    ]

