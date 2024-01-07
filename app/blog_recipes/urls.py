"""
URL mappings for the blog-recipes app.
"""
from django.urls import (
    path,
    include,
)

from blog_recipes import views

from rest_framework.routers import DefaultRouter

# from recipe import views

router = DefaultRouter()
router.register('', views.BlogRecipeViewSet)

app_name = 'blog-recipes'

urlpatterns = [
    path('', include(router.urls)),
]
