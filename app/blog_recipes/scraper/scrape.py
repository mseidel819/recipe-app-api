"""
This script scrapes Sally's Baking Addiction
for recipes and saves them to the DB.
"""
from get_urls import get_urls
from add_to_db import add_recipe_to_db

categories = [
            #   'bread',
            #   "breakfast-treats",
            #   "desserts/cakes",
            #   "desserts/cookies",
            "desserts/pies"
            ]

HEADERS = {'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X)\
           AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148'}


for category in categories:
    cleaned_filename = category.replace("/", "-")
    url = f'https://sallysbakingaddiction.com/category/{category}/'
    href_list = get_urls(url, HEADERS)
    add_recipe_to_db(href_list, cleaned_filename, HEADERS)
    print(f'json successfully compiled for {category}!')

print('Complete!')
