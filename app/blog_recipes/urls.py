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
# router.register('recipes', views.BlogRecipeViewSet)
router.register('', views.BlogRecipeByAuthorViewSet)
# router.register('<str:author>', views.BlogRecipeByAuthorViewSet)
# router.register('authors', views.AuthorViewSet)

app_name = 'blog-recipes'

urlpatterns = [
    path('', include(router.urls)),
    path('by-author/<int:author_id>/', include(router.urls)),
]
