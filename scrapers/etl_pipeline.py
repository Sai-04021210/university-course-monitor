#!/usr/bin/env python3
"""
ETL Pipeline for Course Monitor
Extracts data from HRK, DAAD, and Accreditation Council
Transforms and loads into PostgreSQL database
"""

import os
import sys
import json
import logging
from datetime import datetime
from typing import List, Dict, Optional
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

# Import individual scrapers
from hrk_scraper import HRKScraper
from daad_scraper import DAADScraper
from accreditation_scraper import AccreditationScraper

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/etl.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ETLPipeline:
    def __init__(self):
        self.db_url = self._get_db_url()
        self.engine = create_engine(self.db_url)
        self.Session = sessionmaker(bind=self.engine)
        
        # Initialize scrapers
        self.hrk_scraper = HRKScraper()
        self.daad_scraper = DAADScraper()
        self.accreditation_scraper = AccreditationScraper()
        
    def _get_db_url(self) -> str:
        """Get database URL from environment variables"""
        host = os.getenv('POSTGRES_HOST', '127.0.0.1')
        db = os.getenv('POSTGRES_DB', 'course_monitor')
        user = os.getenv('POSTGRES_USER', 'course_user')
        password = os.getenv('POSTGRES_PASSWORD', 'course_monitor_secure_password_2024')

        db_url = f"postgresql://{user}:{password}@{host}:5432/{db}"
        logger.info(f"Connecting to database: postgresql://{user}:***@{host}:5432/{db}")
        return db_url
    
    def extract_data(self) -> Dict[str, List[Dict]]:
        """Extract data from all sources"""
        logger.info("Starting data extraction from all sources")
        
        data = {
            'hrk': [],
            'daad': [],
            'accreditation': []
        }
        
        try:
            # Extract from DAAD (working)
            logger.info("Extracting from DAAD International Programmes")
            data['daad'] = self.daad_scraper.scrape_english_programmes()
            logger.info(f"Extracted {len(data['daad'])} programmes from DAAD")

        except Exception as e:
            logger.error(f"Error extracting from DAAD: {e}")

        try:
            # Extract from HRK (placeholder for now)
            logger.info("Extracting from HRK Hochschulkompass")
            data['hrk'] = self.hrk_scraper.scrape_english_programmes()
            logger.info(f"Extracted {len(data['hrk'])} programmes from HRK")

        except Exception as e:
            logger.error(f"Error extracting from HRK: {e}")

        try:
            # Extract from Accreditation Council (placeholder for now)
            logger.info("Extracting from German Accreditation Council")
            data['accreditation'] = self.accreditation_scraper.scrape_english_programmes()
            logger.info(f"Extracted {len(data['accreditation'])} programmes from Accreditation Council")

        except Exception as e:
            logger.error(f"Error extracting from Accreditation Council: {e}")
        
        return data
    
    def transform_data(self, raw_data: Dict[str, List[Dict]]) -> pd.DataFrame:
        """Transform and normalize data from all sources"""
        logger.info("Starting data transformation")
        
        all_programmes = []
        
        for source, programmes in raw_data.items():
            for programme in programmes:
                transformed = self._transform_programme(programme, source)
                if transformed:
                    all_programmes.append(transformed)
        
        df = pd.DataFrame(all_programmes)
        
        if df.empty:
            logger.warning("No programmes to transform")
            return df
        
        # Remove duplicates based on institution, programme name, and degree
        df = df.drop_duplicates(subset=['institution_name', 'program_name', 'degree'])
        
        # Normalize tuition fees
        df['tuition_fee'] = df['tuition_fee'].fillna(0)
        df['tuition_fee'] = pd.to_numeric(df['tuition_fee'], errors='coerce').fillna(0)
        
        # Standardize language field
        df['language'] = df['language'].str.strip().str.title()
        
        logger.info(f"Transformed {len(df)} unique programmes")
        return df
    
    def _transform_programme(self, programme: Dict, source: str) -> Optional[Dict]:
        """Transform individual programme data"""
        try:
            transformed = {
                'institution_name': programme.get('institution', '').strip(),
                'program_name': programme.get('program_name', '').strip(),
                'degree': programme.get('degree', '').strip(),
                'language': programme.get('language', 'English'),
                'tuition_fee': self._parse_tuition(programme.get('tuition_fee', 0)),
                'tuition_period': programme.get('tuition_period', 'semester'),
                'start_date': programme.get('start_date', ''),
                'source': source.upper(),
                'source_url': programme.get('source_url', ''),
                'accreditation_date': programme.get('accreditation_date')
            }
            
            # Validate programme data quality
            if not self._validate_programme(transformed):
                logger.debug(f"Programme failed validation: {transformed['program_name']} at {transformed['institution_name']}")
                return None
                
            return transformed
        except Exception as e:
            logger.error(f"Error transforming programme {programme}: {e}")
            return None
    
    def _parse_tuition(self, tuition_str) -> float:
        """Parse tuition fee string to numeric value"""
        if not tuition_str or tuition_str in ['None', 'Free', 'Tuition-free', '-']:
            return 0.0
        
        if isinstance(tuition_str, (int, float)):
            return float(tuition_str)
        
        # Extract numeric value from string
        import re
        numbers = re.findall(r'[\d,]+\.?\d*', str(tuition_str))
        if numbers:
            return float(numbers[0].replace(',', ''))
        
        return 0.0
    
    def _validate_programme(self, programme: Dict) -> bool:
        """Validate programme data quality - reject UI elements and invalid data"""
        program_name = programme.get('program_name', '').strip()
        institution_name = programme.get('institution_name', '').strip()
        
        # Reject empty or too short names
        if len(program_name) < 3:
            return False
            
        # Reject common UI elements and invalid data
        ui_elements = {
            'grid', 'map', 'activate map', 'sort by', 'filter', 'search',
            'results', 'page', 'next', 'previous', 'show more', 'load more',
            'cookie', 'accept', 'decline', 'privacy', 'toggle', 'menu',
            'navigation', 'breadcrumb', 'footer', 'header', 'sidebar',
            'help', 'support', 'feedback', 'improve', 'website', 'contact'
        }
        
        if program_name.lower() in ui_elements:
            return False
            
        # Reject numeric-only program names
        if program_name.isdigit():
            return False
            
        # Reject single characters or very short strings
        if len(program_name.strip()) <= 2:
            return False
            
        # Reject if institution is 'Unknown' and no source URL
        if institution_name.lower() in ['unknown', ''] and not programme.get('source_url'):
            return False
            
        # Programme name should contain letters (not just symbols/numbers)
        if not any(c.isalpha() for c in program_name):
            return False
            
        # Reject common web elements and help messages
        web_elements = [
            'click here', 'read more', 'learn more', 'find out',
            'download', 'upload', 'submit', 'reset', 'cancel',
            'ok', 'yes', 'no', 'back', 'home', 'contact',
            'we need your help', 'improve our website', 'help us',
            'feedback', 'survey', 'newsletter', 'subscribe',
            'follow us', 'social media', 'share this'
        ]
        
        if any(element in program_name.lower() for element in web_elements):
            return False
            
        # Reject programme names that contain typical help/website text patterns
        help_patterns = [
            'help to improve', 'your help to', 'feedback',
            'we need', 'please help', 'improve our',
            'website', 'survey', 'questionnaire'
        ]
        
        if any(pattern in program_name.lower() for pattern in help_patterns):
            return False
            
        logger.debug(f"Programme passed validation: {program_name} at {institution_name}")
        return True
    
    def load_data(self, df: pd.DataFrame) -> Dict[str, int]:
        """Load data into PostgreSQL database"""
        logger.info("Starting data loading to database")
        
        stats = {
            'new_programmes': 0,
            'updated_programmes': 0,
            'new_institutions': 0
        }
        
        if df.empty:
            logger.warning("No data to load")
            return stats
        
        session = self.Session()
        
        try:
            # Process each programme
            for _, row in df.iterrows():
                # Get or create institution
                inst_id = self._get_or_create_institution(session, row)
                if inst_id:
                    stats['new_institutions'] += 1 if inst_id == 'new' else 0
                    
                    # Insert or update programme
                    result = self._upsert_programme(session, row, inst_id)
                    if result == 'new':
                        stats['new_programmes'] += 1
                    elif result == 'updated':
                        stats['updated_programmes'] += 1
            
            session.commit()
            logger.info(f"Data loading completed: {stats}")
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error loading data: {e}")
            raise
        finally:
            session.close()
        
        return stats
    
    def _get_or_create_institution(self, session, row) -> Optional[int]:
        """Get existing institution or create new one"""
        institution_name = row['institution_name']
        
        # Check if institution exists
        result = session.execute(
            text("SELECT inst_id FROM institutions WHERE name = :name"),
            {'name': institution_name}
        ).fetchone()
        
        if result:
            return result[0]
        
        # Create new institution
        try:
            result = session.execute(
                text("""
                    INSERT INTO institutions (name, type, status, created_at)
                    VALUES (:name, 'Universität', 'public', CURRENT_TIMESTAMP)
                    RETURNING inst_id
                """),
                {'name': institution_name}
            )
            session.commit()
            return result.fetchone()[0]
        except IntegrityError:
            session.rollback()
            # Institution might have been created by another process
            result = session.execute(
                text("SELECT inst_id FROM institutions WHERE name = :name"),
                {'name': institution_name}
            ).fetchone()
            return result[0] if result else None
    
    def _upsert_programme(self, session, row, inst_id: int) -> str:
        """Insert new programme or update existing one"""
        
        # Check if programme exists
        result = session.execute(
            text("""
                SELECT prog_id FROM programmes 
                WHERE inst_id = :inst_id AND program_name = :name AND degree = :degree
                AND is_active = TRUE
            """),
            {
                'inst_id': inst_id,
                'name': row['program_name'],
                'degree': row['degree']
            }
        ).fetchone()
        
        if result:
            # Update existing programme
            session.execute(
                text("""
                    UPDATE programmes SET
                        language = :language,
                        tuition_fee = :tuition_fee,
                        tuition_period = :tuition_period,
                        start_date = :start_date,
                        source = :source,
                        source_url = :source_url,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE prog_id = :prog_id
                """),
                {
                    'prog_id': result[0],
                    'language': row['language'],
                    'tuition_fee': row['tuition_fee'],
                    'tuition_period': row['tuition_period'],
                    'start_date': row['start_date'],
                    'source': row['source'],
                    'source_url': row['source_url']
                }
            )
            return 'updated'
        else:
            # Insert new programme
            session.execute(
                text("""
                    INSERT INTO programmes (
                        inst_id, program_name, degree, language, tuition_fee,
                        tuition_period, start_date, source, source_url,
                        accreditation_date, created_at, updated_at
                    ) VALUES (
                        :inst_id, :program_name, :degree, :language, :tuition_fee,
                        :tuition_period, :start_date, :source, :source_url,
                        :accreditation_date, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                    )
                """),
                {
                    'inst_id': inst_id,
                    'program_name': row['program_name'],
                    'degree': row['degree'],
                    'language': row['language'],
                    'tuition_fee': row['tuition_fee'],
                    'tuition_period': row['tuition_period'],
                    'start_date': row['start_date'],
                    'source': row['source'],
                    'source_url': row['source_url'],
                    'accreditation_date': row.get('accreditation_date')
                }
            )
            return 'new'
    
    def run_etl(self) -> Dict[str, int]:
        """Run the complete ETL pipeline"""
        logger.info("Starting ETL pipeline")
        start_time = datetime.now()
        
        try:
            # Extract
            raw_data = self.extract_data()
            
            # Transform
            df = self.transform_data(raw_data)
            
            # Load
            stats = self.load_data(df)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            logger.info(f"ETL pipeline completed in {duration:.2f} seconds")
            logger.info(f"Final stats: {stats}")
            
            return stats
            
        except Exception as e:
            logger.error(f"ETL pipeline failed: {e}")
            raise

def main():
    """Main entry point"""
    try:
        pipeline = ETLPipeline()
        stats = pipeline.run_etl()
        
        # Output stats for Node-RED to consume
        print(json.dumps(stats))
        
    except Exception as e:
        logger.error(f"ETL pipeline failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()