from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
import time
import random
from bs4 import BeautifulSoup
import requests
import concurrent.futures

import threading
import traceback

   
# Initialize a lock for synchronization
lock = threading.Lock()


import logging

# Set up logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# [1] Use Selenium to load the webpage and click the "Afficher la suite" button as needed

# configure webdriver
chrome_options = Options()
chrome_options.add_argument("--headless")  # hide GUI
chrome_options.add_argument("--window-size=1920,1080")  # set window size to native GUI size
chrome_options.add_argument("start-maximized")  # ensure window is full-screen
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
# configure chrome browser to not load images and javascript
# chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option(
    # this will disable image loading
    "prefs", {"profile.managed_default_content_settings.images": 2}
)

driver = webdriver.Chrome(options=chrome_options)

driver.get("https://mubi.com/fr/lists/dyke-cinema")



def click_show_more_button():
     logger.info('Starting clicking on "Show More"')
     while True:

        try:
            button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Afficher la suite']")))
            driver.execute_script("arguments[0].scrollIntoView();", button)  # Scroll to the button
            # button.click()
             # Click the button using JavaScript to bypass interception
            driver.execute_script("arguments[0].click();", button)
            time.sleep(5)  # Wait for content to load (adjust as needed)
        except Exception as e:
            print(f"Exception clicking button: {e}")
            break 

# [2] Parse the page source and extract target content with BeautifulSoup

def scrape_movies():
    logger.info('Starting retrieving movies from DOM')

    # Initialize a lock for synchronization
    lock = threading.Lock()

    page_source = driver.page_source
    soup = BeautifulSoup(page_source, "html.parser")

    li_elements = soup.find_all("li", class_="css-1t2q5wf e18pxekp0")

    print("number of li elements / movies : ", len(li_elements))

    lesbianOrDyke_dict = {}
    synopsis_link = []

#could add link as the value of synopsis temporarly in the lesbian object and then process the link in parallel and compare the fetched link with the link stored inside the object, if ti matches, replace it with actual synopsis
    for li in li_elements:
        link_tag = li.find("a")
        link = link_tag.get("href") if link_tag else None
        if link:
            synopsis_link.append("https://mubi.com" + link)

        img_tag = li.find("img")
        image = img_tag.get("src") if img_tag else "No image available"
        title_tag = li.find("h3")
        title = title_tag.text if title_tag else "No title available"
        director_tag = li.find("span", class_="css-in3yi3 e1tl7wq0")
        director = director_tag.text if director_tag else "No director available"
        country_tag = li.find("span", class_="css-ahepiu e1xnd4uf1")
        if country_tag:
            country = country_tag.text
            year_tag = country_tag.find_next_sibling("span")
            year = year_tag.text if year_tag else "No year available"
        else:
            country = "Country information not specified"
            year_tag = director_tag.find_next_sibling("span")
            year = year_tag.text if year_tag else "No year available"

    
        lesbianOrDyke_dict[title] = {
            "image": image,
            "director": director,
            "country": country,
            "year": year,
            "synopsis" : "https://mubi.com" + link
        }

    # Batch processing of synopsis fetching
    batch_size = 50  
    total_movies = len(synopsis_link)
    
    for start_index in range(0, total_movies, batch_size):
        batch_links = synopsis_link[start_index:start_index + batch_size]

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_link = {executor.submit(scrape_synopsis, link): link for link in batch_links}
            for future in concurrent.futures.as_completed(future_to_link):
                link = future_to_link[future]
                try:
                    synopsis = future.result()
                    logger.info(f"Fetching synopsis: {synopsis} for link : {link}")

                    # Update corresponding title in the dictionary
                    with lock:
                        for title, info in lesbianOrDyke_dict.items():
                            if info["synopsis"] == link:
                                info["synopsis"] = synopsis if synopsis != 'No synopsis available' else 'No synopsis available'
                                break
                except Exception as exc:
                    logger.error(f"Error fetching synopsis: {exc}")
                    logger.error(f"Exception type: {type(exc)}")
                    traceback.print_exc()

        # Introduce a delay between batches
        if start_index + batch_size < total_movies:
            logger.info(f"Waiting for 60 seconds before fetching next batch...")
            time.sleep(60)

    return lesbianOrDyke_dict



def scrape_synopsis(url):
    try:
        response = requests.get(url)
        response.raise_for_status() 

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            div = soup.find('div', class_="css-dykg55 e1fc1h0z17")
            synopsis = div.find("p").text if div else 'No synopsis available'
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed for URL {url}: {e}")
        time.sleep(5) # Introduce a 5 seconds delay after a failed request
        synopsis = 'No synopsis available' 
   

    return synopsis
   


try:
    logger.info('Scraping start')
    start_time = time.time()

    click_show_more_button()
    time.sleep(6)
    result = scrape_movies()
    print(result)
except Exception as e:
    logger.error(f'Exception during scraping : {e}')
finally:
    driver.quit()
    end_time = time.time()
    computation_time = end_time - start_time
    logger.info(f"Computation time: {computation_time:.2f} seconds")
