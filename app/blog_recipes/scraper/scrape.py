"""
This script scrapes Sally's Baking Addiction for recipes and saves them to a json file.
"""
import json
from get_urls import get_urls
from create_json import create_json


categories = ['bread', "breakfast-treats", "desserts/cakes", "desserts/cookies", "desserts/pies"]

total = 0
HEADERS = {'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148'}

recipeData = []

for category in categories:
    cleaned_filename = category.replace("/", "-")
    url = f'https://sallysbakingaddiction.com/category/{category}/'
    href_list = get_urls(url, HEADERS)
    json_data = create_json(href_list, cleaned_filename, HEADERS)
    total += len(json_data)
    recipeData.extend(json_data)
    print(f'json successfully compiled for {category}!')

with open('blog_recipes/sallys-baking-addiction.json', "w") as json_file:
    json.dump(recipeData, json_file, indent=2)

print(f'Success! {total} recipes were added to sallys-baking-addiction.json')
