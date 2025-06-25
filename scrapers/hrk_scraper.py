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
        self.search_url = f"{self.base_url}/studium/studiengangsuche/erweiterte-suche"
        
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
        
        return webdriver.Chrome(options=options)
    
    def scrape_english_programmes(self) -> List[Dict]:
        """Scrape English-taught programmes from HRK"""
        logger.info("Starting HRK scraper")

        programmes = []

        try:
            # For now, return a placeholder to avoid breaking the ETL pipeline
            # TODO: Implement proper HRK scraping with working selectors
            logger.info("HRK scraper temporarily disabled - needs selector updates")
            logger.info("Returning empty list to avoid ETL pipeline errors")

            # Placeholder data structure for testing
            programmes = []
            
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

        return programmes
    
    def _set_search_filters(self, driver):
        """Set search filters for English-taught programmes at public universities"""
        logger.info("Setting HRK search filters")
        
        try:
            # Select English as language
            language_select = Select(driver.find_element(By.NAME, "unterrichtssprache"))
            language_select.select_by_visible_text("Englisch")
            
            # Select public universities (Universitäten)
            university_type = driver.find_element(By.XPATH, "//input[@value='Universität']")
            if not university_type.is_selected():
                university_type.click()
            
            # Ensure we get all degree levels
            degree_levels = ["Bachelor", "Master", "Staatsexamen", "Diplom", "Promotion"]
            for level in degree_levels:
                try:
                    checkbox = driver.find_element(By.XPATH, f"//input[@value='{level}']")
                    if not checkbox.is_selected():
                        checkbox.click()
                except NoSuchElementException:
                    logger.debug(f"Degree level {level} not found")
            
            time.sleep(2)  # Allow filters to be applied
            
        except Exception as e:
            logger.error(f"Error setting search filters: {e}")
    
    def _submit_search(self, driver):
        """Submit the search form"""
        try:
            search_button = driver.find_element(By.XPATH, "//button[@type='submit']")
            search_button.click()
            
            # Wait for results to load
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CLASS_NAME, "search-results"))
            )
            
        except TimeoutException:
            logger.error("Search results did not load in time")
            raise
    
    def _scrape_all_results(self, driver) -> List[Dict]:
        """Scrape results from all pages"""
        programmes = []
        page = 1
        
        while True:
            logger.info(f"Scraping HRK results page {page}")
            
            # Scrape current page
            page_programmes = self._scrape_results_page(driver)
            programmes.extend(page_programmes)
            
            # Check if there's a next page
            if not self._go_to_next_page(driver):
                break
            
            page += 1
            
            # Safety check to avoid infinite loops
            if page > 50:
                logger.warning("Reached maximum page limit")
                break
                
            time.sleep(2)  # Be respectful to the server
        
        return programmes
    
    def _scrape_results_page(self, driver) -> List[Dict]:
        """Scrape programmes from current results page"""
        programmes = []
        
        try:
            # Get all programme result elements
            result_elements = driver.find_elements(By.CLASS_NAME, "search-result-item")
            
            for element in result_elements:
                try:
                    programme = self._extract_programme_info(element)
                    if programme:
                        programmes.append(programme)
                except Exception as e:
                    logger.error(f"Error extracting programme info: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"Error scraping results page: {e}")
        
        return programmes
    
    def _extract_programme_info(self, element) -> Dict:
        """Extract programme information from result element"""
        try:
            # Programme name
            name_elem = element.find_element(By.CLASS_NAME, "studiengang-title")
            program_name = name_elem.text.strip()
            
            # Programme URL
            program_url = name_elem.find_element(By.TAG_NAME, "a").get_attribute("href")
            
            # Institution name
            institution_elem = element.find_element(By.CLASS_NAME, "hochschule-name")
            institution = institution_elem.text.strip()
            
            # Degree type
            degree_elem = element.find_element(By.CLASS_NAME, "abschluss")
            degree = degree_elem.text.strip()
            
            # Additional details might be in a details section
            details = self._get_programme_details(program_url)
            
            programme = {
                'program_name': program_name,
                'institution': institution,
                'degree': degree,
                'language': 'English',
                'source_url': program_url,
                'tuition_fee': details.get('tuition_fee', 0),
                'start_date': details.get('start_date', ''),
                'tuition_period': 'semester'
            }
            
            return programme
            
        except Exception as e:
            logger.error(f"Error extracting programme info: {e}")
            return None
    
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
    
    def _go_to_next_page(self, driver) -> bool:
        """Navigate to next page if available"""
        try:
            next_button = driver.find_element(By.XPATH, "//a[contains(@class, 'next')]")
            if next_button.is_enabled():
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
    scraper = HRKScraper()
    programmes = scraper.scrape_english_programmes()
    
    print(f"Found {len(programmes)} programmes")
    for programme in programmes[:5]:  # Show first 5
        print(f"- {programme['program_name']} at {programme['institution']}")

if __name__ == "__main__":
    main()