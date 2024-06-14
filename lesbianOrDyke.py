# Scrap movies from lawrens Mubi incredible list 

import requests
from bs4 import BeautifulSoup
import logging

mubiURL = 'https://mubi.com/fr/lists/dyke-cinema'

# Set up logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def scrap_each_movie(url):
    logger.info('Scraping start')
    response = requests.get(url)

    if response.status_code == 200 : 
        soup = BeautifulSoup(response.content, 'html.parser')
        return soup
    else: 
        logger.error('Failed to request Mubi website', response.status_code)
        return None


print(scrap_each_movie(mubiURL))