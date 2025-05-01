# scraper.py
from selenium import webdriver # type: ignore
from selenium.webdriver.chrome.service import Service # type: ignore
from webdriver_manager.chrome import ChromeDriverManager # type: ignore
from bs4 import BeautifulSoup # type: ignore
import sqlite3
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_db_connection():
    conn = sqlite3.connect('cafes.db')
    conn.row_factory = sqlite3.Row
    return conn

def scrape_laptopfriendly():
    """
    Scrape cafe data from LaptopFriendly.co/london and insert into cafes.db.
    Returns the number of cafes added.
    """
    url = "https://laptopfriendly.co/london"
    scraped_cafes = []

    try:
        # Set up Selenium with ChromeDriver
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # Run in headless mode (no browser UI)
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

        logging.info(f"Navigating to {url}")
        driver.get(url)

        # Wait for dynamic content to load
        time.sleep(5)  # Adjust based on page load time

        # Get page source and parse with Beautiful Soup
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Find cafe listings (based on observed HTML structure)
        # Note: This is a simplified example; actual selectors depend on the site's structure
        cafe_elements = soup.select('div.place-card')  # Adjust selector based on actual HTML

        for cafe in cafe_elements:
            try:
                # Extract data (adjust selectors based on actual HTML)
                name = cafe.select_one('h2.place-title').text.strip() if cafe.select_one('h2.place-title') else 'Unknown'
                address = cafe.select_one('p.address').text.strip() if cafe.select_one('p.address') else 'Unknown'
                
                # WiFi speed (assume text like "Fast WiFi" or fallback)
                wifi_info = cafe.select_one('span.wifi-info').text.strip() if cafe.select_one('span.wifi-info') else 'Moderate'
                wifi_speed = 'Fast' if 'fast' in wifi_info.lower() else 'Moderate' if 'moderate' in wifi_info.lower() else 'Slow'
                
                # Power outlets (assume text like "Many outlets" or fallback)
                power_info = cafe.select_one('span.power-info').text.strip() if cafe.select_one('span.power-info') else 'Few'
                power_outlets = 'Many' if 'many' in power_info.lower() else 'Few' if 'few' in power_info.lower() else 'None'
                
                # Rating (assume a number or fallback)
                rating_elem = cafe.select_one('span.rating')
                rating = float(rating_elem.text.strip()) if rating_elem and rating_elem.text.strip().replace('.', '').isdigit() else 4.0

                scraped_cafes.append({
                    'name': name,
                    'address': address,
                    'wifi_speed': wifi_speed,
                    'power_outlets': power_outlets,
                    'rating': rating
                })
            except Exception as e:
                logging.warning(f"Error parsing cafe: {e}")
                continue

        driver.quit()

        # Insert scraped data into database
        conn = get_db_connection()
        c = conn.cursor()
        inserted_count = 0

        for cafe in scraped_cafes:
            try:
                # Check if cafe already exists to avoid duplicates
                c.execute('SELECT id FROM cafes WHERE name = ? AND address = ?', (cafe['name'], cafe['address']))
                if c.fetchone() is None:
                    c.execute('INSERT INTO cafes (name, address, wifi_speed, power_outlets, rating) VALUES (?, ?, ?, ?, ?)',
                              (cafe['name'], cafe['address'], cafe['wifi_speed'], cafe['power_outlets'], cafe['rating']))
                    inserted_count += 1
            except Exception as e:
                logging.warning(f"Error inserting cafe {cafe['name']}: {e}")
                continue

        conn.commit()
        conn.close()

        logging.info(f"Scraped and inserted {inserted_count} cafes")
        return inserted_count

    except Exception as e:
        logging.error(f"Scraping failed: {e}")
        return 0

# Mock scraping function for testing (if LaptopFriendly.co restricts scraping)
def scrape_mock_data():
    """
    Simulate scraping by providing mock cafe data.
    Returns the number of cafes added.
    """
    mock_cafes = [
        {'name': 'The Coffee House', 'address': '123 Oxford St, London', 'wifi_speed': 'Fast', 'power_outlets': 'Many', 'rating': 4.5},
        {'name': 'Brew & Work', 'address': '456 Camden Rd, London', 'wifi_speed': 'Moderate', 'power_outlets': 'Few', 'rating': 4.0},
        {'name': 'Laptop Haven', 'address': '789 Shoreditch, London', 'wifi_speed': 'Fast', 'power_outlets': 'Many', 'rating': 4.8}
    ]

    conn = get_db_connection()
    c = conn.cursor()
    inserted_count = 0

    for cafe in mock_cafes:
        try:
            c.execute('SELECT id FROM cafes WHERE name = ? AND address = ?', (cafe['name'], cafe['address']))
            if c.fetchone() is None:
                c.execute('INSERT INTO cafes (name, address, wifi_speed, power_outlets, rating) VALUES (?, ?, ?, ?, ?)',
                          (cafe['name'], cafe['address'], cafe['wifi_speed'], cafe['power_outlets'], cafe['rating']))
                inserted_count += 1
        except Exception as e:
            logging.warning(f"Error inserting mock cafe {cafe['name']}: {e}")
            continue

    conn.commit()
    conn.close()

    logging.info(f"Inserted {inserted_count} mock cafes")
    return inserted_count

if __name__ == '__main__':
    # Run mock scraping for testing
    scrape_mock_data()
