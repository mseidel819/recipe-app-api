"""
tests for recipe api
"""
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    BlogRecipe,
    # BlogIngredient,
    # BlogNote,
    # BlogInstruction,
    BlogAuthor,
    # BlogImage,
)

from blog_recipes.serializers import (
    BlogRecipeSerializer,
    BlogRecipeDetailSerializer
)


RECIPES_URL = reverse("blog-recipes:blogrecipe-list")


def detail_url(recipe_slug):
    """
    Return recipe detail url
    """
    return reverse("blog-recipes:blogrecipe-detail", args=[recipe_slug])


def create_recipe(author, **params):
    """
    Helper function to create a recipe
    """
    defaults = {
        "title": "Deliciously Moist Chocolate Layer Cake",
        "author": author,
        "category": "desserts-pies",
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
        res = self.client.get(RECIPES_URL)
        recipes = BlogRecipe.objects.all().order_by("id")
        serializer = BlogRecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_view_recipe_detail(self):
        """
        Test viewing a recipe detail
        """
        recipe = create_recipe(author=self.author)
        url = detail_url(recipe.slug)
        res = self.client.get(url)
        serializer = BlogRecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)
