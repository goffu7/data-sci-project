from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import time

load_dotenv()

# Set Chrome options
options = Options()
options.add_argument("--headless")  # Run in headless mode (no GUI)
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Set the ChromeDriver path
service = Service("/usr/bin/chromedriver")

# Initialize the WebDriver
driver = webdriver.Chrome(service=service, options=options)

mongo_uri = os.getenv("MONGO_URI")
scrape_limit = int(os.getenv("SCRAPE_LIMIT", 1000))

# Setup MongoDB client
mongo_client = MongoClient(mongo_uri)  # Update with your MongoDB connection string
db = mongo_client["arxiv_papers"]  # Database name
collection = db["papers"]  # Collection name

# Starting date for the loop
month = 1
year = 24

# Starting paper ID
paper_id = 1

# Counter for "not found" pages
not_found_count = 0

# Counter for scraped papers
scraped_count = 0

# Wait for elements to load
wait = WebDriverWait(driver, 10)

while scraped_count < scrape_limit:
    # Format of paper ID (YYMM.XXXXXv1)
    yymm = f"{year:02}{month:02}"
    url = f"https://arxiv.org/html/{yymm}.{paper_id:05}v1"
    print(f"Processing {yymm}.{paper_id:05}")

    try:
        # Navigate to the page
        driver.get(url)

        # Check for "not found" page
        if "Article not found" in driver.page_source:
            not_found_count += 1
            if not_found_count == 2:
                break
            paper_id += 1
            continue

        not_found_count = 0  # Reset if valid page is found

        # Extract title
        try:
            title_element = wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "ltx_title.ltx_title_document"))
            )
            title_text = title_element.text.strip()
        except:
            title_text = ""

        # Extract abstract
        try:
            abstract_element = wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "ltx_abstract"))
            )
            abstract_text = abstract_element.text.replace("Abstract\n", "").strip()
        except:
            abstract_text = ""

        # Extract keywords
        try:
            keyword_element = driver.find_element(By.CLASS_NAME, "ltx_keywords")
            keyword_text = keyword_element.text.replace("Keywords: ", "").strip()
            keywords_array = keyword_text.split(", ")
        except:
            keywords_array = []

        # Extract authors and countries
        try:
            contact_elements = driver.find_elements(By.CLASS_NAME, "ltx_contact.ltx_role_affiliation")
            author_elements = driver.find_elements(By.CLASS_NAME, "ltx_personname")
            authors = [element.text.strip() for element in author_elements]
            affiliations = [element.text.strip() for element in contact_elements]
            countries = [element.text.strip().split()[-1] for element in contact_elements]
        except:
            countries = []
            affiliations = []
            authors = []

        # Insert into mongodb if affiliations are non-empty
        if affiliations:
            paper_data = {
                'paper_id': f"{yymm}.{paper_id:05}",
                'url': url,
                'title': title_text,
                'abstract': abstract_text,
                'keyword': keywords_array,
                'authors': authors,
                'affiliations': affiliations,
                'country': countries
            }
            collection.insert_one(paper_data)  # Upload to MongoDB
            scraped_count += 1
            print(f"Uploaded {scraped_count}: {paper_data}")

        # Increment paper ID
        paper_id += 1

        # Stop if 1000 entries are collected
        if len(data) >= 1000:
            break

    except Exception as e:
        print(f"Error with {yymm}.{paper_id:05}: {e}")
        paper_id += 1
        continue

    # Handle month/year rollover
    if not_found_count == 2:
        month += 1
        not_found_count = 0
        if month > 12:
            month = 1
            year += 1

    # Print amount of papers scraped
    print(f"Scraped {scraped_count} papers.")

    # Delay to prevent overload
    time.sleep(1)

# Close the browser
driver.quit()
mongo_client.close()

print(f"Scraping complete. Uploaded {scraped_count} entries to mongoDB.")