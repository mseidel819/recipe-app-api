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


def add_recipe_to_db(href_list, category, headers):
    """
    creates a json file from a list of urls
    """
    def get_text(identifier, soup):
        if len(soup.select(identifier)) > 0:
            return soup.select(identifier)[0].getText()
        return ""

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
        # main recipe class ".tasty-recipes"

        if soup.select('.tasty-recipes') is None:
            continue

        parsed_url = urlparse(url)

        author, create = models.BlogAuthor.objects.update_or_create(
            name="sally\'s baking addiction",
            website_link="https://sallysbakingaddiction.com/"
        )

        recipe, create = models.BlogRecipe.objects.update_or_create(
            title=get_text('.tasty-recipes-title', soup),
            author=author,
            category=category,
            slug=parsed_url.path.replace("/", ""),
            link=url,
            rating=0 if get_text(
                ".rating-label > .average", soup
                ) == "" else float(get_text(".rating-label > .average", soup)),
            num_reviews=0 if get_text(
                ".rating-label > .count", soup
                ) == "" else get_text(".rating-label > .count", soup),
            description=get_text(".tasty-recipes-description-body > p", soup),
            prep_time=get_text(".tasty-recipes-prep-time", soup),
            cook_time=get_text(".tasty-recipes-cook-time", soup),
            total_time=get_text(".tasty-recipes-total-time", soup),
            servings=get_text(".tasty-recipes-yield", soup),
        )

        ingredients = get_scraped_arrays(
            ".tasty-recipes-ingredients-body", "ul", soup
            )
        for ingredient in ingredients:
            models.BlogIngredient.objects.update_or_create(
                recipe=recipe,
                ingredient=ingredient
            )
        instructions = get_scraped_arrays(
            ".tasty-recipes-instructions-body", "ol", soup
            )
        for instruction in instructions:
            models.BlogInstruction.objects.update_or_create(
                recipe=recipe,
                instruction=instruction
            )
        notes = get_scraped_arrays(".tasty-recipes-notes-body", "ol", soup)
        for note in notes:
            models.BlogNote.objects.update_or_create(
                recipe=recipe,
                note=note
            )

        images = []

        img_html = soup.select(".type-post > .entry-content img")
        for img in img_html:
            img_src = img.get('src')
            if img_src[:5] == "https":
                images.append(img.get('src'))

        for image_url in images:
            # Download the image from the URL
            response = requests.get(image_url, headers=headers)

            # Try to open the image with PIL
            image = Image.open(BytesIO(response.content))

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
