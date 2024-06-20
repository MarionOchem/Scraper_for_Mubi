from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import requests
import concurrent.futures
import logging
import threading
import traceback

   
# Initialize a lock for synchronization
lock = threading.Lock()

# Set up logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Load the webpage and click the "Show More" button until all movies are loaded
def click_show_more_button(driver, url):
     logger.info('Starting clicking on "Show More"')

     driver.get(url)

     while True:

        try:

            # Wait up to 10 seconds for the "Afficher la suite" button to be clickable
            button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Afficher la suite']")))

            # Scroll the page to bring the button into view
            driver.execute_script("arguments[0].scrollIntoView();", button)

            # Click the button using JavaScript to bypass server interception
            driver.execute_script("arguments[0].click();", button)

            time.sleep(5)

        except Exception as e:
            print(f"Exception clicking button: {e}")
            break 



# Parse the page source, extract target data from movies and returns structured data
def scrape_movies(driver):
    logger.info('Starting scraping movies info')

    # Get the HTML source of the current page loaded in the WebDriver
    page_source = driver.page_source

    # Parse the HTML using BeautifulSoup
    soup = BeautifulSoup(page_source, "html.parser")

    # Find all <li> elements that contain movie information
    li_elements = soup.find_all("li", class_="css-1t2q5wf e18pxekp0")
    logger.info("number of li elements / movies : ", len(li_elements))

    lesbianOrDyke_dic = {}
    synopsis_link = []

    for li in li_elements:
        link_tag = li.find("a")
        link = link_tag.get("href") if link_tag else None
        if link:
            synopsis_link.append("https://mubi.com" + link)

        img_tag = li.find("img")
        image = img_tag.get("src") if img_tag else "No image available"
        title_tag = li.find("h3")
        title = title_tag.text if title_tag else "No title available"
        title = title.replace("'", "’")
        director_tag = li.find("span", class_="css-in3yi3 e1glieyg0")
        director = director_tag.text if director_tag else "No director available"
        director = director.replace("'", "’")
        country_tag = li.find("span", class_="css-ahepiu e18m0o271")
        if country_tag:
            country = country_tag.text
            country = country.replace("'", "’")
            year_tag = country_tag.find_next_sibling("span")
            year = year_tag.text if year_tag else "No year available"
        else:
            country = "Country information not specified"
            year_tag = director_tag.find_next_sibling("span")
            year = year_tag.text if year_tag else "No year available"


        # Store movie data in the dictionary using the movie title as key
        lesbianOrDyke_dic[title] = {
            "director": director,
            "year": year,
            "country": country,
            "image": image,
            "synopsis" : "https://mubi.com" + link
        }

    return lesbianOrDyke_dic, synopsis_link


# Handle the fetching, processing and storage of movie synopses
def process_synopsis(lesbianOrDyke_dic, synopsis_link):
    logger.info('Starting scraping synopsis')

    # Initialize a lock for dic data manipulation synchronization
    lock = threading.Lock()

    # Initialize a counter for failed requests
    failed_request = 0

    # Batch processing of synopsis fetching
    batch_size = 100
    total_movies = len(synopsis_link)
    
    # Loop through synopsis links in batches of batch_size
    for start_index in range(0, total_movies, batch_size):
        # Get a batch of synopsis links
        batch_links = synopsis_link[start_index:start_index + batch_size]

        # Fetch synopsis concurrently with up to 5 workers
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            # Submit tasks for fetching synopses asynchronously
            future_to_link = {executor.submit(scrape_synopsis, link): link for link in batch_links}
            # Iterate over completed futures as they become available
            for future in concurrent.futures.as_completed(future_to_link):
                # Retrieve the original link associated with the completed future
                link = future_to_link[future]

                try:
                    synopsis = future.result()
                    logger.info(f"Fetching synopsis: {synopsis} for link : {link}")

                    # Update the dictionary 
                    with lock:
                        for title, info in lesbianOrDyke_dic.items():
                            if info["synopsis"] == link:
                                if synopsis.startswith('https://mubi.com'):
                                    # If synopsis indicates a url, keep it that way for re-fetching process of failed requests later
                                    failed_request += 1
                                    pass
                                elif synopsis == 'No synopsis available':
                                    # If synopsis indicates no synopsis available, set info["synopsis"] accordingly
                                    info["synopsis"] = 'No synopsis available'
                                else:
                                    # Otherwise, update info["synopsis"] with the fetched synopsis
                                    info["synopsis"] = synopsis

                except Exception as exc:
                    logger.error(f"Error fetching synopsis: {exc}")
                    logger.error(f"Exception type: {type(exc)}")
                    traceback.print_exc()

        # Cool-down-time between batches to avoid error 429 or 405 from server
        if start_index + batch_size < total_movies:
            logger.info(f"Waiting for 10 minutes before fetching next batch...")
            time.sleep(600)

    return lesbianOrDyke_dic, failed_request


# Scrape synopsis from movie page 
def scrape_synopsis(url):
    
    try:
        response = requests.get(url)
        response.raise_for_status() 

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            div = soup.find('div', class_="css-dykg55 e17wgn1f17")
            synopsis = div.find("p").text if div else 'No synopsis available'
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed for URL {url}: {e}")
        if hasattr(e, 'response') and e.response is not None: # Log response headers if available
            logger.info(f"Response headers: {e.response.headers}")
        time.sleep(60) # Introduce a one minute delay after a failed request
        synopsis = url

    return synopsis