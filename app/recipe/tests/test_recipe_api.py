"""
tests for recipe api
"""
from decimal import Decimal
import tempfile
import os

from PIL import Image

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    Recipe,
    Tag,
    Ingredient
)


from recipe.serializers import (
    RecipeSerializer,
    RecipeDetailSerializer
)


RECIPES_URL = reverse("recipe:recipe-list")


def detail_url(recipe_id):
    """
    Return recipe detail url
    """
    return reverse("recipe:recipe-detail", args=[recipe_id])


def image_upload_url(recipe_id):
    """
    Return url for recipe image upload
    """
    return reverse("recipe:recipe-upload-image", args=[recipe_id])


def create_recipe(user, **params):
    """
    Helper function to create a recipe
    """
    defaults = {
        "title": "Sample recipe",
        "time_minutes": 10,
        "price": Decimal("5.00"),
        "description": "Sample description",
        "link": "http://sample.com/recipe"
    }
    defaults.update(params)
    return Recipe.objects.create(user=user, **defaults)


def create_user(**params):
    """
    Helper function to create a user
    """
    return get_user_model().objects.create_user(**params)


class PublicRecipeApiTests(TestCase):
    """
    Test unauthenticated recipe api access
    """
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """
        Test that authentication is required
        """
        res = self.client.get(RECIPES_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    """
    Test authenticated recipe api access
    """
    def setUp(self):
        self.user = create_user(
            email="test@example.com",
            password="test123"
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """
        Test retrieving a list of recipes
        """
        create_recipe(user=self.user)
        create_recipe(user=self.user)
        res = self.client.get(RECIPES_URL)
        recipes = Recipe.objects.all().order_by("-id")
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipes_limited_to_user(self):
        """
        Test retrieving recipes for user
        """
        user2 = create_user(
            email="user2@example.com",
            password="test123")
        create_recipe(user=user2)
        create_recipe(user=self.user)
        res = self.client.get(RECIPES_URL)
        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_view_recipe_detail(self):
        """
        Test viewing a recipe detail
        """
        recipe = create_recipe(user=self.user)
        url = detail_url(recipe.id)
        res = self.client.get(url)
        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)

    def test_create_basic_recipe(self):
        """
        Test creating recipe
        """
        payload = {
            "title": "Chocolate cheesecake",
            "time_minutes": 30,
            "price": Decimal("5.00")
        }
        res = self.client.post(RECIPES_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data["id"])
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.user, self.user)

    def test_parital_update(self):
        """
        Test updating a recipe with patch
        """
        original_link = "http://sample.com/recipe"
        recipe = create_recipe(
             user=self.user,
             title="sample title",
             link=original_link)

        payload = {"title": "new title"}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload["title"])
        self.assertEqual(recipe.link, original_link)
        self.assertEqual(recipe.user, self.user)

    def test_full_update(self):
        """
        Test updating a recipe with put
        """
        recipe = create_recipe(
            user=self.user,
            title="sample title",
            link="http://sample.com/recipe",
            description="sample description"
            )
        payload = {
            "title": "new title",
            "description": "new description",
            "link": "http://sample.com/new_recipe",
            "time_minutes": 25,
            "price": Decimal("5.00")
        }
        url = detail_url(recipe.id)
        res = self.client.put(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.user, self.user)

    def test_update_user_returns_error(self):
        """
        Test updating a recipe with put
        """
        user2 = create_user(
            email="user2@example.com",
            password="test123")
        recipe = create_recipe(
            user=self.user
            )
        payload = {
            "user": user2.id
        }
        url = detail_url(recipe.id)
        self.client.patch(url, payload)
        recipe.refresh_from_db()
        self.assertEqual(recipe.user, self.user)

    def test_delete_recipe(self):
        """
        Test deleting a recipe
        """
        recipe = create_recipe(user=self.user)
        url = detail_url(recipe.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())

    def test_delete_other_users_recipe_error(self):
        """
        Test deleting a recipe
        """
        user2 = create_user(
            email="user2@example.com",
            password="test123")
        recipe = create_recipe(user=user2)
        url = detail_url(recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())

    def test_create_recipe_with_new_tags(self):
        """
        Test creating a recipe with tags
        """
        payload = {
            "title": "Avocado lime cheesecake",
            "tags": [{"name": "vegan"}, {"name": "dessert"}],
            "time_minutes": 60,
            "price": Decimal("20.00")
        }
        res = self.client.post(RECIPES_URL, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.tags.count(), 2)
        for tag in payload["tags"]:
            exists = recipe.tags.filter(
                name=tag['name'],
                user=self.user
            ).exists()
            self.assertTrue(exists)

    def test_create_recipe_with_existing_tags(self):
        """
        Test creating a recipe with tags
        """
        tag1 = Tag.objects.create(user=self.user, name="vegan")
        payload = {
            "title": "Avocado lime cheesecake",
            "tags": [{"name": "vegan"}, {"name": "dessert"}],
            "time_minutes": 60,
            "price": Decimal("20.00")
        }
        res = self.client.post(RECIPES_URL, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.tags.count(), 2)
        self.assertIn(tag1, recipe.tags.all())
        for tag in payload["tags"]:
            exists = recipe.tags.filter(
                name=tag['name'],
                user=self.user
            ).exists()
            self.assertTrue(exists)

    def test_create_tag_on_update(self):
        """
        Test creating a tag on update
        """
        recipe = create_recipe(user=self.user)
        payload = {
            "tags": [{"name": "Lunch"}],
        }
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # recipe.refresh_from_db() # not needed for many-to-many
        new_tag = Tag.objects.get(user=self.user, name="Lunch")
        self.assertIn(new_tag, recipe.tags.all())

    def test_update_recipe_assign_tags(self):
        """
        Test updating a recipe with tags
        """
        tag_breakfast = Tag.objects.create(user=self.user, name='Breakfast')
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag_breakfast)

        tag_lunch = Tag.objects.create(user=self.user, name='Lunch')
        payload = {
            "tags": [{"name": "Lunch"}]
        }
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(tag_lunch, recipe.tags.all())
        self.assertNotIn(tag_breakfast, recipe.tags.all())

    def test_clear_recipe_tags(self):
        """
        Test clearing a recipe's tags
        """
        tag = Tag.objects.create(user=self.user, name='Breakfast')
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag)
        payload = {
            "tags": []
        }
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.tags.count(), 0)

    def test_create_recipe_with_new_ingredients(self):
        """
        Test creating a recipe with ingredients
        """
        payload = {
            "title": "Avocado lime cheesecake",
            "ingredients": [{"name": "avocado"}, {"name": "lime"}],
            "time_minutes": 60,
            "price": Decimal("20.00")
        }
        res = self.client.post(RECIPES_URL, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.ingredients.count(), 2)
        for ingredient in payload["ingredients"]:
            exists = recipe.ingredients.filter(
                name=ingredient['name'],
                user=self.user
            ).exists()
            self.assertTrue(exists)

    def test_create_recipe_with_existing_ingredients(self):
        """
        Test creating a recipe with ingredients
        """
        ingredient1 = Ingredient.objects.create(user=self.user, name="avocado")
        payload = {
            "title": "Avocado lime cheesecake",
            "ingredients": [{"name": "avocado"}, {"name": "lime"}],
            "time_minutes": 60,
            "price": Decimal("20.00")
        }
        res = self.client.post(RECIPES_URL, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.ingredients.count(), 2)
        self.assertIn(ingredient1, recipe.ingredients.all())
        for ingredient in payload["ingredients"]:
            exists = recipe.ingredients.filter(
                name=ingredient['name'],
                user=self.user
            ).exists()
            self.assertTrue(exists)

    def test_create_ingredient_on_update(self):
        """test creating an ingredient when updating recipe"""
        recipe = create_recipe(user=self.user)

        payload = {
            'ingredients': [{"name": 'Limes'}]
        }
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_ingredient = Ingredient.objects.get(user=self.user, name="Limes")
        self.assertIn(new_ingredient, recipe.ingredients.all())

    def test_update_recipe_assign_ingredients(self):
        """
        Test updating a recipe with existing ingredients
        """
        ingredient_avocado = Ingredient.objects.create(
            user=self.user, name='Avocado'
            )
        recipe = create_recipe(user=self.user)
        recipe.ingredients.add(ingredient_avocado)

        ingredient_lime = Ingredient.objects.create(
            user=self.user, name='Lime'
            )
        payload = {
            "ingredients": [{"name": "Lime"}]
        }
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(ingredient_lime, recipe.ingredients.all())
        self.assertNotIn(ingredient_avocado, recipe.ingredients.all())

    def test_clear_recipe_ingredients(self):
        """
        Test clearing a recipe's ingredients
        """
        ingredient = Ingredient.objects.create(user=self.user, name='Avocado')
        recipe = create_recipe(user=self.user)
        recipe.ingredients.add(ingredient)
        payload = {
            "ingredients": []
        }
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.ingredients.count(), 0)

    def test_filter_by_tags(self):
        """
        Test returning recipes with specific tags
        """
        recipe1 = create_recipe(user=self.user, title="Thai vegetable curry")
        recipe2 = create_recipe(user=self.user, title="Aubergine with tahini")
        tag1 = Tag.objects.create(user=self.user, name="vegan")
        tag2 = Tag.objects.create(user=self.user, name="vegetarian")
        recipe1.tags.add(tag1)
        recipe2.tags.add(tag2)
        recipe3 = create_recipe(user=self.user, title="Fish and chips")
        params = {"tags": f"{tag1.id},{tag2.id}"}
        res = self.client.get(
            RECIPES_URL,
            params,
            )
        serializer1 = RecipeSerializer(recipe1)
        serializer2 = RecipeSerializer(recipe2)
        serializer3 = RecipeSerializer(recipe3)
        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)

    def test_filter_by_ingredients(self):
        """
        Test returning recipes with specific ingredients
        """
        recipe1 = create_recipe(user=self.user, title="Posh beans on toast")
        recipe2 = create_recipe(user=self.user, title="Chicken cacciatore")
        ingredient1 = Ingredient.objects.create(
            user=self.user,
            name="Feta cheese")
        ingredient2 = Ingredient.objects.create(user=self.user, name="Chicken")
        recipe1.ingredients.add(ingredient1)
        recipe2.ingredients.add(ingredient2)
        recipe3 = create_recipe(user=self.user, title="Steak and mushrooms")
        params = {"ingredients": f"{ingredient1.id},{ingredient2.id}"}
        res = self.client.get(
            RECIPES_URL,
            params,
            )
        serializer1 = RecipeSerializer(recipe1)
        serializer2 = RecipeSerializer(recipe2)
        serializer3 = RecipeSerializer(recipe3)
        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)


class ImageUploadTests(TestCase):
    """
    Test uploading image to recipe
    """
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="user@example.com",
            password="test123"
        )
        self.client.force_authenticate(self.user)
        self.recipe = create_recipe(user=self.user)

    def tearDown(self):
        self.recipe.image.delete()

    def test_upload_image_to_recipe(self):
        """
        Test uploading an image to recipe
        """
        url = image_upload_url(self.recipe.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as image_file:
            img = Image.new("RGB", (10, 10))
            img.save(image_file, format="JPEG")
            image_file.seek(0)
            res = self.client.post(
                url,
                {"image": image_file},
                format="multipart"
            )
        self.recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("image", res.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_upload_image_bad_request(self):
        """
        Test uploading an invalid image
        """
        url = image_upload_url(self.recipe.id)
        res = self.client.post(
            url,
            {"image": "notimage"},
            format="multipart"
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
