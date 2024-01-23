"""
tests for recipe api
"""
from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APIClient


from core.models import (
    BlogRecipe,
    BlogAuthor,
    BlogCategory,
    BlogImage
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


def create_user(**params):
    """
    Helper function to create a user
    """
    return get_user_model().objects.create_user(**params)


def create_recipe(author, **params):
    """
    Helper function to create a recipe
    """
    defaults = {
        "title": "Deliciously Moist",
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
        "description": "This is my favorite homemade chocolate cake recipe.",
    }
    defaults.update(params)

    recipe = BlogRecipe.objects.create(**defaults)

    # Create related BlogImage instances (customize as needed)
    BlogImage.objects.create(
        recipe=recipe,
        image_url="https://example.com/image1.jpg",
        name="Image 1"
    )
    BlogImage.objects.create(
        recipe=recipe,
        image_url="https://example.com/image2.jpg",
        name="Image 2"
    )

    return recipe


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
        self.user = create_user(
            email="test@example.com",
            password="test123"
        )
        self.author = create_author()
        self.factory = RequestFactory()
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """
        Test retrieving a list of recipes
        """
        create_recipe(author=self.author)
        create_recipe(
            title="cake2",
            author=self.author,
            slug="chocolate-cake-2")

        request = self.factory.get(
            reverse("blog-recipes:blogrecipe-list", args=[self.author.id]))

        res = self.client.get(
            reverse("blog-recipes:blogrecipe-list", args=[self.author.id]))
        recipes = BlogRecipe.objects.all().order_by("id")
        serializer = BlogRecipeSerializer(
            recipes, many=True, context={'request': request})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data.get('results', []), serializer.data)

    def test_view_recipe_detail(self):
        """
        Test viewing a recipe detail
        """
        recipe = create_recipe(author=self.author)

        BlogImage.objects.create(
            recipe=recipe,
            image_url=(
                "https://sallysbakingaddiction.com/wp-content/"
                "uploads/2017/12/homemade-strawberry-cake-3.jpg"
            ),
            name="moist-chocolate-layer-cake"
        )

        url = detail_url(recipe.id)
        request = self.factory.get(url)
        res = self.client.get(url)
        serializer = BlogRecipeDetailSerializer(
            recipe, context={'request': request})
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
        request = self.factory.get(
            reverse("blog-recipes:blogrecipe-list", args=[self.author.id]))
        res = self.client.get(
            reverse("blog-recipes:blogrecipe-list", args=[self.author.id]),
            {"categories": "cookies"}
        )
        serializer1 = BlogRecipeSerializer(
            recipe1, context={'request': request})
        serializer2 = BlogRecipeSerializer(
            recipe2, context={'request': request})
        serializer3 = BlogRecipeSerializer(
            recipe3, context={'request': request})
        self.assertIn(serializer1.data, res.data.get('results', []))
        self.assertIn(serializer2.data, res.data.get('results', []))
        self.assertNotIn(serializer3.data, res.data.get('results', []))
        self.assertEqual(len(res.data.get('results', [])), 2)


class FavoriteApiTests(TestCase):
    """
    Test favorite api access
    """
    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email="test@example.com",
            password="test123"
        )
        self.author = create_author()
        # self.factory = RequestFactory()
        self.client.force_authenticate(self.user)

    def test_create_favorite(self):
        """
        Test creating a new favorite
        """
        recipe = create_recipe(author=self.author)
        payload = {"recipe_id": recipe.id}
        res = self.client.post(
            reverse("blog-recipes:favorite-list"), payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["recipe"]["id"], recipe.id)

    def test_create_favorite_duplicate(self):
        """
        Test creating a duplicate favorite
        """
        recipe = create_recipe(author=self.author)
        payload = {"recipe_id": recipe.id}
        self.client.post(
            reverse("blog-recipes:favorite-list"), payload)
        self.client.post(
            reverse("blog-recipes:favorite-list"), payload)
        # get the number of favorites for the recipe
        num_favorites = recipe.favorites.count()
        self.assertEqual(num_favorites, 1)

    def test_delete_favorite(self):
        """
        Test deleting a favorite
        """
        recipe = create_recipe(author=self.author)
        recipe2 = create_recipe(author=self.author, slug="recipe2")
        payload1 = {"recipe_id": recipe.id}
        payload2 = {"recipe_id": recipe2.id}
        self.client.post(
            reverse("blog-recipes:favorite-list"), payload1)
        self.client.post(
            reverse("blog-recipes:favorite-list"), payload2)
        res = self.client.delete(
            reverse("blog-recipes:favorite-detail", args=[recipe.id]))
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(res.data, None)
        self.assertEqual(recipe2.favorites.count(), 1)
