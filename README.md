# recipe-app-api

There are two setions of this project. both require user authentication:

## app/recipe

- The /app/recipe which is a personal recipe storage system.
- It allows users to create, update, and manage their own recipes.
- It also allows users to tag recipes with different tags and ingredients.
- Built using Django REST Framework and the project is built using Docker. This API only lets users see their own personal recipes.

## app/blog_recipes

- Allows the user to see all of the recipes collected from specific food blogs. Users are only allowed to GET recipes from this API.
- The recipes are scraped from the food blogs using the scraper.py file.
- Built using Django REST Framework and the project is built using Docker.

## Endpoints

- DOCS can be found at '/api/docs'

## scraping recipes

In order to refresh the recipe DB, run the following command:

```
python manage.py scrape
```

TODO: add parameters to scrape.py to control how much is scraped
