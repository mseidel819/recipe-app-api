"""
Creating a json file from a list of urls
"""
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup as bs


# fix the error handling for when something doesn't exist lines 15-19

def create_json(href_list, category, headers):
    """
    creates a json file from a list of urls
    """
    json_data = []
    # scraping through each url
    print("Beginning data collection...")
    for url in href_list:
        res = requests.get(url, headers=headers)
        soup = bs(res.text, 'html.parser')
        # main recipe class ".tasty-recipes"

        def get_text(identifier):

            if len(soup.select(identifier)) > 0:
                return soup.select(identifier)[0].getText()
            return ""

        def get_scraped_arrays(source, list_type):
            html = soup.select(f"{source} > {list_type} > li")
            final_array = []
            for item in html:
                final_array.append(item.getText())
            return final_array

        if not len(soup.select('.tasty-recipes')):
            continue

        title = get_text('.tasty-recipes-title')
        parsed_url = urlparse(url)
        slug = parsed_url.path.replace("/", "")
        rating = 0 if get_text(
            ".rating-label > .average"
            ) == "" else get_text(".rating-label > .average")
        num_reviews = 0 if get_text(
            ".rating-label > .count"
            ) == "" else get_text(".rating-label > .count")
        prep_time = get_text(".tasty-recipes-prep-time")
        cook_time = get_text(".tasty-recipes-cook-time")
        total_time = get_text(".tasty-recipes-total-time")
        serves = get_text(".tasty-recipes-yield")
        description = get_text(".tasty-recipes-description-body > p")
        ingredients = get_scraped_arrays(
            ".tasty-recipes-ingredients-body", "ul"
            )
        instructions = get_scraped_arrays(
            ".tasty-recipes-instructions-body", "ol"
            )
        notes = get_scraped_arrays(".tasty-recipes-notes-body", "ol")
        images = []
        img_html = soup.select(".type-post > .entry-content img")
        for img in img_html:
            img_src = img.get('src')
            if img_src[:5] == "https":
                images.append(img.get('src'))

        recipe_dict = {
            "title": title,
            "category": category,
            "slug": slug,
            "rating": float(rating),
            "num_reviews": int(num_reviews),
            "link": url,
            "images": images,
            "prep_time": prep_time,
            "cook_time": cook_time,
            "total_time": total_time,
            "serves": serves,
            "description": description,
            "ingredients": ingredients,
            "instructions": instructions,
            "notes": notes
        }

        json_data.append(recipe_dict)

    print(f"Data collected!({len(json_data)} recipes)")
    return json_data
