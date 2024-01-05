"""
tests for the ingredients API
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    Ingredient,
    Recipe,)

from recipe.serializers import IngredientSerializer

INGREDIENTS_URL = reverse("recipe:ingredient-list")


def detail_url(ingredient_id):
    """
    Return ingredient detail URL
    """
    return reverse("recipe:ingredient-detail", args=[ingredient_id])


def create_user(email="user@example.com", password="test123"):
    """
    Create a sample user
    """
    return get_user_model().objects.create_user(email, password)


class PublicIngredientsApiTests(TestCase):
    """
    Test the publicly available ingredients API
    """
    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """
        Test that login is required to access the endpoint
        """
        res = self.client.get(INGREDIENTS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsApiTests(TestCase):
    """
    Test the private ingredients API
    """
    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredient_list(self):
        """
        Test retrieving a list of ingredients
        """
        Ingredient.objects.create(user=self.user, name="Kale")
        Ingredient.objects.create(user=self.user, name="Salt")

        res = self.client.get(INGREDIENTS_URL)
        ingredients = Ingredient.objects.all().order_by("-name")
        serializer = IngredientSerializer(ingredients, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """
        Test that ingredients for the authenticated user are returned
        """
        user2 = get_user_model().objects.create_user(
            "user2@example.com", "test123"
        )
        Ingredient.objects.create(user=user2, name="Vinegar")
        ingredient = Ingredient.objects.create(user=self.user, name="Tumeric")

        res = self.client.get(INGREDIENTS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["name"], ingredient.name)
        self.assertNotIn("Vinegar", res.data)

    def test_update_ingredient_successful(self):
        """
        Test updating an ingredient
        """
        ingredient = Ingredient.objects.create(user=self.user, name="Sugar")
        payload = {"name": "Salt"}
        url = detail_url(ingredient.id)
        res = self.client.patch(url, payload)
        ingredient.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(ingredient.name, payload["name"])

    def test_delete_ingredient_successful(self):
        """
        Test deleting an ingredient
        """
        ingredient = Ingredient.objects.create(user=self.user, name="Sugar")
        url = detail_url(ingredient.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        ingredients = Ingredient.objects.filter(user=self.user)
        self.assertFalse(ingredients.exists())

    def test_filter_ingredients_assigned_to_recipes(self):
        """
        Test returning only ingredients assigned to recipes
        """
        ingredient1 = Ingredient.objects.create(user=self.user, name="Apples")
        ingredient2 = Ingredient.objects.create(user=self.user, name="Turkey")
        recipe = Recipe.objects.create(
            title="Apple crumble",
            time_minutes=5,
            price=Decimal("10.00"),
            user=self.user,
        )
        recipe.ingredients.add(ingredient1)
        res = self.client.get(INGREDIENTS_URL, {"assigned_only": 1})
        serializer1 = IngredientSerializer(ingredient1)
        serializer2 = IngredientSerializer(ingredient2)
        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_filter_ingredients_assigned_unique(self):
        """
        Test filtering ingredients by assigned returns unique items
        """
        ingredient = Ingredient.objects.create(user=self.user, name="Eggs")
        Ingredient.objects.create(user=self.user, name="Cheese")
        recipe1 = Recipe.objects.create(
            title="Eggs benedict",
            time_minutes=30,
            price=Decimal("12.00"),
            user=self.user,
        )
        recipe1.ingredients.add(ingredient)
        recipe2 = Recipe.objects.create(
            title="Coriander eggs on toast",
            time_minutes=20,
            price=Decimal("5.00"),
            user=self.user,
        )
        recipe2.ingredients.add(ingredient)
        res = self.client.get(INGREDIENTS_URL, {"assigned_only": 1})
        self.assertEqual(len(res.data), 1)
