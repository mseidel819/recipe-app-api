"""
views for blog-recipe api
"""
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes
)

from django_filters.rest_framework import DjangoFilterBackend
from django_filters import FilterSet, CharFilter

from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination


from core.models import (
    BlogRecipe,
    BlogAuthor,
    Favorite
)
from blog_recipes import serializers


class CustomPageNumberPagination(PageNumberPagination):
    page_size = 15  # Set your desired page size
    page_size_query_param = 'page_size'
    max_page_size = 50

    def paginate_queryset(self, queryset, request, view=None):
        # Check if the view is an instance of YourSpecificViewClass
        if view and isinstance(view, BlogRecipeByAuthorViewSet):
            return super().paginate_queryset(queryset, request, view)
        else:
            # Return the entire queryset without pagination
            return None


class RecipeFilter(FilterSet):
    title = CharFilter(lookup_expr='icontains')

    class Meta:
        model = BlogRecipe
        fields = ['title']


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
    # pagination_class = PageNumberPagination
    pagination_class = CustomPageNumberPagination
    page_size_query_param = 'page_size'  # Set the query parameter for page size

    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter
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

        return queryset.distinct()

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
            queryset = self.queryset.all()
        else:
            queryset = self.queryset.filter(author__id=author)

        if categories:
            categories = categories.split(",")
            queryset = queryset.filter(categories__name__in=categories)

        filtered_queryset = self.filter_queryset(queryset)
        paginated_queryset = self.paginate_queryset(
            filtered_queryset.order_by("-rating")
            )

        serializer = self.get_serializer(paginated_queryset, many=True)
        return self.get_paginated_response(serializer.data)


class FavoritesViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
    mixins.DestroyModelMixin,
):
    """
    Manage favorites in the database
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    serializer_class = serializers.FavoriteBlogRecipesSerializer
    queryset = Favorite.objects.all()

    def get_queryset(self):
        """
        Return objects for the current authenticated user only
        """
        user = self.request.user
        queryset = self.queryset
        if user:
            queryset = queryset.filter(user=user)
            # queryset = queryset.filter(favorites__user=user)

        return queryset.order_by("-id").distinct()

    # do i need this?
    def perform_create(self, serializer):
        """
        Create a new object
        """
        serializer.save(user=self.request.user)

    # def get_serializer_class(self):
    #     """
    #     Return appropriate serializer class
    #     """
    #     if self.action == "list":
    #         return serializers.BlogRecipeSerializer
    #     return self.serializer_class

    def list(self, request, *args, **kwargs):
        """
        return list of recipes by author,
        if provided. Otherwise, return all recipes
        """
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """
        Delete a favorite
        """
        recipe_id = kwargs.get('pk')
        instance = self.queryset.filter(
            recipe__id=recipe_id, user=self.request.user
            )
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
