# A scraper for Mubi movies lists 

### This Python script leverages Selenium and BeautifulSoup for web scraping.
### It dynamically interacts with Mubi's website, clicking "Show More" buttons using Selenium's WebDriver and handling asynchronous requests with concurrent.futures for efficiency. 
### Threading and synchronization techniques ensure safe concurrent data processing. 
### Error handling, logging, and retry mechanisms are implemented for robustness, covering scenarios like failed requests and exceptions. 
### Data extraction entails parsing HTML, manipulating dictionaries, and formatting data into .sql and .csv files for seamless integration into various applications. 
### The script optimizes resource usage with headless browsing and custom Chrome options, for seamless execution without GUI interruptions or bot detection.
