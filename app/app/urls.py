"""app URL Configuration

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
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView, SpectacularSwaggerView
    )
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('v1/admin/', admin.site.urls),
    path('v1/api/schema/', SpectacularAPIView.as_view(),
         name='schema'),  # yaml file
    path('v1/api/docs/', SpectacularSwaggerView.as_view(url_name='schema'),
         name='api-docs'),
    path('v1/api/user/', include('user.urls')),
    path('v1/api/recipe/', include('recipe.urls')),
    path('v1/api/blog-recipes/', include('blog_recipes.urls')),
    path('v1/api/password_reset/', include(
        'django_rest_passwordreset.urls', namespace='password_reset')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
