"""
tests for scrape.py
"""
from django.test import TestCase

from blog_recipes.scraper.get_urls import get_urls
from blog_recipes.scraper.add_to_db import add_recipe_to_db

from core.models import (
    BlogRecipe,
    BlogIngredient,
    BlogInstruction,
    BlogNote
)


URL = "https://sallysbakingaddiction.com/category/bread/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X)\
    AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148"
}


class ScrapeTests(TestCase):
    """
    Test for scraping through running scrape.py
    """

    def test_get_urls(self):
        """
        Test that urls are returned
        """

        href_list = get_urls(URL, HEADERS)
        self.assertTrue(href_list)
        for url in href_list:
            self.assertTrue(
                url.startswith("https://sallysbakingaddiction.com/")
                )

    def test_add_recipe_to_db(self):
        """
        Test that recipes are added to the database
        """

        href_list = get_urls(URL, HEADERS)
        add_recipe_to_db(href_list[:2], "bread", HEADERS)
        self.assertTrue(href_list)

        recipes = BlogRecipe.objects.all()
        ingredients = BlogIngredient.objects.all()
        instructions = BlogInstruction.objects.all()
        notes = BlogNote.objects.all()

        for recipe in recipes:
            self.assertTrue(recipe.title)
            self.assertTrue(recipe.author)
            self.assertTrue(recipe.category)
            self.assertTrue(recipe.slug)
            self.assertTrue(recipe.link)
            self.assertGreaterEqual(recipe.rating, 0)
            self.assertGreaterEqual(recipe.num_reviews, 0)
            self.assertEqual(recipe.author.name, "sally\'s baking addiction")

        for ingredient in ingredients:
            self.assertTrue(ingredient.ingredient)
            self.assertTrue(ingredient.recipe)

        for instruction in instructions:
            self.assertTrue(instruction.instruction)
            self.assertTrue(instruction.recipe)

        for note in notes:
            self.assertTrue(note.note)
            self.assertTrue(note.recipe)

    def test_update_existing_recipes_in_DB(self):
        """
        Test that recipes are updated in the database
        """

        href_list = get_urls(URL, HEADERS)
        add_recipe_to_db(href_list[:2], "bread", HEADERS)
        add_recipe_to_db(href_list[:2], "bread", HEADERS)
        self.assertTrue(href_list)

        recipes = BlogRecipe.objects.all()
        ingredients = BlogIngredient.objects.all()
        instructions = BlogInstruction.objects.all()
        notes = BlogNote.objects.all()

        self.assertEqual(len(recipes), 2)
        for recipe in recipes:
            self.assertTrue(recipe.title)
            self.assertTrue(recipe.author)
            self.assertTrue(recipe.category)
            self.assertTrue(recipe.slug)
            self.assertTrue(recipe.link)
            self.assertGreaterEqual(recipe.rating, 0)
            self.assertGreaterEqual(recipe.num_reviews, 0)
            self.assertEqual(recipe.author.name, "sally\'s baking addiction")

        for ingredient in ingredients:
            self.assertTrue(ingredient.ingredient)
            self.assertTrue(ingredient.recipe)

        for instruction in instructions:
            self.assertTrue(instruction.instruction)
            self.assertTrue(instruction.recipe)

        for note in notes:
            self.assertTrue(note.note)
            self.assertTrue(note.recipe)
