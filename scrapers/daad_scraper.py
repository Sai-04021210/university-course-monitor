#!/usr/bin/env python3
"""
DAAD Course Scraper
Uses DAAD API to fetch English-taught programmes from DAAD International Programmes database
API Documentation: https://www2.daad.de/deutschland/studienangebote/international-programmes/api/
"""

import logging
import requests
import time
from typing import List, Dict
import json

logger = logging.getLogger(__name__)

class DAADScraper:
    def __init__(self):
        self.api_url = "https://www2.daad.de/deutschland/studienangebote/international-programmes/api/solr/en/search.json"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def scrape_english_programmes(self) -> List[Dict]:
        """Fetch English-taught programmes from DAAD API"""
        logger.info("Starting DAAD API scraper")

        programmes = []

        try:
            # Use the working JSON API to get all programmes at once
            logger.info("Fetching all DAAD programmes from JSON API")
            programmes = self._fetch_from_json_api()

            logger.info(f"DAAD API scraper completed. Found {len(programmes)} programmes")

        except Exception as e:
            logger.error(f"Error in DAAD API scraper: {e}")

        return programmes

    def _fetch_from_json_api(self) -> List[Dict]:
        """Fetch all programmes from DAAD JSON API"""
        programmes = []

        try:
            # Parameters for the JSON API - get all programmes
            params = {
                'rows': '5000'  # Get up to 5000 programmes (all available)
            }

            logger.info("Making request to DAAD JSON API...")
            response = self.session.get(self.api_url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()

            # Debug: Save response to file and log structure
            with open('/tmp/daad_api_response.json', 'w') as f:
                json.dump(data, f, indent=2)
            logger.info(f"Saved API response to /tmp/daad_api_response.json")
            logger.info(f"Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")

            if 'courses' not in data:
                logger.error(f"No 'courses' key in API response. Available keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                return programmes

            docs = data['courses']
            total_found = data.get('numResults', 0)

            logger.info(f"API returned {len(docs)} programmes out of {total_found} total")

            # Process each programme
            for doc in docs:
                programme = self._extract_programme_from_json(doc)
                if programme:
                    programmes.append(programme)

        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
        except Exception as e:
            logger.error(f"Error fetching programmes from JSON API: {e}")

        return programmes

    def _extract_programme_from_json(self, doc: Dict) -> Dict:
        """Extract programme information from JSON API response"""
        try:
            # Extract basic information using actual API field names
            program_name = doc.get('courseName', '')
            if not program_name:
                return None

            # Extract institution information
            institution = doc.get('academy', '')

            # Extract degree information from course type
            course_type = doc.get('courseType', 0)
            degree = self._normalize_degree_from_course_type(course_type)

            # Extract language information
            languages = doc.get('languages', [])
            if isinstance(languages, list):
                language = ', '.join(languages) if languages else 'Unknown'
            else:
                language = str(languages) if languages else 'Unknown'

            # Filter for English programmes only
            if not self._has_english_language(language):
                return None

            # Extract tuition fee information
            tuition_fee = 0
            dates = doc.get('date', [])
            if dates and isinstance(dates, list) and len(dates) > 0:
                first_date = dates[0]
                if isinstance(first_date, dict):
                    costs = first_date.get('costs', 0)
                    if costs:
                        try:
                            tuition_fee = float(costs)
                        except (ValueError, TypeError):
                            tuition_fee = 0

            # Extract start date
            start_date = ''
            if dates and isinstance(dates, list) and len(dates) > 0:
                first_date = dates[0]
                if isinstance(first_date, dict):
                    start_date = first_date.get('start', '')

            # Extract programme URL
            program_url = doc.get('link', '')
            if program_url and not program_url.startswith('http'):
                program_url = 'https://www2.daad.de' + program_url

            # Extract location
            location = doc.get('city', '')

            programme = {
                'program_name': program_name.strip(),
                'institution': institution.strip() if institution else 'Unknown',
                'degree': degree,
                'language': language,
                'source_url': program_url,
                'tuition_fee': tuition_fee,
                'start_date': str(start_date),
                'tuition_period': 'course',
                'location': location
            }

            return programme

        except Exception as e:
            logger.error(f"Error extracting programme from JSON: {e}")
            return None

    def _normalize_degree_from_course_type(self, course_type: int) -> str:
        """Normalize degree level from DAAD course type"""
        # Based on DAAD course type mapping
        course_type_mapping = {
            1: 'B.Sc.',      # Bachelor's degree
            2: 'M.Sc.',      # Master's degree
            3: 'Ph.D.',      # PhD / Doctorate
            4: 'Graduate',   # Graduate school
            5: 'Language',   # Language course
            6: 'Short',      # Short course
            7: 'Prep',       # Preparatory course
            8: 'Online',     # Online degree
            9: 'Various'     # Various
        }

        return course_type_mapping.get(course_type, 'Unknown')

    def _has_english_language(self, language: str) -> bool:
        """Check if the programme has English language instruction"""
        if not language:
            return False

        language_lower = language.lower()
        english_indicators = ['english', 'englisch', 'en']

        return any(indicator in language_lower for indicator in english_indicators)

    def _parse_search_results(self, html_content: str, degree_level: str) -> List[Dict]:
        """Parse HTML search results to extract programme information"""
        from bs4 import BeautifulSoup
        programmes = []

        try:
            soup = BeautifulSoup(html_content, 'html.parser')

            # Debug: Save HTML to file for inspection
            with open(f'/tmp/daad_search_{degree_level}.html', 'w', encoding='utf-8') as f:
                f.write(html_content)
            logger.info(f"Saved HTML to /tmp/daad_search_{degree_level}.html for debugging")

            # Look for programme entries in the search results
            # Try DAAD-specific selectors first, then fallbacks
            selectors_to_try = [
                'article.c-search-result',  # Main programme articles
                'div.c-search-result',      # Alternative programme containers
                '.c-search-result',         # CSS class only
                'article[class*="search"]', # Articles with search in class
                'div[class*="search"]',     # Divs with search in class
                '.search-result',           # Generic search result class
                'article',                  # All articles as last resort
                'div.result'                # Generic result divs
            ]

            programme_elements = []
            for selector in selectors_to_try:
                programme_elements = soup.select(selector)
                if programme_elements:
                    logger.info(f"Found {len(programme_elements)} elements with selector: {selector}")
                    # Filter out obvious non-programme elements
                    filtered_elements = []
                    for elem in programme_elements:
                        text = elem.get_text().strip().lower()
                        # Skip elements that are clearly UI components or modal popups
                        skip_words = ['grid', 'activate map', 'sort by', 'filter', 'cookie',
                                    'we need your help', 'improve our website', 'questionnaire',
                                    'modal', 'close', 'feedback']
                        if not any(ui_word in text for ui_word in skip_words):
                            filtered_elements.append(elem)
                    
                    if filtered_elements:
                        programme_elements = filtered_elements
                        logger.info(f"After filtering: {len(programme_elements)} valid programme elements")
                        break

            if not programme_elements:
                # Check if there's a "no results" message
                no_results = soup.find(text=lambda text: text and ('no results' in text.lower() or 'keine ergebnisse' in text.lower()))
                if no_results:
                    logger.info(f"No programmes found for {degree_level} - search returned no results")
                else:
                    logger.warning(f"Could not find programme elements. Available classes: {[elem.get('class') for elem in soup.find_all() if elem.get('class')][:10]}")

            for i, element in enumerate(programme_elements):
                try:
                    logger.debug(f"Processing element {i+1}: {element.get('class', [])} - {element.name}")
                    logger.debug(f"Element text preview: {element.get_text()[:200]}...")

                    programme = self._extract_programme_from_html(element, degree_level)
                    if programme:
                        programmes.append(programme)
                        logger.info(f"Successfully extracted programme: {programme['program_name']}")
                    else:
                        logger.debug(f"Failed to extract programme from element {i+1}")
                except Exception as e:
                    logger.error(f"Error extracting programme from HTML element {i+1}: {e}")
                    continue

        except Exception as e:
            logger.error(f"Error parsing HTML search results: {e}")

        return programmes

    def _extract_programme_from_html(self, element, degree_level: str) -> Dict:
        """Extract programme information from HTML element"""
        try:
            # Extract programme name - try multiple selectors
            program_name = ""
            name_selectors = [
                'h3', 'h2', 'h4', 'h1',
                'a.title', '.title', '.programme-title', '.course-title',
                'a[href*="detail"]', 'a[href*="programme"]'
            ]

            for selector in name_selectors:
                name_elem = element.select_one(selector)
                if name_elem:
                    program_name = name_elem.get_text(strip=True)
                    if program_name:
                        break

            # If no name found, try getting the first link text
            if not program_name:
                first_link = element.find('a')
                if first_link:
                    program_name = first_link.get_text(strip=True)

            # Extract institution name - try multiple selectors
            institution = ""
            inst_selectors = [
                '.institution', '.university', '.hochschule',
                'p:contains("University")', 'p:contains("Hochschule")',
                '.institution-name', '.uni-name'
            ]

            for selector in inst_selectors:
                inst_elem = element.select_one(selector)
                if inst_elem:
                    institution = inst_elem.get_text(strip=True)
                    if institution:
                        break

            # If no institution found, look for text containing university keywords
            if not institution:
                text = element.get_text()
                import re
                uni_match = re.search(r'(.*(?:University|Hochschule|Institut|College)[^,\n]*)', text, re.IGNORECASE)
                if uni_match:
                    institution = uni_match.group(1).strip()

            # Extract programme URL
            program_url = ""
            link_elem = element.find('a')
            if link_elem and link_elem.get('href'):
                program_url = link_elem['href']
                if program_url.startswith('/'):
                    program_url = 'https://www2.daad.de' + program_url

            # Extract degree information
            degree = self._normalize_degree(degree_level)

            # Log what we found for debugging
            logger.debug(f"Extracted: name='{program_name}', institution='{institution}', url='{program_url}'")

            # Return programme if we have at least a name
            if program_name:
                programme = {
                    'program_name': program_name.strip(),
                    'institution': institution.strip() if institution else 'Unknown',
                    'degree': degree,
                    'language': 'English',
                    'source_url': program_url,
                    'tuition_fee': 0,
                    'start_date': '',
                    'tuition_period': 'semester'
                }

                return programme

        except Exception as e:
            logger.error(f"Error extracting programme from HTML element: {e}")

        return None


    def _normalize_degree(self, degree_level: str) -> str:
        """Normalize degree level to standard format"""
        mapping = {
            'bachelor': 'B.Sc.',
            'master': 'M.Sc.',
            'phd': 'Ph.D.'
        }
        return mapping.get(degree_level.lower(), degree_level.title())

def main():
    """For testing the scraper independently"""
    logging.basicConfig(level=logging.INFO)
    scraper = DAADScraper()
    programmes = scraper.scrape_english_programmes()

    print(f"Found {len(programmes)} programmes")
    for programme in programmes[:5]:  # Show first 5
        print(f"- {programme['program_name']} at {programme['institution']}")

    # Save to JSON for inspection
    if programmes:
        with open('/tmp/daad_programmes.json', 'w') as f:
            json.dump(programmes, f, indent=2)
        print(f"Saved programmes to /tmp/daad_programmes.json")

if __name__ == "__main__":
    main()