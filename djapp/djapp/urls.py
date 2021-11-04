"""djapp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import re_path
from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import SimpleRouter
from .views import NetworkViewSet, PortViewSet


router = SimpleRouter(trailing_slash=False)
router.register(r'network', NetworkViewSet, basename='network')
router.register(r'port', PortViewSet, basename='port')


urlpatterns = [
    path('v2/', include(router.urls)),
    path('admin/', admin.site.urls),
]


if getattr(settings, 'SWAGGER', False):
    from rest_framework import permissions
    from drf_yasg.views import get_schema_view
    from drf_yasg import openapi
    schema_view = get_schema_view(
        openapi.Info(title="cmp-iaas", default_version='v2'),
        public=True,
        permission_classes=(permissions.AllowAny,))
    urlpatterns += [
        re_path(rf'^swagger(?P<format>\.json|\.yaml|\.yml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
        path(f'swagger', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
        path(f'redoc', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    ]

if settings.DEBUG:
    from django.views.static import serve
    urlpatterns.extend([
        re_path(r'^static/(?P<path>.*)$', serve, {
            'document_root': settings.STATIC_ROOT,
        }),
    ])
