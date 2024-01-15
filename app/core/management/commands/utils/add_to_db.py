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
    def get_scraped_arrays(source, list_type, soup, li=True):
        if li:
            html = soup.select(f"{source} > {list_type} > li")
        else:
            html = soup.select(f"{source} > {list_type}")
        final_array = []
        for item in html:
            final_array.append(item.getText())
        return final_array

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
            existing_recipe.rating = 0 if get_text(
               website['selectors']['rating'],
               soup
                ) == "" else float(get_text(
                    website['selectors']['rating'],
                    soup))
            existing_recipe.num_reviews = 0 if get_text(
                website['selectors']['num_reviews'],
                soup
                ) == "" else get_text(
                    website['selectors']['num_reviews'],
                    soup)
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
                rating=0 if get_text(
                            website['selectors']['rating'], soup
                            ) == "" else float(
                                get_text(website['selectors']['rating'],
                                         soup)),
                num_reviews=0 if get_text(
                    website['selectors']['num_reviews'], soup
                    ) == "" else get_text(
                        website['selectors']['num_reviews'], soup
                        ),
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

        # messing with ingredient sections
            # check a ResultSet type
        if isinstance(soup.select(
                    website['selectors']['ingredients']['class']), list):
            ingredient_sections = soup.select(
             website['selectors']['ingredients']['class'])[0]
        else:
            ingredient_sections = soup.select(
                website['selectors']['ingredients']['class'])

        def map_get_text(sections):
            return [section.getText() for section in sections[0]]

        ing_section_titles = []
        if ingredient_sections.select(
             website['selectors']['ingredients']['section_title']
             ):
            ing_section_titles = map_get_text(
                [ingredient_sections.select(
                    website['selectors']['ingredients']['section_title']
                    )]
                )
        else:
            ing_section_titles = [""]

        ing_section_lists = []
        if ingredient_sections.select(
            website['selectors']['ingredients']['list_type']
             ):
            for ul in ingredient_sections.select(
                        website['selectors']['ingredients']['list_type']
                        ):
                li_arr = []
                for li in ul.select("li"):
                    li_arr.append(li.getText())
                ing_section_lists.append(li_arr)

        zipped_ingredient_titles_and_sections = zip(
            ing_section_titles, ing_section_lists
            )

        for title, ingredients in zipped_ingredient_titles_and_sections:
            ing_list, create = models.BlogIngredientList\
             .objects.update_or_create(
                recipe=recipe,
                title=title
             )
            for ingredient in ingredients:
                models.BlogIngredient.objects.update_or_create(
                    ingredient_list=ing_list,
                    ingredient=ingredient
                )

        instructions = get_scraped_arrays(
            website['selectors']['instructions']['class'],
            website['selectors']['instructions']['list_type'],
            soup,
            website['selectors']['instructions']['is_list_item']
            )
        for instruction in instructions:
            models.BlogInstruction.objects.update_or_create(
                recipe=recipe,
                instruction=instruction
            )

        if website['selectors']['notes']["class"] != "":
            notes = get_scraped_arrays(
                website['selectors']['notes']['class'],
                website['selectors']['notes']['list_type'],
                soup,
                website['selectors']['instructions']['is_list_item']

                )
            for note in notes:
                models.BlogNote.objects.update_or_create(
                    recipe=recipe,
                    note=note
                )

        existing_image = models.BlogImage.objects.filter(
                    recipe=recipe,
                    image_url__isnull=False
                ).first()

        if not existing_image:
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
                old_name = os.path.splitext(image_url.split("/")[-1])[0]
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

                # Update or create the BlogImage instance
                # with the uploaded image
                models.BlogImage.objects.update_or_create(
                    recipe=recipe,
                    image_url=uploaded_image,
                    name=old_name
                )

    print(f"Data collected!({len(href_list)} recipes added to db)")
