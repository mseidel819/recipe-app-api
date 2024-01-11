"""
views for blog-recipe api
"""
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
)
from rest_framework import viewsets, mixins
# from rest_framework.decorators import api_view
# from rest_framework.response import Response
# from rest_framework.authentication import TokenAuthentication
# from rest_framework.permissions import IsAuthenticated

from core.models import (
    BlogRecipe,
    BlogAuthor,
)
from blog_recipes import serializers


@extend_schema_view(
    list=extend_schema(
        description="Get list of recipes",
    ),

)
class BlogRecipeViewSet(
    # viewsets.ModelViewSet
        mixins.ListModelMixin,
        viewsets.GenericViewSet,
        mixins.RetrieveModelMixin,
     ):
    """
    Manage recipes in the database
    """
    serializer_class = serializers.BlogRecipeDetailSerializer
    queryset = BlogRecipe.objects.all()
    lookup_field = "slug"
    # authentication_classes = (TokenAuthentication,)
    # permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        """
        Return appropriate serializer class
        """
        if self.action == "list":
            return serializers.BlogRecipeSerializer
        # elif self.action == "upload_image":
        #     return serializers.RecipeImageSerializer
        return self.serializer_class


@extend_schema_view(
    list=extend_schema(
        description="Get list of authors",
    ),

)
class AuthorViewSet(
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    """
    Manage Authors in the database
    """
    # authentication_classes = (TokenAuthentication,)
    # permission_classes = (IsAuthenticated,)
    serializer_class = serializers.BlogAuthorSerializer
    queryset = BlogAuthor.objects.all()
