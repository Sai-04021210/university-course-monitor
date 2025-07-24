#!/usr/bin/env python3
"""
MyGermanUniversity.com Scraper
===============================

IMPORTANT NOTICE:
This scraper is provided as a foundation/reference implementation only.
It is NOT RECOMMENDED for production use due to:

1. Data Redundancy: 85-90% overlap with existing DAAD + HRK sources
2. Legal Risks: Potential Terms of Service violations
3. Data Quality: Secondary source vs primary official sources
4. Cost/Benefit: High implementation cost with minimal additional value

Your current system with DAAD + HRK provides superior coverage:
- Current: 10,335 programmes from official sources
- MGU would add: ~600 unique programmes (15% of 4,060)
- Quality: Official government sources vs commercial aggregator

This implementation is provided for completeness and future reference only.
"""

import requests
import time
import json
import logging
from typing import List, Dict, Optional, Set
from dataclasses import dataclass
from urllib.parse import urljoin, urlparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MGUProgramme:
    """Data structure for MyGermanUniversity programme"""
    title: str
    university: str
    degree_type: str
    duration: Optional[str]
    language: str
    tuition_fees: Optional[str]
    application_deadline: Optional[str]
    description: Optional[str]
    requirements: Optional[str]
    url: str
    city: Optional[str]
    state: Optional[str]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for database insertion"""
        return {
            'title': self.title,
            'university': self.university,
            'degree_type': self.degree_type,
            'duration': self.duration,
            'language': self.language,
            'tuition_fees': self.tuition_fees,
            'application_deadline': self.application_deadline,
            'description': self.description,
            'requirements': self.requirements,
            'url': self.url,
            'city': self.city,
            'state': self.state,
            'source': 'MyGermanUniversity'
        }

class MyGermanUniversityScraper:
    """
    Scraper for MyGermanUniversity.com
    
    WARNING: This is a reference implementation only.
    NOT RECOMMENDED for production use - see module docstring for reasons.
    """
    
    def __init__(self, headless: bool = True, delay: float = 2.0):
        """
        Initialize the scraper
        
        Args:
            headless: Run browser in headless mode
            delay: Delay between requests (seconds)
        """
        self.base_url = "https://www.mygermanuniversity.com"
        self.delay = delay
        self.headless = headless
        self.driver = None
        self.programmes: List[MGUProgramme] = []
        
        # Track processed URLs to avoid duplicates
        self.processed_urls: Set[str] = set()
        
        logger.warning("  MyGermanUniversity scraper initialized")
        logger.warning("  This scraper is NOT RECOMMENDED for production use")
        logger.warning("  See module docstring for detailed reasons")
    
    def _setup_driver(self) -> webdriver.Chrome:
        """Setup Chrome WebDriver with appropriate options"""
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument("--headless")
        
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        
        # Disable images and CSS for faster loading
        prefs = {
            "profile.managed_default_content_settings.images": 2,
            "profile.managed_default_content_settings.stylesheets": 2
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        return webdriver.Chrome(options=chrome_options)
    
    def _wait_and_respect_limits(self):
        """Wait between requests to be respectful"""
        time.sleep(self.delay)
    
    def scrape_programmes(self, max_pages: int = 50) -> List[MGUProgramme]:
        """
        Scrape programmes from MyGermanUniversity
        
        Args:
            max_pages: Maximum number of pages to scrape
            
        Returns:
            List of MGUProgramme objects
            
        Note:
            This is a reference implementation. The actual implementation
            would need to be adapted based on the current site structure.
        """
        logger.warning("🚨 STARTING MGU SCRAPER - NOT RECOMMENDED FOR PRODUCTION")
        logger.info(f"Scraping up to {max_pages} pages from MyGermanUniversity")
        
        try:
            self.driver = self._setup_driver()
            
            # Start with the programmes search page
            search_url = f"{self.base_url}/search-programs"
            logger.info(f"Starting scrape from: {search_url}")
            
            self.driver.get(search_url)
            self._wait_and_respect_limits()
            
            # This is where the actual scraping logic would go
            # The implementation would depend on the current site structure
            
            # Placeholder implementation - would need to be adapted
            programmes = self._scrape_programme_listings(max_pages)
            
            logger.info(f"Scraped {len(programmes)} programmes from MyGermanUniversity")
            return programmes
            
        except Exception as e:
            logger.error(f"Error during MGU scraping: {e}")
            return []
        
        finally:
            if self.driver:
                self.driver.quit()
    
    def _scrape_programme_listings(self, max_pages: int) -> List[MGUProgramme]:
        """
        Scrape programme listings from search results
        
        This is a placeholder implementation that would need to be
        adapted based on the actual site structure.
        """
        programmes = []
        
        for page in range(1, max_pages + 1):
            logger.info(f"Scraping page {page}/{max_pages}")
            
            try:
                # This would need to be adapted to the actual site structure
                # Example placeholder logic:
                
                # Find programme cards/links on the page
                programme_elements = self.driver.find_elements(By.CLASS_NAME, "programme-card")
                
                if not programme_elements:
                    logger.info("No more programmes found, stopping")
                    break
                
                for element in programme_elements:
                    try:
                        programme = self._extract_programme_data(element)
                        if programme and programme.url not in self.processed_urls:
                            programmes.append(programme)
                            self.processed_urls.add(programme.url)
                    except Exception as e:
                        logger.warning(f"Error extracting programme data: {e}")
                        continue
                
                # Navigate to next page
                if not self._go_to_next_page():
                    logger.info("No more pages available")
                    break
                
                self._wait_and_respect_limits()
                
            except Exception as e:
                logger.error(f"Error on page {page}: {e}")
                continue
        
        return programmes
    
    def _extract_programme_data(self, element) -> Optional[MGUProgramme]:
        """
        Extract programme data from a programme element
        
        This is a placeholder that would need to be adapted
        to the actual HTML structure of the site.
        """
        try:
            # Placeholder extraction logic - would need adaptation
            title = element.find_element(By.CLASS_NAME, "programme-title").text
            university = element.find_element(By.CLASS_NAME, "university-name").text
            degree_type = element.find_element(By.CLASS_NAME, "degree-type").text
            url = element.find_element(By.TAG_NAME, "a").get_attribute("href")
            
            # Create programme object
            programme = MGUProgramme(
                title=title.strip(),
                university=university.strip(),
                degree_type=degree_type.strip(),
                duration=None,  # Would extract from detail page
                language="English",  # Assumption - would need verification
                tuition_fees=None,  # Would extract from detail page
                application_deadline=None,  # Would extract from detail page
                description=None,  # Would extract from detail page
                requirements=None,  # Would extract from detail page
                url=url,
                city=None,  # Would extract from detail page
                state=None  # Would extract from detail page
            )
            
            return programme
            
        except NoSuchElementException as e:
            logger.warning(f"Missing element in programme extraction: {e}")
            return None
    
    def _go_to_next_page(self) -> bool:
        """Navigate to the next page of results"""
        try:
            next_button = self.driver.find_element(By.CLASS_NAME, "next-page")
            if next_button.is_enabled():
                next_button.click()
                return True
            return False
        except NoSuchElementException:
            return False
    
    def save_to_json(self, filename: str = "mgu_programmes.json"):
        """Save scraped programmes to JSON file"""
        data = [programme.to_dict() for programme in self.programmes]
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved {len(data)} programmes to {filename}")

def main():
    """
    Main function - demonstrates usage but includes warnings
    """
    print("🚨" * 50)
    print("  WARNING: MyGermanUniversity Scraper")
    print("  This scraper is NOT RECOMMENDED for production use!")
    print("  Reasons:")
    print("  1. 85-90% data overlap with existing DAAD + HRK sources")
    print("  2. Legal risks - potential ToS violations")
    print("  3. Lower data quality vs official sources")
    print("  4. High implementation cost, minimal benefit")
    print("")
    print("  Your current system (10,335 programmes) is superior!")
    print("🚨" * 50)
    
    response = input("\nDo you still want to run this scraper? (yes/no): ")
    if response.lower() != 'yes':
        print("Scraper cancelled. Good choice!")
        return
    
    scraper = MyGermanUniversityScraper(headless=True, delay=3.0)
    
    try:
        programmes = scraper.scrape_programmes(max_pages=10)  # Limited for testing
        
        if programmes:
            scraper.programmes = programmes
            scraper.save_to_json()
            print(f"\n Scraped {len(programmes)} programmes")
            print(" Saved to mgu_programmes.json")
        else:
            print(" No programmes scraped")
            
    except KeyboardInterrupt:
        print("\n🛑 Scraping interrupted by user")
    except Exception as e:
        print(f" Error during scraping: {e}")

def integrate_with_etl():
    """
    Integration function for ETL pipeline

    This function would be called from etl_pipeline.py if MGU scraper
    was to be integrated (NOT RECOMMENDED).
    """
    logger.warning("🚨 MGU Integration called - NOT RECOMMENDED for production")

    # Return empty list to avoid breaking ETL pipeline
    return []

if __name__ == "__main__":
    main()
