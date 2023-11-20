from bs4 import BeautifulSoup
import time
import requests


def get_soup(url):
    # added to make sure we don't violate Pro Football Reference's use policy around rate limiting
    time.sleep(3)
    return BeautifulSoup(requests.get(url).text, 'html.parser')

