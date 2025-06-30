#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Run HRK scraper with increased limits to get the full dataset
"""

import logging
import time
from datetime import datetime
from hrk_scraper import HRKScraper

def run_full_hrk():
    """Run HRK with full pagination"""
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('/tmp/hrk_full_scrape.log'),
            logging.StreamHandler()
        ]
    )
    
    print("STARTING FULL HRK SCRAPE")
    print("=" * 50)
    print("Target: ~22,353 programmes from ~2,236 pages")
    print("Estimated time: 4-6 hours")
    print("Current max_pages: 2,500")
    print()
    
    start_time = datetime.now()
    
    # Run the scraper
    scraper = HRKScraper()
    programmes = scraper.scrape_english_programmes()
    
    end_time = datetime.now()
    duration = end_time - start_time
    
    print("\nHRK SCRAPE COMPLETE!")
    print("Total programmes: {}".format(len(programmes)))
    print("Duration: {}".format(duration))
    print("Average rate: {:.1f} programmes/minute".format(len(programmes) / duration.total_seconds() * 60))
    
    return len(programmes)

if __name__ == "__main__":
    run_full_hrk()