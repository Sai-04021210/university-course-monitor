# German University Course Monitor

A comprehensive Node-RED based monitoring system that tracks German university course offerings from multiple official sources, providing real-time updates and semester-based analytics for higher education programs.

## Overview

This system monitors **2,400+ international programs** from **285+ German universities** using official government APIs, providing automated course detection, semester-based tracking, and intuitive dashboard visualization.

## Features

- **Real-time Monitoring**: Automatic course detection every 4 hours
- **Multi-source Data**: Combines DAAD API + Hochschulkompass data
- **Comprehensive Coverage**: 285+ universities with detailed categorization
- **Semester Tracking**: Organized by Winter/Summer semester additions
- **Smart Detection**: Identifies new courses with application deadlines
- **Visual Dashboard**: Interactive tables with filtering and sorting
- **University Classification**: Technical, Applied Sciences, Arts/Music categories

## Quick Start

1. **Clone & Start**:
   ```bash
   git clone <repository-url>
   cd university-course-monitor
   docker compose up -d
   ```

2. **Access Dashboard**: [http://localhost:1880/ui](http://localhost:1880/ui)
3. **Configure**: Visit [http://localhost:1880](http://localhost:1880) for Node-RED editor

## Data Sources & Reliability

### DAAD API (Primary Source)
- **Source**: German Academic Exchange Service (Official)
- **Coverage**: 2,412+ international programs from 235+ universities
- **Update Frequency**: Live API, refreshed every 4 hours
- **Data Quality**: Government-maintained, high reliability
- **URL**: `https://www2.daad.de/deutschland/studienangebote/international-programmes/api/`

### Hochschulkompass (Secondary Source)
- **Source**: German Higher Education Compass (Official)
- **Coverage**: 50+ major German universities
- **Update Frequency**: Curated institutional data
- **Data Quality**: Official educational database
- **Focus**: Domestic programs and comprehensive university listings

### Data Validation Approach

1. **Official Sources Only**: All data comes from German government/institutional APIs
2. **Cross-Reference Validation**: Multiple sources verify university information
3. **Automated Quality Checks**: Real-time validation of data structure and completeness
4. **Change Detection**: Smart algorithms identify genuine new course additions
5. **Semester Context**: Courses are categorized by appropriate academic semesters

## Architecture & Methodology

### Technical Stack
- **Node-RED**: Workflow automation and API orchestration
- **Docker**: Containerized deployment for consistency
- **Real-time APIs**: Live data feeds from official sources
- **Responsive Dashboard**: Modern web interface with mobile support

### Data Processing Pipeline
```
DAAD API ──┐
           ├── Data Processing ──→ Validation ──→ Semester Classification ──→ Dashboard
Hochschul──┘                      ↓
Kompass                      Change Detection ──→ New Course Alerts
```

### Update Methodology
1. **Scheduled Polling**: Every 4 hours automatic data refresh
2. **Intelligent Comparison**: New course detection using unique identifiers
3. **Semester Attribution**: Automatic semester assignment based on timing
4. **Data Persistence**: Local database maintains historical data
5. **Real-time Updates**: Dashboard reflects changes immediately

## Project Structure

```
university-course-monitor/
├── docker-compose.yml     # Container orchestration
├── Dockerfile            # Node-RED container setup
├── package.json          # Dependencies and configuration
├── README.md             # This documentation
└── workspace/            # Node-RED data directory
    ├── flows.json        # Main workflow configuration
    ├── flows_cred.json   # Encrypted credentials
    ├── settings.js       # Node-RED runtime settings
    └── course_database.json # Persistent course data
```

## Dashboard Features

### Main Dashboard
- **Live Statistics**: Total courses and universities
- **University Table**: Full list with categorization
- **Last Updated**: Real-time data freshness indicator
- **Data Sources**: Transparency panel showing source information

### New Courses Tab
- **Semester View**: Courses organized by Winter/Summer semesters
- **University Focus**: Which institutions are adding programs
- **Course Details**: Actual program names and descriptions
- **Scrollable Interface**: Full-screen table with comprehensive data

## Configuration

### Environment Variables
```bash
NODERED_VERSION=3.1.10-18  # Node-RED version
```

### API Configuration
- **DAAD API**: No authentication required (public API)
- **Hochschulkompass**: Curated data integration
- **Update Interval**: 4-hour cycles (configurable in Node-RED)

## Data Categories

### University Types
- **Technical Universities**: TU Munich, RWTH Aachen, KIT Karlsruhe
- **Universities of Applied Sciences**: Hochschulen across Germany
- **Traditional Universities**: LMU Munich, Heidelberg, Humboldt Berlin
- **Arts/Music Colleges**: Specialized creative institutions
- **Public Administration**: Government-focused institutions

### Program Types
- **Master's Programs**: MSc, MA, MEng degrees
- **International Programs**: English-taught courses
- **Research Programs**: PhD and doctoral opportunities
- **Professional Programs**: Industry-focused specializations

## Deployment

### Development
```bash
docker compose up -d
# Access: http://localhost:1880/ui
```

### Production
1. **Configure Environment**: Set production URLs and credentials
2. **Scale Resources**: Adjust container resources based on usage
3. **Monitor Logs**: Track API performance and data quality
4. **Backup Data**: Regular exports of course database

## Monitoring & Maintenance

### Health Checks
- **API Connectivity**: Automatic validation of data sources
- **Data Freshness**: Alerts for stale or missing data
- **System Performance**: Container resource monitoring

### Data Quality Assurance
- **Source Validation**: Verify API responses and data structure
- **Duplicate Detection**: Prevent redundant course entries
- **Semester Accuracy**: Validate timing-based course classification

## Contributing

1. **Fork the repository**
2. **Test changes locally** using Docker
3. **Validate data sources** ensure no breaking changes
4. **Submit pull request** with detailed description

## License

This project monitors publicly available educational data from official German government sources. All data remains property of respective institutions.

## Support

- **Issues**: Report bugs via GitHub issues
- **Documentation**: Check Node-RED official documentation
- **API Status**: Monitor DAAD and Hochschulkompass service status

---

**Last Updated**: June 2025 | **Version**: 2.0 | **Status**: Production Ready