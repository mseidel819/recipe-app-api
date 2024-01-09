"""
Tests for models
"""
from decimal import Decimal

from unittest.mock import patch
from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def create_user(email="user@example.com", password="test123"):
    """
    Create a sample user
    """
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        """
        Test creating a new user with an email is successful
        """
        email = 'test@example.com'
        password = 'testpass2123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """
        Test the email for a new user is normalized
        """
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com']
        ]
        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, 'test123')
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """
        Test creating user without an email raises error
        """
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'test123')

    def test_create_new_superuser(self):
        """
        Test creating a new superuser
        """
        user = get_user_model().objects.create_superuser(
            "test@example.com", "test123"
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_recipe(self):
        """
        Test creating a new recipe
        """
        user = get_user_model().objects.create_user(
            'test@example.com', 'test123')
        recipe = models.Recipe.objects.create(
            user=user,
            title="Steak and mushroom sauce",
            time_minutes=5,
            price=Decimal('5.00'),
            description="How to cook a steak",
        )
        self.assertEqual(str(recipe), recipe.title)

    def test_create_tag(self):
        """
        Test creating a new tag
        """
        user = create_user()
        tag = models.Tag.objects.create(
            user=user,
            name="Tag1"
        )

        self.assertEqual(str(tag), tag.name)

    def test_create_ingredient(self):
        """test creating ingredient successful"""
        user = create_user()
        ingredient = models.Ingredient.objects.create(
            user=user,
            name="Ingredient1"
        )

        self.assertEqual(str(ingredient), ingredient.name)

    @patch('core.models.uuid.uuid4')
    def test_recipe_file_name_uuid(self, mock_uuid):
        """
        Test that image is saved in the correct location
        """
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid
        file_path = models.recipe_image_file_path(None, 'myimage.jpg')
        expected_path = f'uploads/recipe/{uuid}.jpg'
        self.assertEqual(file_path, expected_path)

    def test_create_blog_recipe(self):
        """
        Test creating a new recipe
        """
        author = models.BlogAuthor.objects.create(
            name="sally\'s baking addiction",
            website_link="https://sallysbakingaddiction.com/"
        )

        recipe = models.BlogRecipe.objects.create(
            author=author,
            title="My Favorite Cornbread Recipe",
            slug="my-favorite-cornbread",
            rating=4.8,
            num_reviews=282,
            link="https://sallysbakingaddiction.com/my-favorite-cornbread/",
            prep_time="10 minutes",
            cook_time="20 minutes",
            total_time="1 hour",
            servings="9 servings",
            description="I was never a fan of cornbread until this recipe! After lots of recipe testing, I found the perfect ratio of ingredients for soft, moist, and buttery cornbread with crisp-crunchy edges. I guarantee this is the best cornbread recipe you\u2019ll try!"
        )
        self.assertEqual(str(recipe), 'My Favorite Cornbread Recipe by sally\'s baking addiction')
        self.assertEqual(str(author), 'sally\'s baking addiction')

    def test_create_blog_ingredient(self):
        """
        Test creating a new ingredient
        """
        author = models.BlogAuthor.objects.create(
            name="sally\'s baking addiction",
            website_link="https://sallysbakingaddiction.com/"
        )
        recipe = models.BlogRecipe.objects.create(
            author=author,
            title="My Favorite Cornbread Recipe",
            slug="my-favorite-cornbread",
            rating=4.8,
            num_reviews=282,
            link="https://sallysbakingaddiction.com/my-favorite-cornbread/",
            prep_time="10 minutes",
            cook_time="20 minutes",
            total_time="1 hour",
            servings="9 servings",
            description="I was never a fan of cornbread until this recipe! After lots of recipe testing, I found the perfect ratio of ingredients for soft, moist, and buttery cornbread with crisp-crunchy edges. I guarantee this is the best cornbread recipe you\u2019ll try!"
        )

        ingredient = models.BlogIngredient.objects.create(
            ingredient="1 cup (240ml) whole milk, at room temperature",
            recipe=recipe
        )
        self.assertEqual(str(ingredient), '1 cup (240ml) whole milk, at room temperature')

    def test_create_blog_instruction(self):
        """
        Test creating a new instruction
        """
        author = models.BlogAuthor.objects.create(
            name="sally\'s baking addiction",
            website_link="https://sallysbakingaddiction.com/"
        )
        recipe = models.BlogRecipe.objects.create(
            author=author,
            title="My Favorite Cornbread Recipe",
            slug="my-favorite-cornbread",
            rating=4.8,
            num_reviews=282,
            link="https://sallysbakingaddiction.com/my-favorite-cornbread/",
            prep_time="10 minutes",
            cook_time="20 minutes",
            total_time="1 hour",
            servings="9 servings",
            description="I was never a fan of cornbread until this recipe! After lots of recipe testing, I found the perfect ratio of ingredients for soft, moist, and buttery cornbread with crisp-crunchy edges. I guarantee this is the best cornbread recipe you\u2019ll try!"
        )

        instruction = models.BlogInstruction.objects.create(
            instruction="Preheat oven to 400\u00b0F (204\u00b0C). Spray a 9-inch or 10-inch cast iron skillet with nonstick spray or grease heavily with butter. Set aside.",
            recipe=recipe
        )
        self.assertEqual(str(instruction), 'Preheat oven to 400\u00b0F (204\u00b0C). Spray a 9-inch or 10-inch cast iron skillet with nonstick spray or grease heavily with butter. Set aside.')

    def test_create_blog_note(self):
        """
        Test creating a new note
        """
        author = models.BlogAuthor.objects.create(
            name="sally\'s baking addiction",
            website_link="https://sallysbakingaddiction.com/"
        )
        recipe = models.BlogRecipe.objects.create(
            author=author,
            title="My Favorite Cornbread Recipe",
            slug="my-favorite-cornbread",
            rating=4.8,
            num_reviews=282,
            link="https://sallysbakingaddiction.com/my-favorite-cornbread/",
            prep_time="10 minutes",
            cook_time="20 minutes",
            total_time="1 hour",
            servings="9 servings",
            description="I was never a fan of cornbread until this recipe! After lots of recipe testing, I found the perfect ratio of ingredients for soft, moist, and buttery cornbread with crisp-crunchy edges. I guarantee this is the best cornbread recipe you\u2019ll try!"
        )

        note = models.BlogNote.objects.create(
            note="Make Ahead & Freezing Instructions: Prepare cornbread through step 5. Cover tightly and store in the refrigerator for up to 2 days or freeze for up to 3 months. Thaw in the refrigerator overnight. Bring to room temperature, then continue with step 6. Baked cornbread freezes well for up to 3 months. Thaw in the refrigerator or on the counter, then warm up before enjoying.",
            recipe=recipe
        )
        self.assertEqual(str(note), 'Make Ahead & Freezing Instructions: Prepare cornbread through step 5. Cover tightly and store in the refrigerator for up to 2 days or freeze for up to 3 months. Thaw in the refrigerator overnight. Bring to room temperature, then continue with step 6. Baked cornbread freezes well for up to 3 months. Thaw in the refrigerator or on the counter, then warm up before enjoying.')