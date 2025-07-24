#!/usr/bin/env python3
"""
HRK Hochschulkompass Scraper
Scrapes English-taught programmes from German Higher Education Compass
"""

import time
import logging
from typing import List, Dict
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
import requests

logger = logging.getLogger(__name__)

class HRKScraper:
    def __init__(self):
        self.base_url = "https://www.hochschulkompass.de"
        self.search_url = f"{self.base_url}/studium/studiengangsuche/erweiterte-studiengangsuche.html"
        
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
        options.add_argument('--disable-web-security')
        options.add_argument('--allow-running-insecure-content')
        options.add_argument('--disable-features=VizDisplayCompositor')

        # Set Chrome binary path for Alpine Linux
        import os
        if os.path.exists('/usr/bin/chromium-browser'):
            options.binary_location = '/usr/bin/chromium-browser'
        elif os.path.exists('/usr/bin/chromium'):
            options.binary_location = '/usr/bin/chromium'

        try:
            from selenium.webdriver.chrome.service import Service

            # Try to use the system chromedriver first
            if os.path.exists('/usr/bin/chromedriver'):
                service = Service('/usr/bin/chromedriver')
                driver = webdriver.Chrome(service=service, options=options)
                logger.info("Using system chromedriver at /usr/bin/chromedriver")
                return driver
            elif os.path.exists('/usr/lib/chromium/chromedriver'):
                service = Service('/usr/lib/chromium/chromedriver')
                driver = webdriver.Chrome(service=service, options=options)
                logger.info("Using system chromedriver at /usr/lib/chromium/chromedriver")
                return driver
            else:
                # Fallback to webdriver-manager
                try:
                    from webdriver_manager.chrome import ChromeDriverManager
                    service = Service(ChromeDriverManager().install())
                    driver = webdriver.Chrome(service=service, options=options)
                    logger.info("Using webdriver-manager to install chromedriver")
                    return driver
                except Exception as wm_error:
                    logger.error(f"WebDriver manager failed: {wm_error}")
                    # Last resort: try without service
                    driver = webdriver.Chrome(options=options)
                    logger.info("Using Chrome without explicit service")
                    return driver
        except Exception as e:
            logger.error(f"Failed to setup Chrome driver: {e}")
            raise
    
    def scrape_english_programmes(self) -> List[Dict]:
        """Scrape English-taught programmes from HRK"""
        logger.info("Starting HRK scraper")

        programmes = []
        driver = None

        try:
            # Setup WebDriver
            driver = self.setup_driver()
            
            # Navigate to search page
            logger.info("Navigating to HRK search page")
            driver.get(self.search_url)
            
            # Wait for page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "form"))
            )
            
            # Set search filters
            self._set_search_filters(driver)
            
            # Submit search
            self._submit_search(driver)
            
            # Scrape results from all pages
            programmes = self._scrape_all_results(driver)
            
            logger.info(f"HRK scraper completed. Found {len(programmes)} programmes")
            
        except Exception as e:
            logger.error(f"Error in HRK scraper: {e}")
        finally:
            # Always close the driver
            if driver:
                driver.quit()

        return programmes
    
    def _set_search_filters(self, driver):
        """Set search filters for English-taught programmes at public universities"""
        logger.info("Setting HRK search filters")
        
        try:
            # Select English as language
            language_select = Select(driver.find_element(By.NAME, "tx_szhrksearch_pi1[sprache]"))
            language_select.select_by_value("2")  # 2 = Englisch
            
            # Select university type (if available)
            try:
                traegerschaft_select = Select(driver.find_element(By.NAME, "tx_szhrksearch_pi1[traegerschaft]"))
                # Try to select public universities if the option exists
                options = [opt.get_attribute("value") for opt in traegerschaft_select.options]
                logger.debug(f"Traegerschaft options: {options}")
            except Exception as e:
                logger.debug(f"Could not find traegerschaft selector: {e}")
            
            # Look for submit button or search button
            logger.debug("Looking for submit button...")
            
            time.sleep(2)  # Allow filters to be applied
            
        except Exception as e:
            logger.error(f"Error setting search filters: {e}")
    
    def _submit_search(self, driver):
        """Submit the search form"""
        try:
            # Look for submit button with various methods
            submit_buttons = driver.find_elements(By.XPATH, "//input[@type='submit']")
            submit_buttons.extend(driver.find_elements(By.XPATH, "//button[@type='submit']"))
            submit_buttons.extend(driver.find_elements(By.XPATH, "//button[contains(text(), 'Suchen')]"))
            submit_buttons.extend(driver.find_elements(By.XPATH, "//input[contains(@value, 'Treffer')]"))
            
            if not submit_buttons:
                logger.error("No submit button found")
                return
                
            submit_button = submit_buttons[0]
            logger.info(f"Clicking submit button: {submit_button.get_attribute('value')}")
            
            # Use JavaScript to avoid click interception
            driver.execute_script("arguments[0].click();", submit_button)
            
            # Wait longer for AJAX results to load
            logger.info("Waiting for AJAX search results...")
            time.sleep(10)
            
        except Exception as e:
            logger.error(f"Error submitting search: {e}")
            raise
    
    def _scrape_all_results(self, driver) -> List[Dict]:
        """Scrape results from all pages with pagination"""
        programmes = []
        page = 1
        max_pages = 10  # Quick test: 10 pages = ~1,000 programmes

        
        try:
            # First, try to increase results per page to 100 for efficiency
            self._set_results_per_page(driver, 100)
            
            while page <= max_pages:
                logger.info(f"Scraping HRK results page {page}")
                
                # Scrape current page
                page_programmes = self._scrape_results_page(driver)
                if not page_programmes:
                    logger.info("No programmes found on this page, stopping")
                    break
                    
                programmes.extend(page_programmes)
                logger.info(f"Page {page}: Found {len(page_programmes)} programmes (Total: {len(programmes)})")
                
                # Check if there's a next page and navigate to it
                if not self._go_to_next_page(driver):
                    logger.info("No more pages available")
                    break
                
                page += 1
                
                # Progress update every 10 pages
                if page % 10 == 0:
                    logger.info(f"Progress: Scraped {page} pages, {len(programmes)} programmes total")
                
                # Be respectful to the server
                time.sleep(1)
                
        except Exception as e:
            logger.error(f"Error during pagination: {e}")
        
        logger.info(f"HRK pagination completed: {len(programmes)} programmes from {page-1} pages")
        return programmes
    
    def _scrape_results_page(self, driver) -> List[Dict]:
        """Scrape programmes from current results page"""
        programmes = []
        
        try:
            # Look for result elements with updated selectors
            result_elements = []
            selectors_to_try = [
                'div[class*="result"]',
                '.result-item', 
                '.search-result', 
                'table tr',
                'tbody tr'
            ]
            
            for selector in selectors_to_try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    logger.info(f"Found {len(elements)} elements with selector: {selector}")
                    # Filter out header/sorting elements
                    filtered_elements = []
                    for elem in elements:
                        text = elem.text.strip().lower()
                        if text and len(text) > 50 and "hochschule" in text:
                            filtered_elements.append(elem)
                    
                    if filtered_elements:
                        result_elements = filtered_elements
                        logger.info(f"After filtering: {len(result_elements)} programme elements")
                        break
            
            if not result_elements:
                logger.warning("No programme result elements found")
                return programmes
            
            for element in result_elements:
                try:
                    element_programmes = self._extract_programme_info(element)
                    programmes.extend(element_programmes)
                except Exception as e:
                    logger.error(f"Error extracting programme info: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"Error scraping results page: {e}")
        
        return programmes
    
    def _extract_programme_info(self, element) -> List[Dict]:
        """Extract multiple programme information from result element"""
        programmes = []
        
        try:
            # Get the full text and parse it
            full_text = element.text.strip()
            lines = [line.strip() for line in full_text.split('\n') if line.strip()]
            
            if len(lines) < 3:
                logger.debug(f"Not enough lines in result: {lines}")
                return programmes
            
            # Skip if this is a UI element (like sorting controls)
            if "treffer" in full_text.lower() or "ansicht" in full_text.lower():
                return programmes
                
            # Parse multiple programmes from the combined result
            # Each programme follows pattern: Name -> Hochschule -> Institution -> Studienort -> Location -> Abschluss -> Degree
            i = 0
            while i < len(lines):
                # Look for the start of a new programme (programme name followed by "Hochschule" label)
                if i + 2 < len(lines) and lines[i + 1] == "Hochschule":
                    try:
                        program_name = lines[i]
                        institution = lines[i + 2] if i + 2 < len(lines) else "Unknown"
                        
                        # Look ahead for degree info
                        degree = "Unknown"
                        j = i + 3
                        while j < len(lines) and j < i + 15:  # Look within next 15 lines
                            if lines[j] == "Abschluss" and j + 1 < len(lines):
                                degree_text = lines[j + 1]
                                if "master" in degree_text.lower():
                                    degree = "M.Sc."
                                elif "bachelor" in degree_text.lower():
                                    degree = "B.Sc."
                                elif "phd" in degree_text.lower() or "promotion" in degree_text.lower():
                                    degree = "Ph.D."
                                else:
                                    degree = degree_text
                                break
                            j += 1
                        
                        # Skip if programme name is too short or looks like UI element
                        if len(program_name) > 3 and not any(ui_word in program_name.lower() for ui_word in ["treffer", "ansicht", "mehr erfahren"]):
                            programme = {
                                'program_name': program_name,
                                'institution': institution,
                                'degree': degree,
                                'language': 'English',
                                'source_url': "",  # Will extract later if needed
                                'tuition_fee': 0,
                                'start_date': '',
                                'tuition_period': 'semester'
                            }
                            programmes.append(programme)
                            logger.debug(f"Extracted programme: {program_name} at {institution}")
                        
                        # Move to next potential programme (skip ahead)
                        i += 8  # Typical programme entry has ~8 lines
                    except Exception as e:
                        logger.debug(f"Error parsing programme at line {i}: {e}")
                        i += 1
                else:
                    i += 1
            
            logger.info(f"Extracted {len(programmes)} programmes from result element")
            return programmes
            
        except Exception as e:
            logger.error(f"Error extracting programme info: {e}")
            return programmes
    
    def _get_programme_details(self, program_url: str) -> Dict:
        """Get additional programme details from detail page"""
        details = {}
        
        try:
            # Use requests for faster detail page fetching
            response = requests.get(program_url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for tuition fee information
            tuition_section = soup.find('section', {'id': 'kosten'})
            if tuition_section:
                tuition_text = tuition_section.get_text().lower()
                if 'kostenfrei' in tuition_text or 'keine studiengebühren' in tuition_text:
                    details['tuition_fee'] = 0
                else:
                    # Try to extract numeric tuition value
                    import re
                    tuition_match = re.search(r'(\d+(?:\.\d+)?)\s*€', tuition_text)
                    if tuition_match:
                        details['tuition_fee'] = float(tuition_match.group(1))
            
            # Look for start date information
            start_section = soup.find('section', {'id': 'studienbeginn'})
            if start_section:
                start_text = start_section.get_text().strip()
                details['start_date'] = start_text
            
        except Exception as e:
            logger.debug(f"Could not fetch details for {program_url}: {e}")
        
        return details
    
    def _set_results_per_page(self, driver, count: int):
        """Set results per page to increase efficiency"""
        try:
            logger.info(f"Attempting to set {count} results per page")
            
            # Look for the results per page selector
            results_per_page_select = driver.find_element(By.CSS_SELECTOR, '.hrk-perpage select')
            options = results_per_page_select.find_elements(By.TAG_NAME, 'option')
            
            # Find option with the desired count
            for option in options:
                if str(count) in option.text:
                    url = option.get_attribute('value')
                    if url:
                        logger.info(f"Navigating to {count} results per page")
                        driver.get('https://www.hochschulkompass.de' + url)
                        time.sleep(5)  # Wait for page to load
                        return True
            
            logger.info(f"Could not find {count} results per page option, using default")
            return False
            
        except Exception as e:
            logger.debug(f"Could not set results per page: {e}")
            return False
    
    def _go_to_next_page(self, driver) -> bool:
        """Navigate to next page if available"""
        try:
            # Save current page HTML for debugging
            current_url = driver.current_url
            logger.info(f"Current page URL: {current_url}")
            
            # Try multiple selectors for pagination
            pagination_selectors = [
                '.pagination .next',
                '.pagination a[title*="nächste"]',
                '.pagination a[title*="weiter"]', 
                'a[href*="page="]',
                '.pager .next',
                '.hrk-pagination .next',
                'a:contains(">")',
                'a[aria-label*="next"]',
                'a[aria-label*="nächste"]'
            ]
            
            next_button = None
            for selector in pagination_selectors:
                try:
                    buttons = driver.find_elements(By.CSS_SELECTOR, selector)
                    if buttons:
                        logger.info(f"Found {len(buttons)} buttons with selector: {selector}")
                        for btn in buttons:
                            href = btn.get_attribute('href')
                            text = btn.text.strip()
                            logger.info(f"Button text: '{text}', href: {href}")
                            if href and 'disabled' not in btn.get_attribute('class'):
                                next_button = btn
                                break
                        if next_button:
                            break
                except Exception as e:
                    logger.debug(f"Selector {selector} failed: {e}")
            
            if not next_button:
                # Try JavaScript-based pagination
                try:
                    logger.info("Trying JavaScript-based pagination")
                    # Look for pagination info
                    page_info = driver.find_elements(By.CSS_SELECTOR, '.pagination, .pager, [class*="page"]')
                    for elem in page_info:
                        logger.info(f"Pagination element: {elem.get_attribute('outerHTML')[:200]}")
                    
                    # Try to find any link that might be next page
                    all_links = driver.find_elements(By.TAG_NAME, 'a')
                    for link in all_links:
                        href = link.get_attribute('href')
                        text = link.text.strip().lower()
                        if href and ('page=' in href or 'weiter' in text or 'next' in text or '>' in text):
                            logger.info(f"Potential next link: {text} -> {href}")
                    
                    return False
                    
                except Exception as e:
                    logger.error(f"JavaScript pagination failed: {e}")
                    return False
            
            # Navigate to next page
            href = next_button.get_attribute('href')
            logger.info(f"Navigating to next page: {href}")
            driver.get(href)
            
            # Wait for new page to load
            time.sleep(5)
            
            # Verify we're on a new page
            new_url = driver.current_url
            if new_url == current_url:
                logger.warning("URL didn't change after navigation")
                return False
                
            # Check for results on new page
            try:
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'div[class*="result"]'))
                )
                logger.info(f"Successfully navigated to new page: {new_url}")
                return True
            except TimeoutException:
                logger.warning("No results found on new page")
                return False
                
        except Exception as e:
            logger.error(f"Error in pagination: {e}")
            return False

def main():
    """For testing the scraper independently"""
    scraper = HRKScraper()
    programmes = scraper.scrape_english_programmes()
    
    print(f"Found {len(programmes)} programmes")
    for programme in programmes[:5]:  # Show first 5
        print(f"- {programme['program_name']} at {programme['institution']}")

if __name__ == "__main__":
    main()