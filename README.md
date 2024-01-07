# recipe-app-api

There are two setions of this project. both require user authentication:
The /app/recipe which is a personal recipe storage system. It allows users to create, update, and manage their own recipes. It also allows users to tag recipes with different tags and ingredients. The API is built using Django REST Framework and the project is built using Docker. This API only lets users see their personal recipes.

the /api/blog_recipes API requires authentication as well, but allows the user to see all of the recipes collected from specific food blogs. Users are only allowed to GET recipes from this API.

- DOCS can be found at '/api/docs'
