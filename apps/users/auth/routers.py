from rest_framework.routers import DefaultRouter

from apps.users.auth.auth_views import AccountUserViewSet

router = DefaultRouter()

router.register('user',AccountUserViewSet, basename='user')

urlpatterns = router.urls
