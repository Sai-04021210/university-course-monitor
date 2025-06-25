# Developer Guide - University Course Monitor

**Quick reference for developers working on the system**

---

## 🚀 **Quick Start**

### **Run the Working System:**
```bash
# Start infrastructure
docker compose up -d

# Run ETL pipeline (gets 2,217 programmes)
cd scrapers
python3 etl_pipeline.py

# View dashboard
open http://localhost:1880/ui
```

### **Check Database:**
```bash
# Connect to database
docker exec -it course-monitor-db psql -U course_user -d course_monitor

# Check data
SELECT COUNT(*) FROM programmes;
SELECT degree, COUNT(*) FROM programmes GROUP BY degree;
```

---

## 🔧 **Working Components**

### **✅ DAAD Scraper (scrapers/daad_scraper.py)**
```python
# Usage:
from daad_scraper import DAADScraper
scraper = DAADScraper()
programmes = scraper.scrape_english_programmes()  # Returns 2,217 programmes

# API endpoint:
https://www2.daad.de/deutschland/studienangebote/international-programmes/api/solr/en/search.json?rows=5000

# Key methods:
- scrape_english_programmes() -> List[Dict]
- _fetch_from_json_api() -> List[Dict] 
- _extract_programme_from_json(doc) -> Dict
- _has_english_language(language) -> bool
```

### **✅ ETL Pipeline (scrapers/etl_pipeline.py)**
```python
# Usage:
from etl_pipeline import ETLPipeline
pipeline = ETLPipeline()
pipeline.run()  # Complete ETL process

# Key methods:
- extract_data() -> Dict[str, List[Dict]]
- transform_data(raw_data) -> pd.DataFrame
- load_data(df) -> Dict[str, int]
```

### **✅ Database Schema**
```sql
-- Main tables:
institutions (inst_id, name, location, website, created_at)
programmes (prog_id, inst_id, program_name, degree, language, tuition_fee, ...)

-- Key indexes:
idx_programme_unique (inst_id, program_name, degree)
idx_programmes_language (language)
idx_programmes_source (source)
```

---

## ❌ **Broken Components (Need Fixing)**

### **❌ HRK Scraper (scrapers/hrk_scraper.py)**
```python
# Current status: Returns empty list
# Issue: Broken selectors

# To fix:
1. Research https://www.hochschulkompass.de/studium/studiengangsuche/erweiterte-suche
2. Update selectors in _set_search_filters()
3. Fix form submission in _submit_search()
4. Update result parsing in _scrape_results_page()

# Broken selectors to fix:
By.NAME, "unterrichtssprache"  # Language field
By.CLASS_NAME, "search-form"   # Search form
By.XPATH, "//input[@value='Universität']"  # University type
```

### **❌ Accreditation Scraper (scrapers/accreditation_scraper.py)**
```python
# Current status: Returns empty list
# Issue: No real implementation

# To fix:
1. Research German accreditation agencies
2. Find searchable databases
3. Implement agency-specific scrapers
4. Create unified data format

# Agencies to investigate:
- ACQUIN (www.acquin.org)
- AQAS (www.aqas.de)
- ASIIN (www.asiin.de)
- FIBAA (www.fibaa.org)
```

---

## 🛠 **Development Workflow**

### **Testing Individual Scrapers:**
```bash
# Test DAAD scraper (working)
cd scrapers
python3 daad_scraper.py

# Test HRK scraper (broken - returns 0)
python3 hrk_scraper.py

# Test Accreditation scraper (broken - returns 0)
python3 accreditation_scraper.py
```

### **Testing ETL Pipeline:**
```bash
# Full pipeline
python3 etl_pipeline.py

# Check logs
tail -f /tmp/etl.log
```

### **Database Operations:**
```bash
# Connect to database
docker exec -it course-monitor-db psql -U course_user -d course_monitor

# Useful queries:
SELECT COUNT(*) FROM programmes WHERE language LIKE '%English%';
SELECT institution.name, COUNT(*) FROM programmes p JOIN institutions i ON p.inst_id = i.inst_id GROUP BY i.name ORDER BY COUNT(*) DESC LIMIT 10;
SELECT degree, AVG(tuition_fee) FROM programmes WHERE tuition_fee > 0 GROUP BY degree;
```

---

## 🔍 **Debugging Guide**

### **Common Issues:**

