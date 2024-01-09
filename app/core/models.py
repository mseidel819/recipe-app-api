"""
Create Models for the core app
"""
import uuid
import os
from django.conf import settings
from django.db import models

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)


def recipe_image_file_path(instance, filename):
    """
    Generate file path for new recipe image
    """
    ext = os.path.splitext(filename)[1]  # get the extension
    filename = f'{uuid.uuid4()}{ext}'  # generate a unique filename
    return os.path.join('uploads', 'recipe', filename)  # return the path


class UserManager(BaseUserManager):
    """
    Custom user manager
    """
    def create_user(self, email, password=None, **extra_fields):
        """
        Creates and saves a new user
        """
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)  # encrypts the password
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """
        Creates and saves a new superuser
        """
        user = self.create_user(email, password)
        user.is_staff = True  # automatically created by PermissionsMixin
        user.is_superuser = True  # automatically created by PermissionsMixin
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model that supports using email instead of username
    """
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    objects = UserManager()

    USERNAME_FIELD = 'email'


class Recipe(models.Model):
    """
    Recipe object
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    time_minutes = models.IntegerField()
    price = models.DecimalField(decimal_places=2, max_digits=5)
    link = models.CharField(max_length=255, blank=True)
    ingredients = models.ManyToManyField('Ingredient')
    image = models.ImageField(null=True, upload_to=recipe_image_file_path)
    tags = models.ManyToManyField('Tag')

    def __str__(self):
        return self.title


class Tag(models.Model):
    """
    Tag object
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """
    Ingredient object
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


# blog recipe models. condiser merging with recipe models
class BlogAuthor(models.Model):
    """
    Author object
    """
    name = models.CharField(max_length=255)
    website_link = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class BlogRecipe(models.Model):
    """
    Recipe object
    """

    title = models.CharField(max_length=255)
    author = models.ForeignKey(
        BlogAuthor,
        on_delete=models.CASCADE
    )
    category = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    rating = models.IntegerField()
    num_reviews = models.IntegerField()
    description = models.TextField(blank=True)
    prep_time = models.CharField(max_length=255)
    cook_time = models.CharField(max_length=255)
    total_time = models.CharField(max_length=255)
    servings = models.CharField(max_length=255)
    link = models.CharField(max_length=255, blank=True)
    ingredients = models.ManyToManyField('BlogIngredient')
    instructions = models.ManyToManyField('BlogInstruction')
    # image = models.ImageField(null=True, upload_to=recipe_image_file_path)
    notes = models.ManyToManyField('BlogNote')

    def __str__(self):
        return f"{self.title} by {self.author}"


class BlogIngredient(models.Model):
    """
    Ingredient object
    """
    recipe = models.ForeignKey(
        BlogRecipe,
        on_delete=models.CASCADE
    )
    ingredient = models.TextField()

    def __str__(self):
        return self.ingredient


class BlogInstruction(models.Model):
    """
    Instruction object
    """
    recipe = models.ForeignKey(
        BlogRecipe,
        on_delete=models.CASCADE
    )
    instruction = models.TextField()

    def __str__(self):
        return self.instruction


class BlogNote(models.Model):
    """
    Notes object
    """
    recipe = models.ForeignKey(
        BlogRecipe,
        on_delete=models.CASCADE
    )
    note = models.TextField()

    def __str__(self):
        return self.note
