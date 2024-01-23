"""
Add/update each recipe to the database
"""
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup as bs

from core import models
from core.management.commands.utils.helpers import (
    get_rating,
    get_num_reviews,
    get_text,
    get_scraped_arrays,
    set_ingredients,
    set_instructions,
    set_images
)


def add_recipe_to_db(href_list, category, headers, website):
    """
    creates a json file from a list of urls
    """
    # scraping through each url
    print("Beginning data collection...")

    for url in href_list:
        res = requests.get(url, headers=headers)
        soup = bs(res.text, 'html.parser')
        if soup.select(
            website['selectors']['main_recipe_class']) is None or (
                len(soup.select(
                 website['selectors']['main_recipe_class'])) == 0):
            continue

        parsed_url = urlparse(url)

        author, create = models.BlogAuthor.objects.update_or_create(
            name=website['name'],
            website_link=website['website_link'],
        )
        category, create = models.BlogCategory.objects.update_or_create(
            name=category,
            author=author
        )

        slug = parsed_url.path.replace("/", "")

        rating = 0
        if website['name'] == "Half Baked Harvest":
            num_reviews = get_num_reviews(
                website['selectors']['num_reviews'], "data-attr", soup)
            rating = get_rating(
                website['selectors']['rating'], "data-attr", soup)
        else:
            rating = get_rating(
                website['selectors']['rating'], "text", soup)
            num_reviews = get_num_reviews(
                website['selectors']['num_reviews'], "text", soup)

        existing_recipe = models.BlogRecipe.objects.filter(
            author=author,
            slug=slug
        ).first()

        if existing_recipe:
            existing_recipe.title = get_text(
                website['selectors']['title'],
                soup)
            existing_recipe.slug = slug
            existing_recipe.link = url
            existing_recipe.rating = rating
            existing_recipe.num_reviews = num_reviews
            existing_recipe.description = get_text(
                website['selectors']['description'],
                soup)
            existing_recipe.prep_time = get_text(
                website['selectors']['prep_time'],
                soup)
            existing_recipe.cook_time = get_text(
                website['selectors']['cook_time'],
                soup)
            existing_recipe.total_time = get_text(
                website['selectors']['total_time'],
                soup)
            existing_recipe.servings = get_text(
                website['selectors']['servings'],
                soup)
            existing_recipe.save()
            recipe = existing_recipe
        else:
            recipe, create = models.BlogRecipe.objects.update_or_create(
                title=get_text(website['selectors']['title'], soup),
                author=author,
                slug=slug,
                link=url,
                rating=rating,
                num_reviews=num_reviews,
                description=get_text(website['selectors']['description'],
                                     soup),
                prep_time=get_text(website['selectors']['prep_time'],
                                   soup),
                cook_time=get_text(website['selectors']['cook_time'],
                                   soup),
                total_time=get_text(website['selectors']['total_time'],
                                    soup),
                servings=get_text(website['selectors']['servings'], soup)
            )

        if category not in recipe.categories.all():
            recipe.categories.add(category)

        set_ingredients(
            website['selectors']['ingredients']['class'],
            website['selectors']['ingredients']['section_title'],
            website['selectors']['ingredients']['list_type'],
            soup,
            recipe
        )

        set_instructions(
            website['selectors']['instructions']['class'],
            website['selectors']['instructions']['section_title'],
            website['selectors']['instructions']['list_type'],
            soup,
            recipe,
            website['name']
        )

        if website['selectors']['notes']["class"] != "":
            notes = get_scraped_arrays(
                website['selectors']['notes']['class'],
                website['selectors']['notes']['list_type'],
                soup,
                website['selectors']['notes']['is_list_item']
                )
            for note in notes:
                models.BlogNote.objects.update_or_create(
                    recipe=recipe,
                    note=note
                )

        set_images(recipe, website, soup, headers)

    print(f"Data collected!({len(href_list)} recipes added to db)")
