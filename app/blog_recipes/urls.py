"""
URL mappings for the blog-recipes app.
"""
from django.urls import (
    path,
    include,
)

from blog_recipes import views

from rest_framework.routers import DefaultRouter

router_recipes = DefaultRouter()
# router.register('recipes', views.BlogRecipeViewSet)
# router.register('authors', views.AuthorViewSet)
router_recipes.register('', views.BlogRecipeByAuthorViewSet)

router_author = DefaultRouter()
router_author.register('authors', views.AuthorViewSet, basename='blogauthor')

app_name = 'blog-recipes'

urlpatterns = [
    path('', include(router_author.urls)),
    path('by-author/<int:author_id>/', include(router_recipes.urls)),
]