#### **1. Database Connection Errors:**
```bash
# Check if database is running
docker ps | grep postgres

# Check connection
docker exec course-monitor-db psql -U course_user -d course_monitor -c "SELECT 1;"

# Fix: Update password in etl_pipeline.py if needed
password = os.getenv('POSTGRES_PASSWORD', 'course_monitor_secure_password_2024')
```

#### **2. DAAD API Issues:**
```python
# Check API response
import requests
response = requests.get('https://www2.daad.de/deutschland/studienangebote/international-programmes/api/solr/en/search.json?rows=10')
print(response.status_code)
print(response.json().keys())
```

#### **3. Scraper Import Errors:**
```bash
# Install dependencies
pip install -r scrapers/requirements.txt

# Check imports
python3 -c "from scrapers.daad_scraper import DAADScraper; print('OK')"
```

### **Logging and Monitoring:**
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Check ETL logs
tail -f /tmp/etl.log

# Check saved API responses
cat /tmp/daad_api_response.json | jq '.courses[0]'
```

---

## 📝 **Adding New Scrapers**

### **Template for New Scraper:**
```python
#!/usr/bin/env python3
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class NewScraper:
    def __init__(self):
        self.base_url = "https://example.com"
    
    def scrape_english_programmes(self) -> List[Dict]:
        """Main method called by ETL pipeline"""
        programmes = []
        
        try:
            # Your scraping logic here
            programmes = self._fetch_programmes()
            
        except Exception as e:
            logger.error(f"Error in scraper: {e}")
        
        return programmes
    
    def _fetch_programmes(self) -> List[Dict]:
        """Implement your scraping logic"""
        # Return list of dictionaries with these keys:
        return [{
            'program_name': 'Programme Name',
            'institution': 'University Name', 
            'degree': 'B.Sc.|M.Sc.|Ph.D.',
            'language': 'English',
            'source_url': 'https://...',
            'tuition_fee': 0,
            'start_date': '',
            'tuition_period': 'semester'
        }]
```

### **Integration with ETL Pipeline:**
```python
# 1. Add import to etl_pipeline.py
from new_scraper import NewScraper

# 2. Add to __init__ method
self.new_scraper = NewScraper()

# 3. Add to extract_data method
data['new_source'] = self.new_scraper.scrape_english_programmes()
```

---

## 🎯 **Performance Optimization**

### **Current Performance:**
- DAAD API: ~0.7 seconds for 2,217 programmes
- ETL Transform: ~0.02 seconds
- Database Load: ~1.9 seconds
- **Total: ~2.5 seconds**

### **Optimization Opportunities:**
```python
# 1. Batch database inserts
# Current: Individual inserts
# Better: Bulk insert with pandas.to_sql()

# 2. Parallel scraping
# Current: Sequential scraper execution  
# Better: Concurrent.futures for parallel execution

# 3. Caching
# Add Redis for API response caching
# Cache institution lookups
```

---

## 📊 **Data Quality Checks**

### **Validation Rules:**
```python
# Programme validation
def validate_programme(prog):
    required_fields = ['program_name', 'institution', 'degree']
    return all(prog.get(field) for field in required_fields)

# English language detection
def is_english_programme(prog):
    language = prog.get('language', '').lower()
    return 'english' in language or 'englisch' in language
```

### **Quality Metrics:**
```sql
-- Check data quality
SELECT 
    COUNT(*) as total,
    COUNT(CASE WHEN program_name IS NOT NULL AND LENGTH(program_name) > 5 THEN 1 END) as valid_names,
    COUNT(CASE WHEN language LIKE '%English%' THEN 1 END) as english_programmes
FROM programmes;
```

---

## 🔐 **Security & Maintenance**

### **Security Considerations:**
- Database credentials in environment variables
- Rate limiting for web scraping
- Input validation for scraped data
- SQL injection prevention (using parameterized queries)

### **Regular Maintenance:**
```bash
# Update dependencies
pip install -r scrapers/requirements.txt --upgrade

# Clean old logs
find /tmp -name "*.log" -mtime +7 -delete

# Database maintenance
docker exec course-monitor-db psql -U course_user -d course_monitor -c "VACUUM ANALYZE;"
```

**This system is production-ready for DAAD data. Focus on fixing HRK and Accreditation scrapers to complete the multi-source vision.**
