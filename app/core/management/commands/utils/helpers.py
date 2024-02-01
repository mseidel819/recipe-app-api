"""module for helper functions"""
import os
from io import BytesIO
import requests

from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils.text import slugify


from core import models


def get_text(identifier, soup):
    if len(soup.select(identifier)) > 0:
        return soup.select(identifier)[0].getText()
    return ""


# possible mods for absrtation between blogs
def get_scraped_arrays(source, list_type, soup, li=True):
    if li:
        html = soup.select(f"{source} > {list_type} > li")
    else:
        html = soup.select(f"{source} {list_type}")
    final_array = []
    for item in html:
        final_array.append(item.getText())
    return final_array


def map_get_text(sections):
    return [section.getText() for section in sections[0]]


def get_rating(rating, data_type, soup):
    """gets rating for recipe. accounts for text and data values"""
    if data_type == "data-attr":
        data = soup.select(rating)[0]
        return float(data.get('data-average'))

    if data_type == "text":
        return 0 if get_text(rating, soup) == "" else float(
            get_text(rating, soup)
            )
    return 0


def get_num_reviews(num_reviews, data_type, soup):
    """gets rating for recipe. accounts for text and data values"""
    if data_type == "data-attr":
        data = soup.select(num_reviews)[0]
        return float(data.get('data-count'))

    if data_type == "text":
        return 0 if get_text(num_reviews, soup) == "" else float(
            get_text(num_reviews, soup)
            )
    return 0


def get_section_titles(class_name, section_title, soup):
    """gets section titles for ingredients and instructions"""
    sections = soup.select(class_name)
    section_titles = []
    for section in sections:
        if section_title and section.select(
            section_title
                ):
            title_list = map_get_text(
                [section.select(section_title)]
                )
            for title in title_list:
                section_titles.append(title)
        else:
            section_titles.append('')

    return section_titles


def set_ingredients(class_name, section_title, list_type, soup, recipe):
    """sets ingredients for recipe"""
    ingredient_sections = soup.select(class_name)
    ing_section_titles = get_section_titles(class_name, section_title, soup)

    ing_section_lists = []
    for section in ingredient_sections:
        if section.select(list_type):
            for ul in section.select(list_type):
                li_arr = []
                for li in ul.select("li"):
                    text = li.getText()
                    if text[:1] == "▢":
                        text = text[2:]

                    li_arr.append(text)
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


def set_instructions(
        class_name, section_title, list_type, soup, recipe, website_name=""
        ):
    """sets instructions for recipe"""
    instruction_sections = soup.select(class_name)
    instruction_section_titles = get_section_titles(
        class_name, section_title, soup)

    instruction_section_lists = []
    for section in instruction_sections:
        if section.select(list_type):
            for ul in section.select(list_type):
                li_arr = []
                for li in ul.select("li"):
                    if website_name == "Half Baked Harvest":
                        # blog is fucked. no consitancy. nested spans SOMETIMES for no good reason
                        # get only direct span children
                        divs =  li.find('div', recursive=False)
                        span_arr = divs.find_all('span', recursive=False)

                        # for buffalo chicken
                        if len(span_arr) == 0:
                            span_arr = li.find_all("span", recursive=False)
                            if len(span_arr) == 0:
                                text= divs.get_text()
                                if text== "":
                                    print("1- no text here", recipe)
                                li_arr.append(text)
                        else:
                            for span in span_arr:
                                if span.getText() == "":
                                    print("2- no text here", recipe)

                                if span.getText()[:1].isdigit():
                                    li_arr.append(span.getText()[3:])
                                else:
                                    li_arr.append(span.getText())
                    else:
                        if li.getText() == "":
                            print("3-no text here", recipe)
                        li_arr.append(li.getText())
                instruction_section_lists.append(li_arr)

    zipped_instruction_titles_and_sections = zip(
        instruction_section_titles, instruction_section_lists
        )

    for title, instructions in zipped_instruction_titles_and_sections:
        instruction_list, create = models.BlogInstructionList\
            .objects.update_or_create(recipe=recipe, title=title)
        for instruction in instructions:
            models.BlogInstruction.objects.update_or_create(
                instruction_list=instruction_list,
                instruction=instruction
            )


def set_images(recipe, website, soup, headers):
    """downloads and saves image to db if it doesnt already exist"""
    existing_image = models.BlogImage.objects.filter(
                    recipe=recipe,
                    image_url__isnull=False
                ).first()

    if not existing_image:
        images = []

        img_html = soup.select(website['selectors']['img_html'])
        for img in img_html:
            img_src = img.get('src')
            if img_src is not None and img_src[:5] == "https":
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
            blog_name = slugify(website['name'])
            filename = f'{blog_name}_{old_name}{ext}'
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
                name=filename
            )
