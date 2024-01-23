"""
This script scrapes Sally's Baking Addiction
for recipes and saves them to the DB.
"""
from core.management.commands.utils.get_urls import get_urls
from core.management.commands.utils.add_to_db import add_recipe_to_db

from django.core.management.base import BaseCommand

import json

with open(
    'core/management/commands/utils/blog_data.json',
    'r', encoding="utf-8"
      ) as file:
    data = json.load(file)


class Command(BaseCommand):
    """
    Django command to populate db with
    recipes from Sally's Baking Addiction
    """
    def add_arguments(self, parser):
        # Define the command line arguments
        parser.add_argument('website', nargs='+', type=str)
        #  add ategory argument
        parser.add_argument(
            '--category',
            nargs='+',
            type=str,
            help='Specify the category to scrape'
        )

    def handle(self, *args, **options):
        """Handle the command"""
        website = data[options['website'][0]]
        categories = options['category']
        if not categories:
            categories = website['categories']

        HEADERS = {'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X)\
                AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148'}

        for category in categories:
            cleaned_filename = category.split('/')[-1]
            url = f'{website["category_entry_url"]}{category}/'
            href_list = get_urls(url, HEADERS, website)
            add_recipe_to_db(href_list, cleaned_filename, HEADERS, website)
            print(f'recipes successfully compiled for {category}!')

        print('Complete!')
