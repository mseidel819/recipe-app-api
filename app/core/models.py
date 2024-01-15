"""
Create Models for the core app
"""
import uuid
import os
from django.conf import settings
from django.db import models
from django.utils.text import slugify


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


def blog_recipe_image_file_path(instance, filename):
    """
    Generate file path for new recipe image
    """
    ext = os.path.splitext(filename)[1]  # get the extension
    filename = f'{uuid.uuid4()}{ext}'  # generate a unique filename
    return os.path.join('uploads', 'blog-recipe', filename)  # return the path


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
        related_name='recipes',
        on_delete=models.CASCADE
    )
    categories = models.ManyToManyField('BlogCategory')
    slug = models.SlugField(blank=True, max_length=100)
    link = models.CharField(max_length=255, blank=True)
    rating = models.FloatField()
    num_reviews = models.IntegerField()
    description = models.TextField(blank=True)
    prep_time = models.CharField(max_length=255)
    cook_time = models.CharField(max_length=255)
    total_time = models.CharField(max_length=255)
    servings = models.CharField(max_length=255)

    def save(self, *args, **kwargs):
        """saves the slug and adds one, if not provided"""
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} by {self.author}"


class BlogImage(models.Model):
    """
    Image object
    """
    recipe = models.ForeignKey(
        BlogRecipe,
        related_name='images',
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=255)
    image_url = models.ImageField(null=True,
                                  upload_to=blog_recipe_image_file_path)

    def __str__(self):
        return self.name


class BlogIngredientList(models.Model):
    """
    Ingredient list object
    """
    recipe = models.ForeignKey(
        BlogRecipe,
        related_name='ingredient_list',
        on_delete=models.CASCADE
    )
    title = models.TextField()

    def __str__(self):
        return self.title


class BlogIngredient(models.Model):
    """
    Ingredient object
    """
    ingredient_list = models.ForeignKey(
        BlogIngredientList,
        related_name='ingredients',
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
        related_name='instructions',
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
        related_name='notes',
        on_delete=models.CASCADE
    )
    note = models.TextField()

    def __str__(self):
        return self.note


class BlogCategory(models.Model):
    """
    Category object
    """
    name = models.CharField(max_length=255)
    author = models.ForeignKey(
        BlogAuthor,
        related_name='categories',
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name
