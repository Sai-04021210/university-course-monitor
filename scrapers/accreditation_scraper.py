#!/usr/bin/env python3
"""
German Accreditation Council Scraper
Scrapes English-taught programmes from the German Accreditation Council database
"""

import logging
import time
import os
from typing import List, Dict
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
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
        options.add_argument('--disable-extensions')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36')
        
        # Set Chrome binary path for Alpine Linux
        if os.path.exists('/usr/bin/chromium-browser'):
            options.binary_location = '/usr/bin/chromium-browser'
        
        try:
            if os.path.exists('/usr/bin/chromedriver'):
                service = Service('/usr/bin/chromedriver')
                driver = webdriver.Chrome(service=service, options=options)
                return driver
            else:
                driver = webdriver.Chrome(options=options)
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
            # Setup WebDriver
            driver = self.setup_driver()

            # Navigate to search page
            logger.info("Navigating to Accreditation Council database")
            driver.get(self.search_url)

            # Wait for the JavaScript application to load
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            # Wait a bit more for the app to fully initialize
            time.sleep(5)

            # Set search filters for English programmes
            self._set_search_filters(driver)

            # Submit search
            self._submit_search(driver)

            # Scrape results from all pages
            programmes = self._scrape_all_results(driver)

            logger.info(f"Accreditation Council scraper completed. Found {len(programmes)} programmes")

        except Exception as e:
            logger.error(f"Error in Accreditation Council scraper: {e}")
        finally:
            # Always close the driver
            if driver:
                driver.quit()

        return programmes
    
    def _set_search_filters(self, driver):
        """Set search filters for English-taught programmes"""
        try:
            logger.info("Setting search filters for English programmes")

            # Wait for the search interface to load
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input, [data-testid*='search'], [placeholder*='Suche']"))
            )

            # Try different selectors for the search input
            search_selectors = [
                "input[placeholder*='Suche']",
                "input[placeholder*='Search']",
                "[data-testid*='search'] input",
                "input[type='text']",
                ".search-input",
                "#search"
            ]

            search_input = None
            for selector in search_selectors:
                try:
                    search_input = driver.find_element(By.CSS_SELECTOR, selector)
                    if search_input.is_displayed():
                        break
                except NoSuchElementException:
                    continue

            if search_input:
                logger.info("Found search input, entering 'English'")
                search_input.clear()
                search_input.send_keys("English")
                time.sleep(2)
            else:
                logger.warning("Could not find search input field")

            # Try to open advanced search/filters
            try:
                advanced_buttons = driver.find_elements(By.XPATH, "//*[contains(text(), 'Erweiterte') or contains(text(), 'Filter') or contains(text(), 'Advanced')]")
                for button in advanced_buttons:
                    if button.is_displayed() and button.is_enabled():
                        logger.info("Clicking advanced search/filter button")
                        button.click()
                        time.sleep(2)
                        break
            except Exception as e:
                logger.debug(f"Could not find advanced search button: {e}")

            time.sleep(3)  # Allow filters to be applied

        except Exception as e:
            logger.error(f"Error setting Accreditation Council search filters: {e}")
    
    def _submit_search(self, driver):
        """Submit the search form"""
        try:
            logger.info("Submitting search")

            # Try different selectors for search/submit buttons
            submit_selectors = [
                "button[type='submit']",
                "button:contains('Suchen')",
                "button:contains('Search')",
                "[data-testid*='search'] button",
                ".search-button",
                "input[type='submit']",
                "button.btn-primary",
                "*[role='button']:contains('Suchen')"
            ]

            search_button = None
            for selector in submit_selectors:
                try:
                    if ":contains(" in selector:
                        # Use XPath for text-based selectors
                        xpath_selector = f"//*[contains(text(), 'Suchen') or contains(text(), 'Search')]"
                        buttons = driver.find_elements(By.XPATH, xpath_selector)
                        for btn in buttons:
                            if btn.is_displayed() and btn.is_enabled():
                                search_button = btn
                                break
                    else:
                        search_button = driver.find_element(By.CSS_SELECTOR, selector)
                        if search_button.is_displayed() and search_button.is_enabled():
                            break
                except NoSuchElementException:
                    continue

                if search_button:
                    break

            if search_button:
                logger.info("Found search button, clicking")
                search_button.click()
            else:
                # Try pressing Enter on the search input
                logger.info("No search button found, trying Enter key")
                search_inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='text']")
                if search_inputs:
                    from selenium.webdriver.common.keys import Keys
                    search_inputs[0].send_keys(Keys.RETURN)

            # Wait for results to load - try different selectors
            logger.info("Waiting for search results to load")
            result_selectors = [
                ".search-results",
                "[data-testid*='result']",
                ".result-list",
                ".programme-list",
                "table tbody tr",
                ".data-table"
            ]

            results_loaded = False
            for selector in result_selectors:
                try:
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    logger.info(f"Results loaded with selector: {selector}")
                    results_loaded = True
                    break
                except TimeoutException:
                    continue

            if not results_loaded:
                logger.warning("Could not detect search results loading, continuing anyway")
                time.sleep(5)  # Wait a bit anyway

        except Exception as e:
            logger.error(f"Error submitting search: {e}")
            # Continue anyway, maybe results are already loaded
    
    def _scrape_all_results(self, driver) -> List[Dict]:
        """Scrape results from all pages"""
        programmes = []
        page = 1
        
        while True:
            logger.info(f"Scraping Accreditation Council results page {page}")
            
            # Scrape current page
            page_programmes = self._scrape_results_page(driver)
            programmes.extend(page_programmes)
            
            # Check if there's a next page
            if not self._go_to_next_page(driver):
                break
            
            page += 1
            
            # Safety check
            if page > 20:
                logger.warning("Reached maximum page limit for Accreditation Council")
                break
                
            time.sleep(2)
        
        return programmes
    
    def _scrape_results_page(self, driver) -> List[Dict]:
        """Scrape programmes from current results page"""
        programmes = []

        try:
            logger.info("Scraping current results page")

            # Try different selectors for result elements
            result_selectors = [
                "table tbody tr",  # Table rows
                ".result-item",
                ".programme-entry",
                "[data-testid*='result']",
                ".data-row",
                "tr[role='row']",
                ".list-item"
            ]

            result_elements = []
            for selector in result_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        logger.info(f"Found {len(elements)} elements with selector: {selector}")
                        result_elements = elements
                        break
                except Exception as e:
                    logger.debug(f"Selector {selector} failed: {e}")
                    continue

            if not result_elements:
                logger.warning("No result elements found")
                return programmes

            logger.info(f"Processing {len(result_elements)} result elements")

            for i, element in enumerate(result_elements):
                try:
                    programme = self._extract_programme_info(element)
                    if programme and self._is_english_programme(programme):
                        programmes.append(programme)
                        logger.debug(f"Extracted programme: {programme['program_name']}")
                except Exception as e:
                    logger.debug(f"Error extracting programme from element {i}: {e}")
                    continue

            logger.info(f"Successfully extracted {len(programmes)} English programmes from page")

        except Exception as e:
            logger.error(f"Error scraping Accreditation Council results page: {e}")

        return programmes
    
    def _extract_programme_info(self, element) -> Dict:
        """Extract programme information from result element"""
        try:
            # Get all text content from the element
            element_text = element.text.strip()

            if not element_text or len(element_text) < 10:
                return None

            # Try to extract programme name from different possible locations
            program_name = ""
            name_selectors = [
                "td:first-child",  # First column in table
                ".programme-name",
                ".studiengang",
                "a",  # Link text
                "strong",  # Bold text
                "h3, h4, h5"  # Headers
            ]

            for selector in name_selectors:
                try:
                    name_elem = element.find_element(By.CSS_SELECTOR, selector)
                    if name_elem and name_elem.text.strip():
                        program_name = name_elem.text.strip()
                        break
                except NoSuchElementException:
                    continue

            # If no specific element found, try to parse from full text
            if not program_name:
                lines = element_text.split('\n')
                for line in lines:
                    line = line.strip()
                    if len(line) > 10 and not any(skip in line.lower() for skip in ['hochschule', 'university', 'bachelor', 'master', 'datum']):
                        program_name = line
                        break

            if not program_name:
                return None

            # Extract institution name
            institution = "Unknown"
            institution_selectors = [
                "td:nth-child(2)",  # Second column
                ".institution",
                ".hochschule"
            ]

            for selector in institution_selectors:
                try:
                    inst_elem = element.find_element(By.CSS_SELECTOR, selector)
                    if inst_elem and inst_elem.text.strip():
                        institution = inst_elem.text.strip()
                        break
                except NoSuchElementException:
                    continue

            # If no specific element, try to find institution in text
            if institution == "Unknown":
                lines = element_text.split('\n')
                for line in lines:
                    line = line.strip()
                    if any(keyword in line.lower() for keyword in ['hochschule', 'universität', 'university', 'institut']):
                        institution = line
                        break

            # Extract degree type
            degree = self._extract_degree_from_name(program_name)

            # Try to find degree in separate column/element
            degree_selectors = [
                "td:nth-child(3)",  # Third column
                ".degree-type",
                ".abschluss"
            ]

            for selector in degree_selectors:
                try:
                    degree_elem = element.find_element(By.CSS_SELECTOR, selector)
                    if degree_elem and degree_elem.text.strip():
                        degree_text = degree_elem.text.strip()
                        if any(d in degree_text.lower() for d in ['bachelor', 'master', 'phd', 'diploma']):
                            degree = degree_text
                            break
                except NoSuchElementException:
                    continue

            # Extract accreditation date if available
            accreditation_date = None
            try:
                date_selectors = [
                    "td:last-child",  # Last column
                    ".accreditation-date",
                    ".datum"
                ]

                for selector in date_selectors:
                    try:
                        date_elem = element.find_element(By.CSS_SELECTOR, selector)
                        if date_elem and date_elem.text.strip():
                            date_text = date_elem.text.strip()
                            # Simple date validation
                            if any(char.isdigit() for char in date_text) and len(date_text) > 4:
                                accreditation_date = date_text
                                break
                    except NoSuchElementException:
                        continue
            except Exception:
                pass

            # Programme URL (if available)
            program_url = ""
            try:
                url_elem = element.find_element(By.TAG_NAME, "a")
                href = url_elem.get_attribute("href")
                if href and href.startswith('http'):
                    program_url = href
            except NoSuchElementException:
                pass

            programme = {
                'program_name': program_name,
                'institution': institution,
                'degree': degree,
                'language': 'English',
                'source_url': program_url,
                'tuition_fee': 0,  # Most German public universities are tuition-free
                'start_date': '',
                'tuition_period': 'semester',
                'accreditation_date': accreditation_date
            }

            return programme

        except Exception as e:
            logger.debug(f"Error extracting Accreditation Council programme info: {e}")
            return None
    
    def _is_english_programme(self, programme: Dict) -> bool:
        """Check if programme is likely English-taught"""
        program_name = programme.get('program_name', '').lower()
        institution = programme.get('institution', '').lower()
        
        # Keywords that indicate English-taught programmes
        english_keywords = [
            'english', 'international', 'global', 'european',
            'master of science', 'master of arts', 'bachelor of science',
            'bachelor of arts', 'msc', 'mba', 'phd'
        ]
        
        # German keywords that indicate German-taught programmes
        german_keywords = [
            'deutsch', 'germanistik', 'deutschsprachig'
        ]
        
        # Check for English keywords
        for keyword in english_keywords:
            if keyword in program_name:
                return True
        
        # Exclude programmes with German keywords
        for keyword in german_keywords:
            if keyword in program_name:
                return False
        
        # Additional heuristics: international institutions or English degree titles
        if any(word in institution for word in ['international', 'european']):
            return True
        
        return False
    
    def _extract_degree_from_name(self, program_name: str) -> str:
        """Extract degree type from programme name"""
        name_lower = program_name.lower()
        
        if 'master' in name_lower or 'm.sc' in name_lower or 'm.a' in name_lower:
            return 'M.Sc.'
        elif 'bachelor' in name_lower or 'b.sc' in name_lower or 'b.a' in name_lower:
            return 'B.Sc.'
        elif 'phd' in name_lower or 'doctorate' in name_lower:
            return 'Ph.D.'
        elif 'diploma' in name_lower:
            return 'Diploma'
        else:
            return 'Unknown'
    
    def _go_to_next_page(self, driver) -> bool:
        """Navigate to next page if available"""
        try:
            next_button = driver.find_element(By.XPATH, "//a[contains(@class, 'next') or contains(text(), 'Weiter')]")
            if next_button.is_enabled() and next_button.is_displayed():
                next_button.click()
                
                # Wait for new page to load
                WebDriverWait(driver, 10).until(
                    EC.staleness_of(driver.find_element(By.CLASS_NAME, "search-results"))
                )
                
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "search-results"))
                )
                
                return True
                
        except (NoSuchElementException, TimeoutException):
            pass
        
        return False

def main():
    """For testing the scraper independently"""
    logging.basicConfig(level=logging.INFO)
    scraper = AccreditationScraper()
    programmes = scraper.scrape_english_programmes()
    
    print(f"Found {len(programmes)} programmes")
    for programme in programmes[:5]:  # Show first 5
        print(f"- {programme['program_name']} at {programme['institution']}")

if __name__ == "__main__":
    main()