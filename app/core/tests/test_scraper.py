"""
tests for scrape.py
"""
from django.test import TestCase

from core.management.commands.utils.get_urls import get_urls
from core.management.commands.utils.add_to_db import add_recipe_to_db

from core.models import (
    BlogRecipe,
    BlogIngredient,
    BlogInstruction,
    BlogNote
)

import json

with open(
    'core/management/commands/utils/blog_data.json',
    'r', encoding="utf-8"
      ) as file:
    data = json.load(file)

website = data['sallys-baking-addiction']


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

        href_list = get_urls(URL, HEADERS, website)
        self.assertTrue(href_list)
        for url in href_list:
            self.assertTrue(
                url.startswith("https://sallysbakingaddiction.com/")
                )

    def test_add_recipe_to_db(self):
        """
        Test that recipes are added to the database
        """

        href_list = get_urls(URL, HEADERS, website)
        add_recipe_to_db(href_list[:2], "bread", HEADERS, website)
        self.assertTrue(href_list)

        recipes = BlogRecipe.objects.all()
        ingredients = BlogIngredient.objects.all()
        instructions = BlogInstruction.objects.all()
        notes = BlogNote.objects.all()

        for recipe in recipes:
            self.assertTrue(recipe.title)
            self.assertTrue(recipe.author)
            self.assertTrue(recipe.categories)
            self.assertTrue(recipe.slug)
            self.assertTrue(recipe.link)
            self.assertGreaterEqual(recipe.rating, 0)
            self.assertGreaterEqual(recipe.num_reviews, 0)
            self.assertEqual(recipe.author.name, "Sally\'s Baking Addiction")

        for ingredient in ingredients:
            self.assertTrue(ingredient.ingredient)
            self.assertTrue(ingredient.ingredient_list)

        for instruction in instructions:
            self.assertTrue(instruction.instruction)
            self.assertTrue(instruction.recipe)

        for note in notes:
            self.assertTrue(note.note)
            self.assertTrue(note.recipe)

    def test_update_existing_recipes_in_db(self):
        """
        Test that recipes are updated in the database
        """

        href_list = get_urls(URL, HEADERS, website)
        add_recipe_to_db(href_list[:2], "bread", HEADERS, website)
        recipes1 = BlogRecipe.objects.all()
        ingredients1 = BlogIngredient.objects.all()
        instructions1 = BlogInstruction.objects.all()
        notes1 = BlogNote.objects.all()
        add_recipe_to_db(href_list[:2], "bread", HEADERS, website)
        self.assertTrue(href_list)

        recipes2 = BlogRecipe.objects.all()
        ingredients2 = BlogIngredient.objects.all()
        instructions2 = BlogInstruction.objects.all()
        notes2 = BlogNote.objects.all()

        for recipe in recipes1:
            self.assertTrue(recipe.title)
            self.assertTrue(recipe.author)
            self.assertTrue(recipe.categories)
            self.assertTrue(recipe.slug)
            self.assertTrue(recipe.link)
            self.assertGreaterEqual(recipe.rating, 0)
            self.assertGreaterEqual(recipe.num_reviews, 0)
            self.assertEqual(recipe.author.name, "Sally\'s Baking Addiction")

        for ingredient in ingredients1:
            self.assertTrue(ingredient.ingredient)
            self.assertTrue(ingredient.ingredient_list)

        for instruction in instructions1:
            self.assertTrue(instruction.instruction)
            self.assertTrue(instruction.recipe)

        for note in notes1:
            self.assertTrue(note.note)
            self.assertTrue(note.recipe)

        self.assertEqual(len(recipes1), len(recipes2))
        self.assertEqual(len(ingredients1), len(ingredients2))
        self.assertEqual(len(instructions1), len(instructions2))
        self.assertEqual(len(notes1), len(notes2))
