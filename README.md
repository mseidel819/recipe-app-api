# recipe-app-api

Link to live API docs [here](https://peppy-alpaca-9050d7.netlify.app/v1/api/docs/).

This is a personal project that I needed to make because of how frustrated I get with recipe blogs. Currently, it is set up to extract all of the recipe info from a list of blogs and throw it into an API that I can access through another react app found at https://peppy-alpaca-9050d7.netlify.app/v1/api/docs/

In order to add and view favorites, the user must log in. Authentication is done using JWT.

## app/blog_recipes

- The v1/app/blog_recipes API is a recipe storage system that scrapes recipes from my most used food blogs.
- Allows the user to see all of the recipes collected from specific food blogs. Users are only allowed to GET recipes from this API.
- v1/api/blog-recipes/authors/ does not require authentication and returns a list of all of the authors that have recipes in the database.
- v1/api/blog-recipes/by-author/{author_id} returns a list of all of the recipes by a certain author in the database.
- v1/api/blog-recipes/favorites/ returns a list of all of the recipes that the user has favorited. (requires authentication)
- The recipes are scraped from the food blogs using the scrape.py file.
- In order to scrape a new blog, add the blog name and all relevant data to the blog_data.json file and run the scrape.py file.
- Built using Django REST Framework, Docker, AWS, Beautiful Soup, and PostgreSQL.

## app/recipe (in progress)

- The /app/recipe which is a personal recipe storage system.
- It allows users to create, update, and manage their own recipes.
- It also allows users to tag recipes with different tags and ingredients.
- Built using Django REST Framework and the project is built using Docker. This API only lets users see their own personal recipes.

## Endpoints

- DOCS can be found at 'v1/api/docs'

## scraping recipes

In order to refresh the recipe DB within the docker env, run the following command:

```

docker-compose run --rm app sh -c "python manage.py scrape [blog_name] --category [categories to scrape(no commas)]"

```

A list of blogs to scrape are:

- sallys-baking-addiction
- budget-bytes
- half-baked-harvest

These are updated in core/management/commands/utils/blog_data.json

### TODO:

- learn how to spell budget
- update tests for more thourough scenarios.
- write user tests
- fuzzy search-all, search-author,

### add filters and queries

- by rating. num-rating tiebreaker

reset password with email
