"""
Menus app URLs
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MenuViewSet, MenuSectionViewSet, MenuItemViewSet, QRCodeViewSet, MenuTagViewSet, MenuAllergenViewSet

router = DefaultRouter()
router.register(r'menus', MenuViewSet, basename='menu')
router.register(r'menu-sections', MenuSectionViewSet, basename='menusection')
router.register(r'menu-items', MenuItemViewSet, basename='menuitem')
router.register(r'qrcodes', QRCodeViewSet, basename='qrcode')
router.register(r'menu-tags', MenuTagViewSet, basename='menutag')
router.register(r'menu-allergens', MenuAllergenViewSet, basename='menuallergen')

urlpatterns = [
    path('', include(router.urls)),
]
