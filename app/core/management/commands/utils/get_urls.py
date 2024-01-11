"""
Getting urls from a category page
"""
import copy
import requests
from bs4 import BeautifulSoup as bs


def get_urls(url, headers):
    """
    gets all urls for the recipes in a category and returns a list of them
    """
    url_copy = copy.copy(url)

    href_list = []

    print("getting urls....")
    while not url_copy == "":
        res = requests.get(url_copy, headers=headers)
        soup = bs(res.text, 'html.parser')
        links = soup.select('.archive-content > article > a')
        hrefs = [link.get('href') for link in links]

        print('Adding %s links to list...' % len(hrefs))
        href_list.extend(hrefs)
        next_url = ''

        if soup.select('.nav-links > .next'):
            next_url = soup.select('.nav-links > .next')[0].get('href')

        url_copy = next_url

    print(f'Url list completed ({len(href_list)} items)')
    return href_list
