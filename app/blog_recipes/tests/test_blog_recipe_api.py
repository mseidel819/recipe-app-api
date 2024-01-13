"""
tests for recipe api
"""
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    BlogRecipe,
    BlogAuthor,
    BlogCategory,
)

from blog_recipes.serializers import (
    BlogRecipeSerializer,
    BlogRecipeDetailSerializer
)


RECIPES_URL = reverse("blog-recipes:blogrecipe-list", args=[0])


def detail_url(recipe_slug):
    """
    Return recipe detail url
    """
    return reverse("blog-recipes:blogrecipe-detail", args=[0, recipe_slug])


def create_recipe(author, **params):
    """
    Helper function to create a recipe
    """
    defaults = {
        "title": "Deliciously Moist Chocolate Layer Cake",
        "author": author,
        "slug": "triple-chocolate-layer-cake",
        "rating": 4.9,
        "num_reviews": 918,
        "link":
            "https://sallysbakingaddiction.com/triple-chocolate-layer-cake/",
        "prep_time": "30 minutes",
        "cook_time": "25 minutes",
        "total_time": "4 hours",
        "servings": "serves 12-16",
        "description": "This is my favorite homemade chocolate cake recipe."
    }
    defaults.update(params)
    return BlogRecipe.objects.create(**defaults)


def create_author(**params):
    """
    Helper function to create an author
    """
    defaults = {
        "name": "sally\'s baking addiction",
        "website_link": "https://sallysbakingaddiction.com/"
    }
    defaults.update(params)
    return BlogAuthor.objects.create(**defaults)


class BlogRecipeApiTests(TestCase):
    """
    Test blog recipe api access
    """
    def setUp(self):
        self.client = APIClient()
        self.author = create_author()

    def test_retrieve_recipes(self):
        """
        Test retrieving a list of recipes
        """
        create_recipe(author=self.author)
        create_recipe(
            title="cake2",
            author=self.author,
            slug="chocolate-cake-2")
        res = self.client.get(
            reverse("blog-recipes:blogrecipe-list", args=[self.author.id]))
        recipes = BlogRecipe.objects.all().order_by("id")
        serializer = BlogRecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_view_recipe_detail(self):
        """
        Test viewing a recipe detail
        """
        recipe = create_recipe(author=self.author)
        url = detail_url(recipe.id)
        res = self.client.get(url)
        serializer = BlogRecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)

    def test_filter_by_category_query_params(self):
        """
        Test filtering recipes by category query params
        """
        author = create_author(name="author2")
        cookies = BlogCategory.objects.create(
            name="cookies",
            author=author
        )
        pizza = BlogCategory.objects.create(
            name="pizza",
            author=author
        )

        cake = BlogCategory.objects.create(
            name="cake",
            author=author
        )

        recipe1 = create_recipe(
            author=self.author,
        )
        recipe1.categories.add(cookies)
        recipe2 = create_recipe(
            author=self.author,
            slug="recipe2",
        )
        recipe2.categories.add(cookies)
        recipe2.categories.add(pizza)

        recipe3 = create_recipe(
            author=self.author,
            slug="recipe3",
        )
        recipe3.categories.add(cake)
        res = self.client.get(
            reverse("blog-recipes:blogrecipe-list", args=[self.author.id]),
            {"categories": "cookies"}
        )
        serializer1 = BlogRecipeSerializer(recipe1)
        serializer2 = BlogRecipeSerializer(recipe2)
        serializer3 = BlogRecipeSerializer(recipe3)
        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)
        self.assertEqual(len(res.data), 2)
