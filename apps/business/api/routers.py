from rest_framework.routers import DefaultRouter
from apps.business.api.bookings.bookings_views import BookingViewSet, CardViewSet
from apps.business.api.dwelling.dwelling_views import DwellingViewSet
from apps.business.api.inventory.inventory_views import InventoryViewSet
from apps.business.api.services.services_views import ServiceViewSet
from apps.business.api.shopping.shopping_views import ShoppingViewSet

router = DefaultRouter()

router.register('inventory', InventoryViewSet, basename='inventory')
router.register('dwelling', DwellingViewSet, basename='dwelling')
router.register('booking',BookingViewSet, basename='booking')
router.register('card',CardViewSet, basename='card')
router.register('service',ServiceViewSet, basename='service')
router.register('shopping',ShoppingViewSet, basename='shopping')

urlpatterns = router.urls