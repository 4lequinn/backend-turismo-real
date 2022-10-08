from rest_framework.routers import DefaultRouter
from apps.business.api.dwelling.dwelling_views import DwellingViewSet

from apps.business.api.inventory.inventory_views import InventoryViewSet

router = DefaultRouter()

router.register('inventory', InventoryViewSet, basename='inventory')
router.register('dwelling', DwellingViewSet, basename='dwelling')

urlpatterns = router.urls