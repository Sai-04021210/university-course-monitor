# German University Course Monitor

> **WARNING: IMPORTANT: RESTRICTED USE LICENSE**
>
> This repository is under a **restricted use license**. Viewing and studying the code is permitted for educational purposes, but **commercial use, deployment, and redistribution require explicit written permission**.
>
> **Before using this code:** Please read the [LICENSE](./docs/legal/LICENSE) file and submit a [Usage Request](../../issues/new/choose) if you plan to use this beyond educational study.

A comprehensive monitoring system that tracks English-taught degree programmes at German universities using official data sources. The system provides automated data collection, processing, and visualization through a modern ETL pipeline and dashboard interface.

##  Current Status (October 2025)

** PRODUCTION READY** - Fully Dockerized with real data

### **Live Data:**
- **Over 3,000+ English-taught programmes** from **250+ German universities**
- **Official DAAD & HRK integration** (real-time data)
- **Complete ETL pipeline** (automated data processing)
- **PostgreSQL database** with structured data
- **Node-RED dashboard** for interactive visualization

##  Working Features

- **DAAD API Integration**: Real-time data from official German Academic Exchange Service
- **HRK Scraper**: Web scraping from German Higher Education Compass
- **English Language Filtering**: Automatically identifies English-taught programmes
- **Data Validation**: Quality checks and duplicate removal
- **PostgreSQL Storage**: Structured database with proper relationships
- **ETL Pipeline**: Extract, Transform, Load with comprehensive error handling
- **Docker Deployment**: Fully containerized infrastructure (no local Python setup needed)
- **Node-RED Dashboard**: Interactive data visualization with filters

##  Quick Start

### **Prerequisites:**
- Docker and Docker Compose installed
- 4GB RAM minimum
- That's it! No Python installation needed - everything runs in Docker

### **1. Clone and Start:**
```bash
git clone <repository-url>
cd university-course-monitor

# Start all services (PostgreSQL + Node-RED)
docker compose up -d

# Wait for containers to be healthy (~30 seconds)
docker compose ps
```

### **2. Run Data Collection:**

**Important:** All Python scripts now run **inside Docker containers**. You don't need Python installed locally.

```bash
# Run ETL pipeline inside Docker (scrapes DAAD + HRK data)
docker exec node-red python3 /opt/scrapers/etl_pipeline.py

# Expected output:
# INFO - Extracted 2317 programmes from DAAD
# INFO - Extracted 1000 programmes from HRK
# INFO - Transformed 3000+ unique programmes
# INFO - Data loading completed: {'new_programmes': 3000, ...}

# This takes ~2-5 minutes depending on HRK page limit
```

**Monitor ETL Progress:**
```bash
# Watch ETL progress in real-time
docker exec node-red tail -f /tmp/etl.log

# Check specific progress updates
docker exec node-red tail -f /tmp/etl.log | grep -E "Progress:|Page.*Found|completed"

# Check database count (while ETL is running or after)
docker exec course-monitor-db psql -U course_user -d course_monitor -c "SELECT COUNT(*) FROM programmes;"
```

### **3. Reload Dashboard:**

**After ETL completes**, restart Node-RED to load the data:

```bash
# Restart Node-RED to reload dashboard with new data
docker restart node-red

# Wait 10-15 seconds for Node-RED to restart
```

