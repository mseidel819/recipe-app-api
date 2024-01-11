"""
URL mappings for the blog-recipes app.
"""
from django.urls import (
    path,
    include,
)

from blog_recipes import views

from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register('recipes', views.BlogRecipeViewSet)
router.register('authors', views.AuthorViewSet)
router.register('ingredients', views.IngredientViewSet)
# router.register('authors', views.get_authors, basename='authors')


app_name = 'blog-recipes'

urlpatterns = [
    path('', include(router.urls)),
]
