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
router.register('recipes', views.BlogRecipeViewSet)
router.register('authors', views.AuthorViewSet)

app_name = 'blog-recipes'

urlpatterns = [
    path('', include(router.urls)),
]
