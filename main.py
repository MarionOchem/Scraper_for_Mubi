import time
import logging
import traceback

# Import function from modules
from driver_config import get_webdriver
from scrape import click_show_more_button, scrape_movies, process_synopsis, scrape_synopsis
from data_processing import export_data

# Set up logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# URL to scrap
mubi_url = "https://mubi.com/fr/lists/dyke-cinema"

def main():
    start_time = time.time()
    logger.info("-- Main function start --")

    # Initialize web driver 
    driver = get_webdriver()
    
    try:

        click_show_more_button(driver, mubi_url)
        time.sleep(10) # pause to ensure all content loads 
        lesbianOrDyke_dic, synopsis_link = scrape_movies(driver) 
        lesbianOrDyke_dic, failed_request = process_synopsis(lesbianOrDyke_dic, synopsis_link)

        # Handle potential failed request during scraping
        if failed_request > 0:
            logger.info("Re-fetching failed requests")
            time.sleep(600) # cool-down-time to avoid error 429 or 405 from server
            for title, info in lesbianOrDyke_dic.items():
                if info["synopsis"] == info["synopsis"].startswith('https://mubi.com'):
                    url = info["synopsis"] 
                    retry_synopsis = scrape_synopsis(url)
                    logger.info(f"Re-fetching synopsis: {retry_synopsis} for link : {url}")
                    lesbianOrDyke_dic[title]["synopsis"] = retry_synopsis

        export_data(lesbianOrDyke_dic, 'Lesbian_Or_Dyke.csv', 'Lesbian_Or_Dyke.sql', 'LesbianOrDyke')

    except Exception as e:
        logger.error(f'Exception in main function : {e}')
        logger.error(f"Exception type : {type(e)}")
        traceback.print_exc()

    finally:
        driver.quit()
        end_time = time.time()
        computation_time = end_time - start_time
        logger.info(f"Computation time: {computation_time:.2f} seconds")
        logger.info('-- Main function end --')




if __name__ == "__main__":
    main()