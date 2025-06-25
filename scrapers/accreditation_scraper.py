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
        self.base_url = "https://www.akkreditierungsrat.de/studiensuche"
        
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

        try:
            # For now, return a placeholder to avoid breaking the ETL pipeline
            # TODO: Implement proper Accreditation Council scraping
            logger.info("Accreditation Council scraper temporarily disabled - needs implementation")
            logger.info("Returning empty list to avoid ETL pipeline errors")

            # Placeholder data structure for testing
            programmes = []

        except Exception as e:
            logger.error(f"Error in Accreditation Council scraper: {e}")

        return programmes
    
    def _set_search_filters(self, driver):
        """Set search filters for English-taught programmes"""
        try:
            # Search for programmes with "English" in the name or description
            search_term_input = driver.find_element(By.NAME, "search")
            search_term_input.clear()
            search_term_input.send_keys("English")
            
            # Filter for recently accredited programmes (last 2 years)
            try:
                date_from = driver.find_element(By.NAME, "accredited_from")
                two_years_ago = (datetime.now() - timedelta(days=730)).strftime("%Y-%m-%d")
                date_from.send_keys(two_years_ago)
            except NoSuchElementException:
                logger.debug("Date filter not available")
            
            # Select university types if available
            try:
                university_checkbox = driver.find_element(By.XPATH, "//input[@value='Universität']")
                if not university_checkbox.is_selected():
                    university_checkbox.click()
            except NoSuchElementException:
                logger.debug("University type filter not available")
            
            time.sleep(2)  # Allow filters to be applied
            
        except Exception as e:
            logger.error(f"Error setting Accreditation Council search filters: {e}")
    
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
            logger.error("Accreditation Council search results did not load")
            raise
    
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
            # Get all programme result elements
            result_elements = driver.find_elements(By.CLASS_NAME, "result-item")
            
            if not result_elements:
                # Try alternative selectors
                result_elements = driver.find_elements(By.CLASS_NAME, "programme-entry")
            
            for element in result_elements:
                try:
                    programme = self._extract_programme_info(element)
                    if programme and self._is_english_programme(programme):
                        programmes.append(programme)
                except Exception as e:
                    logger.error(f"Error extracting Accreditation Council programme info: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"Error scraping Accreditation Council results page: {e}")
        
        return programmes
    
    def _extract_programme_info(self, element) -> Dict:
        """Extract programme information from result element"""
        try:
            # Programme name
            name_elem = element.find_element(By.CLASS_NAME, "programme-name")
            program_name = name_elem.text.strip()
            
            # Institution name
            institution_elem = element.find_element(By.CLASS_NAME, "institution")
            institution = institution_elem.text.strip()
            
            # Degree type
            try:
                degree_elem = element.find_element(By.CLASS_NAME, "degree-type")
                degree = degree_elem.text.strip()
            except NoSuchElementException:
                # Try to extract from programme name
                degree = self._extract_degree_from_name(program_name)
            
            # Accreditation date
            try:
                accred_elem = element.find_element(By.CLASS_NAME, "accreditation-date")
                accreditation_date = accred_elem.text.strip()
            except NoSuchElementException:
                accreditation_date = None
            
            # Programme URL (if available)
            try:
                url_elem = element.find_element(By.TAG_NAME, "a")
                program_url = url_elem.get_attribute("href")
            except NoSuchElementException:
                program_url = ""
            
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
            logger.error(f"Error extracting Accreditation Council programme info: {e}")
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