# recipe-app-api

This is a personal project that I needed to make because of how frustrated I get with recipe blogs. Currently, it is set up to extract all of the recipe info from Sally's Baking Addiction, and throw it into an API that I can access through another react app. The next step is to create a frontend in order to display the data so I can access my favorite recipes without all of the fluff and ads that make recipe blogs suck.

There are two setions of this project. both (will eventually) require user authentication:

## app/blog_recipes

- The /app/blog_recipes API is a recipe storage system that scrapes recipes from my most used food blogs.
- Allows the user to see all of the recipes collected from specific food blogs. Users are only allowed to GET recipes from this API.
- The recipes are scraped from the food blogs using the scrape.py file.
- Built using Django REST Framework and the project is built using Docker.

## app/recipe

- The /app/recipe which is a personal recipe storage system.
- It allows users to create, update, and manage their own recipes.
- It also allows users to tag recipes with different tags and ingredients.
- Built using Django REST Framework and the project is built using Docker. This API only lets users see their own personal recipes.

## Endpoints

- DOCS can be found at '/api/docs'

## scraping recipes

In order to refresh the recipe DB within the docker env, run the following command:

```
docker-compose run --rm app sh -c "python manage.py scrape [blog_name]"
```

A list of blogs to scrape are:

- sallys-baking-addiction
- budjet-bytes

These are updated in core/management/commands/utils/blog_data.json

TODO: add parameters to scrape.py to control how much is scraped
