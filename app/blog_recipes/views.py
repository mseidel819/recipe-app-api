"""
views for blog-recipe api
"""
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes
)
from rest_framework import viewsets, mixins
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
        parameters=[
            OpenApiParameter(
                name="authors",
                type=OpenApiTypes.STR,
                description="Filter by author IDs(commas separated)",
            ),
            OpenApiParameter(
                name="categories",
                type=OpenApiTypes.STR,
                description="Filter by categories(commas separated)",
            ),
        ]
    ),

)
class BlogRecipeViewSet(
        mixins.ListModelMixin,
        viewsets.GenericViewSet,
        mixins.RetrieveModelMixin,
     ):
    """
    Get individual recipe from the database
    """
    serializer_class = serializers.BlogRecipeDetailSerializer
    queryset = BlogRecipe.objects.all()
    lookup_field = "slug"
    # authentication_classes = (TokenAuthentication,)
    # permission_classes = (IsAuthenticated,)

    def _params_to_ints(self, qs):
        """
        Convert a list of string IDs to a list of integers
        """
        return [int(str_id) for str_id in qs.split(",")]

    def get_queryset(self):
        """
        Return objects for the current authenticated user only
        """
        authors = self.request.query_params.get("authors")
        categories = self.request.query_params.get("categories")
        queryset = self.queryset

        if authors:
            author_ids = self._params_to_ints(authors)
            queryset = queryset.filter(author__id__in=author_ids)

        if categories:
            categories = categories.split(",")
            queryset = queryset.filter(categories__name__in=categories)
        return queryset.order_by("-id").distinct()

    def get_serializer_class(self):
        """
        Return appropriate serializer class
        """
        if self.action == "list":
            return serializers.BlogRecipeSerializer
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
