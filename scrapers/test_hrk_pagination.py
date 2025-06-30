#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test HRK pagination debugging
"""

import logging
import sys
from hrk_scraper import HRKScraper

def test_pagination():
    """Test HRK pagination with detailed logging"""
    
    # Setup detailed logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    print("Testing HRK pagination with detailed debugging")
    print("=" * 60)
    
    # Temporarily reduce max_pages for testing
    scraper = HRKScraper()
    
    # Override max_pages in the scraper for testing
    original_scrape_method = scraper._scrape_all_results
    
    def test_scrape_results(driver):
        programmes = []
        page = 1
        max_pages = 20  # Test with 20 pages
        
        try:
            # First, try to increase results per page to 100 for efficiency
            scraper._set_results_per_page(driver, 100)
            
            while page <= max_pages:
                logging.info(f"=== TESTING PAGE {page} ===")
                
                # Scrape current page
                page_programmes = scraper._scrape_results_page(driver)
                if not page_programmes:
                    logging.info("No programmes found on this page, stopping")
                    break
                    
                programmes.extend(page_programmes)
                logging.info(f"Page {page}: Found {len(page_programmes)} programmes (Total: {len(programmes)})")
                
                # Check if there's a next page and navigate to it
                if not scraper._go_to_next_page(driver):
                    logging.info("No more pages available")
                    break
                
                page += 1
                
                # Stop early for debugging
                if page > 16:  # Stop after a few pages past the problem
                    logging.info("Stopping early for debugging")
                    break
                
        except Exception as e:
            logging.error(f"Error during pagination test: {e}")
        
        logging.info(f"HRK pagination test completed: {len(programmes)} programmes from {page-1} pages")
        return programmes
    
    # Replace the method temporarily
    scraper._scrape_all_results = test_scrape_results
    
    # Run the test
    programmes = scraper.scrape_english_programmes()
    
    print(f"\nTest completed: {len(programmes)} programmes found")
    return len(programmes)

if __name__ == "__main__":
    test_pagination()