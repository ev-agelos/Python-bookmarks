"""Helper functions."""

from os.path import basename, isfile

from flask import current_app
import requests
from bs4 import BeautifulSoup


def get_url_thumbnail(url):
    """Save url's image, if does not exist already locally."""
    # TODO optimization: get chunks of data until find the og:image
    # same to the script for suggesting the title.
    try:
        response = requests.get(url)
    except OSError: # Host might now allow extenrnal requests
        return None
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        img_has_link =  soup.find('meta', {'property': 'og:image'})
        img_link = None
        if img_has_link:
            img_link = img_has_link.get('content')
        if img_link is not None:
            img_name = basename(img_link)
            destination = current_app.static_folder + '/img/' + img_name
            if not isfile(destination):
                img_response = requests.get(img_link, stream=True)
                if img_response.status_code == 200:
                    with open(destination, 'wb') as fob:
                        for chunk in img_response:
                            fob.write(chunk)
                else:
                    # TODO if not accessible i should re-try to download
                    return None
            return img_name
    return None
