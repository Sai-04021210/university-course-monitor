#!/usr/bin/env python3
"""
German Accreditation Council Scraper
Scrapes English-taught programmes from the German Accreditation Council database
"""

import logging
import time
import os
from typing import List, Dict
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.service import Service

logger = logging.getLogger(__name__)

class AccreditationScraper:
    def __init__(self):
        self.base_url = "https://antrag.akkreditierungsrat.de"
        self.search_url = f"{self.base_url}/#/akkreditierungsdatenbank/studiengaenge"

    def setup_driver(self):
        """Setup Chrome WebDriver with headless options"""
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36')

        if os.path.exists('/usr/bin/chromium-browser'):
            options.binary_location = '/usr/bin/chromium-browser'

        try:
            if os.path.exists('/usr/bin/chromedriver'):
                service = Service('/usr/bin/chromedriver')
                driver = webdriver.Chrome(service=service, options=options)
                return driver
            else:
                from webdriver_manager.chrome import ChromeDriverManager
                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=options)
                return driver
        except Exception as e:
            logger.error(f"Failed to setup Chrome driver: {e}")
            raise

    def scrape_english_programmes(self) -> List[Dict]:
        """Scrape English-taught programmes from Accreditation Council database"""
        logger.info("Starting Accreditation Council scraper")
        programmes = []
        driver = None

        try:
            driver = self.setup_driver()
            driver.get(self.search_url)

            wait = WebDriverWait(driver, 20)

            # Click on "Erweiterte Filter anzeigen"
            try:
                advanced_filter_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Erweiterte Filter anzeigen')]")))
                logger.info("Found and clicking 'Erweiterte Filter anzeigen'.")
                advanced_filter_button.click()
                time.sleep(2)
            except TimeoutException:
                logger.warning("Could not find 'Erweiterte Filter anzeigen' button.")

            studiengang_input = wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@placeholder='Studiengang']")))
            logger.info("Found 'Studiengang' input field.")

            studiengang_input.clear()
            studiengang_input.send_keys("English")
            time.sleep(1)

            search_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Treffer anzeigen')]")))
            logger.info("Found and clicking the search button.")
            search_button.click()
            time.sleep(5)

            programmes = self._scrape_all_results(driver)

            logger.info(f"Accreditation Council scraper completed. Found {len(programmes)} programmes.")

        except TimeoutException as e:
            logger.error(f"A critical element was not found on the page. Saving screenshot to accreditation_scraper_error.png")
            driver.save_screenshot("accreditation_scraper_error.png")
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            driver.save_screenshot("accreditation_scraper_error.png")
        finally:
            if driver:
                driver.quit()

        return programmes

    def _scrape_all_results(self, driver) -> List[Dict]:
        """Scrape results from all pages"""
        programmes = []
        page = 1
        while True:
            logger.info(f"Scraping Accreditation Council results page {page}")
            
            try:
                wait = WebDriverWait(driver, 15)
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table.table-result > tbody > tr")))
                
                page_programmes = self._scrape_results_page(driver)
                programmes.extend(page_programmes)
                
                if not self._go_to_next_page(driver):
                    logger.info("No more pages to scrape.")
                    break
                
                page += 1
                if page > 50:
                    logger.warning("Reached page limit of 50.")
                    break
                time.sleep(2)

            except TimeoutException:
                logger.info("No more results found on the page.")
                break
            except Exception as e:
                logger.error(f"Error scraping page {page}: {e}")
                break
        
        return programmes

    def _scrape_results_page(self, driver) -> List[Dict]:
        """Scrape programmes from the current results page"""
        programmes = []
        try:
            result_rows = driver.find_elements(By.CSS_SELECTOR, "table.table-result > tbody > tr")
            logger.info(f"Found {len(result_rows)} result rows on the current page.")

            for row in result_rows:
                try:
                    programme = self._extract_programme_info(row)
                    if programme:
                        programmes.append(programme)
                except Exception as e:
                    logger.debug(f"Could not extract programme from a row: {e}")
        except Exception as e:
            logger.error(f"Error scraping results page: {e}")
        return programmes

    def _extract_programme_info(self, row) -> Dict:
        """Extract programme information from a table row"""
        try:
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) < 4:
                return None

            program_name = cells[0].text.strip()
            institution = cells[1].text.strip()
            degree = cells[2].text.strip()
            accreditation_date = cells[3].text.strip()

            if not program_name or not institution:
                return None

            return {
                'program_name': program_name,
                'institution': institution,
                'degree': degree,
                'language': 'English',
                'source_url': self.search_url,
                'accreditation_date': accreditation_date,
            }
        except Exception as e:
            logger.debug(f"Error extracting info from row:. {e}")
            return None

    def _go_to_next_page(self, driver) -> bool:
        """Navigate to the next page if available"""
        try:
            next_button = driver.find_element(By.CSS_SELECTOR, "a.page-link[aria-label='Next page']")
            if "disabled" in next_button.get_attribute("class"):
                return False
            
            driver.execute_script("arguments[0].click();", next_button)
            return True
        except NoSuchElementException:
            return False
        except Exception as e:
            logger.error(f"Error navigating to next page: {e}")
            return False

def main():
    """For testing the scraper independently"""
    logging.basicConfig(level=logging.INFO)
    scraper = AccreditationScraper()
    programmes = scraper.scrape_english_programmes()
    
    print(f"Found {len(programmes)} programmes")
    if programmes:
        print("First 5 programmes:")
        for programme in programmes[:5]:
            print(f"- {programme}")

if __name__ == "__main__":
    main()