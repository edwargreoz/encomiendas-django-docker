from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenBlacklistView,
)
from envios.auth import EncomiendaTokenView
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)
from envios.viewsets import EncomiendaViewSet
from envios import api_views
from envios.api_auth import LoginCookieView, LogoutCookieView

router = DefaultRouter()
router.register('encomiendas', EncomiendaViewSet, basename='encomienda')

urlpatterns = [
    path('auth/token/', EncomiendaTokenView.as_view(), name='token_obtain'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/token/blacklist/', TokenBlacklistView.as_view(), name='token_blacklist'),
    path('auth/login/cookie/', LoginCookieView.as_view(), name='login-cookie'),
    path('auth/logout/cookie/', LogoutCookieView.as_view(), name='logout-cookie'),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(), name='swagger'),
    path('clientes/', api_views.ClienteListView.as_view(), name='cliente-list'),
    path('rutas/', api_views.RutaListView.as_view(), name='ruta-list'),
    path('', include(router.urls)),
]
