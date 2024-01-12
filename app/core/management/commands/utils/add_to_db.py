"""
Add/update each recipe to the database
"""
from urllib.parse import urlparse
import os
import uuid
from io import BytesIO
import requests
from bs4 import BeautifulSoup as bs

from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile

from core import models


def add_recipe_to_db(href_list, category, headers, website):
    """
    creates a json file from a list of urls
    """
    def get_text(identifier, soup):
        if len(soup.select(identifier)) > 0:
            return soup.select(identifier)[0].getText()
        return ""

# possible mods for absrtation between blogs
    def get_scraped_arrays(source, list_type, soup):
        html = soup.select(f"{source} > {list_type} > li")
        final_array = []
        for item in html:
            final_array.append(item.getText())
        return final_array

    # scraping through each url
    print("Beginning data collection...")

    for url in href_list:
        res = requests.get(url, headers=headers)
        soup = bs(res.text, 'html.parser')

        if soup.select(website['selectors']['main_recipe_class']) is None:
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

        existing_recipe = models.BlogRecipe.objects.filter(
            slug=slug
        ).first()

        if existing_recipe:
            existing_recipe.title=get_text(website['selectors']['title'], soup),
            existing_recipe.slug=slug,
            existing_recipe.link=url,
            existing_recipe.rating=0 if get_text(
               website['selectors']['rating'], soup
                ) == "" else float(get_text(website['selectors']['rating'], soup))
            existing_recipe.num_reviews=0 if get_text(
                website['selectors']['num_reviews'], soup
                ) == "" else get_text(website['selectors']['num_reviews'], soup)
            existing_recipe.description=get_text(website['selectors']['description'], soup)
            existing_recipe.prep_time=get_text(website['selectors']['prep_time'], soup)
            existing_recipe.cook_time=get_text(website['selectors']['cook_time'], soup)
            existing_recipe.total_time=get_text(website['selectors']['total_time'], soup)
            existing_recipe.servings=get_text(website['selectors']['servings'], soup)
            existing_recipe.save()
            recipe = existing_recipe
        else:
            recipe, create = models.BlogRecipe.objects.update_or_create(
                title=get_text(website['selectors']['title'], soup),
                author=author,
                slug=slug,
                link=url,
                rating=0 if get_text(
                website['selectors']['rating'], soup
                    ) == "" else float(get_text(website['selectors']['rating'], soup)),
                num_reviews=0 if get_text(
                    website['selectors']['num_reviews'], soup
                    ) == "" else get_text(website['selectors']['num_reviews'], soup),
                description=get_text(website['selectors']['description'], soup),
                prep_time=get_text(website['selectors']['prep_time'], soup),
                cook_time=get_text(website['selectors']['cook_time'], soup),
                total_time=get_text(website['selectors']['total_time'], soup),
                servings=get_text(website['selectors']['servings'], soup),
            )

        if category not in recipe.categories.all():
            recipe.categories.add(category)

        ingredients = get_scraped_arrays(
            website['selectors']['ingredients']['class'], website['selectors']['ingredients']['list_type'], soup
            )
        for ingredient in ingredients:
            models.BlogIngredient.objects.update_or_create(
                recipe=recipe,
                ingredient=ingredient
            )
        instructions = get_scraped_arrays(
            website['selectors']['instructions']['class'], website['selectors']['instructions']['list_type'], soup
            )
        for instruction in instructions:
            models.BlogInstruction.objects.update_or_create(
                recipe=recipe,
                instruction=instruction
            )
        notes = get_scraped_arrays(website['selectors']['notes']['class'], website['selectors']['notes']['list_type'], soup)
        for note in notes:
            models.BlogNote.objects.update_or_create(
                recipe=recipe,
                note=note
            )

        images = []

        img_html = soup.select(website['selectors']['img_html'])
        for img in img_html:
            img_src = img.get('src')
            if img_src[:5] == "https":
                images.append(img.get('src'))

        for image_url in images:
            # Download the image from the URL
            response = requests.get(image_url, headers=headers)

            # Try to open the image with PIL
            image = Image.open(BytesIO(response.content))

            if image.mode != 'RGB':
                image = image.convert('RGB')

            # Generate a unique filename
            ext = os.path.splitext(image_url.split("/")[-1])[1]
            filename = f'{uuid.uuid4()}{ext}'

            # Create an InMemoryUploadedFile from the downloaded image
            image_io = BytesIO()
            image.save(image_io, format='JPEG')

            uploaded_image = InMemoryUploadedFile(
                image_io,  # file
                None,  # field_name
                filename,  # file name
                'image/jpeg',  # content_type
                image_io.tell,  # size
                None  # content_type_extra
            )

            # Update or create the BlogImage instance with the uploaded image
            models.BlogImage.objects.update_or_create(
                recipe=recipe,
                image_url=uploaded_image
            )

    print(f"Data collected!({len(href_list)} recipes added to db)")