### **4. Access Dashboard:**
- **Node-RED Dashboard**: [http://localhost:1882/ui](http://localhost:1882/ui) ← **Main Dashboard**
- **Node-RED Editor**: [http://localhost:1882](http://localhost:1882) (for flow editing)
- **Database Access**: `docker exec -it course-monitor-db psql -U course_user -d course_monitor`

##  Working with Python Scripts

### **All scripts run inside Docker - no local Python needed!**

#### **Run ETL Pipeline:**
```bash
# Full ETL pipeline (Extract → Transform → Load)
docker exec node-red python3 /opt/scrapers/etl_pipeline.py
```

#### **Test Individual Scrapers:**
```bash
# Test DAAD scraper only (fast - API call)
docker exec node-red python3 /opt/scrapers/daad_scraper.py

# Test HRK scraper only (slower - web scraping)
docker exec node-red python3 /opt/scrapers/hrk_scraper.py
```

#### **Modify Scrapers:**

If you need to modify the Python scripts:

```bash
# 1. Edit the file locally
nano scrapers/hrk_scraper.py  # or use your preferred editor

# 2. Copy updated file to Docker container
docker cp scrapers/hrk_scraper.py node-red:/opt/scrapers/hrk_scraper.py

# 3. Run the ETL again
docker exec node-red python3 /opt/scrapers/etl_pipeline.py

# 4. Restart Node-RED to see changes in dashboard
docker restart node-red
```

#### **Adjust HRK Scraping Limit:**

The HRK scraper is configured to scrape 10 pages (1,000 programmes) by default for testing. To change this:

```python
# Edit scrapers/hrk_scraper.py line ~175
max_pages = 10  # Change to 50 for 5,000 progs, 100 for 10,000+, or 223 for all

# Then copy to Docker and run ETL
docker cp scrapers/hrk_scraper.py node-red:/opt/scrapers/hrk_scraper.py
docker exec node-red python3 /opt/scrapers/etl_pipeline.py
```

##  Data Sources & Status

###  DAAD API (Working - Primary Source)
- **Source**: German Academic Exchange Service (Official)
- **API Endpoint**: `https://www2.daad.de/deutschland/studienangebote/international-programmes/api/solr/en/search.json`
- **Coverage**: 2,317 English-taught programmes from 220 universities
- **Update Frequency**: Real-time API access
- **Data Quality**: Official government source, validated
- **Performance**: Sub-second data extraction

###  HRK Hochschulkompass (Working)
- **Source**: German Higher Education Compass (Official)
- **Status**: Scraper is active and working
- **Coverage**: 22,292 total programmes (configurable via max_pages)
- **URL**: `https://www.hochschulkompass.de/studium/studiengangsuche/erweiterte-studiengangsuche`
- **Performance**: ~10 seconds per page (100 programmes/page)
- **Configuration**: `max_pages = 10` (default), increase for more data

###  Accreditation Council (Partially Working)
- **Source**: German Accreditation Agencies
- **Status**: Scraper template exists but needs research
- **Potential Coverage**: Programme validation and accreditation data
- **Required Fix**: 2-4 hours to research agencies and implement scrapers
- **Agencies**: ACQUIN, AQAS, ASIIN, FIBAA, ZEvA

### Data Quality & Validation

 **Implemented Validations:**
- English language detection and filtering
- Programme name and institution validation
- Duplicate detection and removal
- Data structure validation
- Source tracking and provenance
- UI element filtering (rejects invalid scraped data)

 **Quality Metrics:**
- 100% official data sources
- Automatic deduplication across sources
- Field validation (degree names up to 255 chars)

##  Architecture & Technical Stack

### **Core Technologies:**
- **Docker & Docker Compose**: Containerized infrastructure
- **Python 3.12**: ETL pipeline and data processing (runs in Docker)
- **PostgreSQL 15**: Structured data storage with proper schema
- **Node-RED 3.1**: Dashboard and workflow automation
- **Selenium + ChromeDriver**: Web scraping for HRK (Alpine Linux)
- **Requests + JSON**: API integration for DAAD

### **Data Processing Pipeline:**
```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐    ┌──────────────┐
│ DAAD API    │───▶│ Extract      │───▶│ Transform   │───▶│ PostgreSQL   │
│ (Working)   │    │ 2,317 progs  │    │ Dedupe      │    │ 3,000+ progs │
└─────────────┘    │              │    │ Validate    │    └──────────────┘
                   │              │    │ Normalize   │           │
┌─────────────┐    │              │    │             │           ▼
│ HRK Scraper │───▶│ (Working)    │───▶│             │    ┌──────────────┐
│ (Working)   │    │ 1,000+ progs │    │             │    │ Node-RED     │
└─────────────┘    │              │    │             │    │ Dashboard    │
                   │              │    │             │    └──────────────┘
┌─────────────┐    │              │    │             │
│ Accred.     │───▶│ (Partial)    │───▶│             │
│ (Partial)   │    │ 0 progs      │    │             │
└─────────────┘    └──────────────┘    └─────────────┘
```

### **Performance Metrics:**
- **DAAD Extraction**: 0.7 seconds (API call)
- **HRK Extraction**: ~10 seconds per page (100 programmes)
- **Transformation**: ~0.5 seconds (deduplication)
- **Loading**: ~2-5 seconds (PostgreSQL insert)
- **Full Pipeline**: 2-5 minutes (depends on HRK page limit)

### **Database Schema:**
```sql
-- Institutions table
institutions (
    inst_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(100),
    location VARCHAR(255),
    website VARCHAR(255),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
)

-- Programmes table
programmes (
    prog_id SERIAL PRIMARY KEY,
    inst_id INTEGER REFERENCES institutions(inst_id),
    program_name VARCHAR(500) NOT NULL,
    degree VARCHAR(255),  -- Updated to handle long German degree names
    language VARCHAR(100),
    tuition_fee DECIMAL(10,2) DEFAULT 0,
    tuition_period VARCHAR(20),
    start_date VARCHAR(50),
    source VARCHAR(50),
    source_url VARCHAR(500),
    accreditation_date DATE,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
)
```

##  Project Structure

```
university-course-monitor/
├── docker-compose.yml           # Container orchestration
├── Dockerfile                   # Node-RED container with Python + Chrome
├── README.md                    # This documentation
├── config/
│   └── database/
│       └── init.sql            # PostgreSQL schema initialization
├── scrapers/                    # Python ETL pipeline (runs in Docker)
│   ├── requirements.txt         # Python dependencies (auto-installed)
│   ├── etl_pipeline.py         # Main ETL orchestrator
│   ├── daad_scraper.py         # DAAD API scraper ( working)
│   ├── hrk_scraper.py          # HRK scraper ( working, configurable)
│   └── accreditation_scraper.py # Accreditation scraper ( partial)
└── workspace/                   # Node-RED data directory
    ├── flows.json              # Dashboard configuration
    └── node_modules/           # Node-RED dependencies
```

##  Dashboard & Usage

### **Node-RED Dashboard (http://localhost:1882/ui)**
- **System Statistics**: Total courses and universities with gauges
- **University Filters**: Filter by degree type, tuition fee, language
- **University Selector**: Browse courses by specific university
- **Course Listings**: Detailed table with programme information
- **Data Sources Info**: Status of DAAD, HRK, and other sources

### **Dashboard Features:**
- Filter by degree type (Bachelor's, Master's, PhD)
- Filter by tuition (Free, Up to €500, Affordable)
- Filter by language (English, German, Mixed)
- Select specific university to view all their programmes
- Real-time statistics and counts

### **Database Access:**
```bash
# Connect to PostgreSQL
docker exec -it course-monitor-db psql -U course_user -d course_monitor

# Sample queries
SELECT COUNT(*) FROM programmes;
SELECT COUNT(DISTINCT inst_id) FROM programmes;
SELECT degree, COUNT(*) FROM programmes GROUP BY degree ORDER BY COUNT(*) DESC;
SELECT i.name, COUNT(*) as course_count FROM programmes p
  JOIN institutions i ON p.inst_id = i.inst_id
  GROUP BY i.name ORDER BY COUNT(*) DESC LIMIT 10;
```

##  Configuration & Environment

### **Environment Variables (.env):**
```bash
# Database configuration
POSTGRES_DB=course_monitor
POSTGRES_USER=course_user
POSTGRES_PASSWORD=course_monitor_secure_password_2024
POSTGRES_HOST=postgres

# Node-RED version
NODERED_VERSION=3.1.10-18

# Timezone
TZ=Europe/Berlin
```

### **Docker Compose Services:**
```yaml
services:
  postgres:     # PostgreSQL database (port 5432)
  nodered:      # Node-RED + Python + Chrome (port 1882 → 1880)
```

### **Ports:**
- `1882`: Node-RED Dashboard & Editor (mapped to container port 1880)
- `5432`: PostgreSQL Database (for external connections)

##  Common Operations

### **Stop Services:**
```bash
docker compose down
```

### **View Logs:**
```bash
# Node-RED logs
docker logs node-red

# PostgreSQL logs
docker logs course-monitor-db

# ETL logs (while ETL is running)
docker exec node-red tail -f /tmp/etl.log
```

### **Reset Database:**
```bash
# Stop containers
docker compose down

# Remove database volume
docker volume rm university-course-monitor_postgres_data

# Start fresh
docker compose up -d

# Run ETL again
docker exec node-red python3 /opt/scrapers/etl_pipeline.py
docker restart node-red
```

### **Update Scrapers:**
```bash
# Edit locally
nano scrapers/etl_pipeline.py

# Copy to container
docker cp scrapers/etl_pipeline.py node-red:/opt/scrapers/

# Run ETL
docker exec node-red python3 /opt/scrapers/etl_pipeline.py
```

##  Troubleshooting

### **Dashboard is Empty:**
1. Check if ETL ran successfully:
   ```bash
   docker exec course-monitor-db psql -U course_user -d course_monitor -c "SELECT COUNT(*) FROM programmes;"
   ```
2. If count is 0, run ETL:
   ```bash
   docker exec node-red python3 /opt/scrapers/etl_pipeline.py
   ```
3. Restart Node-RED to reload data:
   ```bash
   docker restart node-red
   ```

### **Database Connection Errors:**
```bash
# Check if containers are running
docker compose ps

# Both should show "healthy" status
# If not, check logs:
docker logs course-monitor-db
docker logs node-red

# Restart if needed
docker compose restart
```

### **ETL Pipeline Errors:**
```bash
# Check ETL logs
docker exec node-red tail -50 /tmp/etl.log

# Common issues:
# 1. Database schema mismatch → Run reset database steps above
# 2. Chrome/Selenium issues → Check if chromedriver is working:
docker exec node-red which chromedriver
docker exec node-red chromium-browser --version
```

### **Degree Field Too Long Error:**
If you see `StringDataRightTruncation` error:
```bash
# Fix: Increase degree field size
docker exec course-monitor-db psql -U course_user -d course_monitor -c "ALTER TABLE programmes ALTER COLUMN degree TYPE VARCHAR(255);"

# Then run ETL again
docker exec node-red python3 /opt/scrapers/etl_pipeline.py
```

##  Known Issues & Future Work

### ** Issues to Fix:**
1. **Accreditation Scraper**: Needs research and implementation (2-4 hours)
2. **HRK Scraping Speed**: Takes ~10 seconds per page (use smaller max_pages for testing)

### ** Future Enhancements:**
- **Automated Scheduling**: Cron jobs or Node-RED scheduled flows
- **REST API**: External data access endpoints
- **Change Detection**: Track programme additions/removals over time
- **Enhanced Filtering**: More sophisticated search capabilities
- **Data Enrichment**: Application deadlines, requirements, fees
- **Email Notifications**: Alert when new programmes are added

##  Contributing

### **Priority Contributions:**
1. **Improve HRK scraper performance** (parallel scraping)
2. **Implement accreditation scraper** (research German agencies)
3. **Add automated scheduling** (cron jobs or Node-RED flows)
4. **Enhance data validation** (more quality checks)

### **Development Setup:**
```bash
git clone <repository-url>
cd university-course-monitor

# Start all services
docker compose up -d

# Run ETL
docker exec node-red python3 /opt/scrapers/etl_pipeline.py

# Restart Node-RED
docker restart node-red

# Access dashboard
open http://localhost:1882/ui
```

##  License

Educational and research use. Data sourced from official German government APIs (DAAD) and educational institutions.

---

**Status**:  Production ready with DAAD and HRK data | Fully Dockerized
**Last Updated**: October 24, 2025
**Data Sources**: Official DAAD API (2,317 programmes) + HRK Scraper (configurable)
**Architecture**: Docker Compose | PostgreSQL | Node-RED | Python 3.12 | Selenium
