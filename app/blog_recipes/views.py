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
from rest_framework.response import Response

from core.models import (
    BlogRecipe,
    BlogAuthor,
)
from blog_recipes import serializers


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


@extend_schema_view(
    list=extend_schema(
        description="Get list of recipes",
        parameters=[
            OpenApiParameter(
                name="categories",
                type=OpenApiTypes.STR,
                description="Filter by categories(commas separated)",
            ),
        ]
    ),
)
class BlogRecipeByAuthorViewSet(
        mixins.ListModelMixin,
        viewsets.GenericViewSet,
        mixins.RetrieveModelMixin,
     ):
    """
    Get recipes from the database
    """

    serializer_class = serializers.BlogRecipeDetailSerializer
    queryset = BlogRecipe.objects.all()
    lookup_field = "id"
    # authentication_classes = (TokenAuthentication,)
    # permission_classes = (IsAuthenticated,)

    def get_queryset(self, *args, **kwargs):
        """
        Return objects for the current authenticated user only
        """
        author_id = self.kwargs.get("author_id")
        queryset = self.queryset
        if author_id:
            queryset = queryset.filter(author__id=int(author_id))

        return queryset.order_by("-id").distinct()

    def get_serializer_class(self):
        """
        Return appropriate serializer class
        """
        if self.action == "list":
            return serializers.BlogRecipeSerializer
        return self.serializer_class

    def list(self, request, *args, **kwargs):
        """
        return list of recipes by author,
        if provided. Otherwise, return all recipes
        """
        author = kwargs.get('author_id')
        categories = self.request.query_params.get("categories")

        if author is None:
            queryset = self.queryset.all().order_by("-id")
        else:
            queryset = self.queryset.filter(author__id=author)

        if categories:
            categories = categories.split(",")
            queryset = queryset.filter(categories__name__in=categories)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
