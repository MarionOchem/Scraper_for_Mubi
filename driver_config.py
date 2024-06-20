from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import logging 

# Set up logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Configure Chrome options for the webdriver 
def get_chrome_options():
    chrome_options = Options() # Creation of an instance of Chrome options
    chrome_options.add_argument("--headless")  # Hide GUI
    chrome_options.add_argument("--window-size=1920,1080")  # Set window size to native 
    chrome_options.add_argument("start-maximized")  # Ensure window is full-screen
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36") # Set a custom user agent string to avoid bot detection
    chrome_options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2}) # Disable loading of images to save bandwidth and speed up page loading

    return chrome_options

# Initialize webdriver with configured Chrome options
def get_webdriver():
    logger.info("Getting web driver configured")
    chrome_options = get_chrome_options()
    driver = webdriver.Chrome(options=chrome_options)

    return driver
