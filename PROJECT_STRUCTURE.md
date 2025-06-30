# Project Structure

This document outlines the professional organization of the University Course Monitor repository.

##  Directory Structure

```
university-course-monitor/
├──  README.md                    # Main project overview and quick start
├──  LICENSE                      # License summary (full text in docs/legal/)
├──  CONTRIBUTING.md              # Contribution guidelines and process
├──  PROJECT_STRUCTURE.md         # This file - project organization
├── docker-compose.yml           # Multi-container orchestration
├── Dockerfile                   # Container build definition
├── .env                         # Environment configuration
│
├──  .github/                     # GitHub-specific configurations
│   ├──  ISSUE_TEMPLATE/          # Issue templates for bug reports, features
│   │   └── usage-request.md        # Usage permission request template
│   └──  workflows/               # GitHub Actions automation
│       └── monitor-usage.yml       # Repository monitoring and notifications
│
├──  config/                      # Configuration files and settings
│   └──  database/                # Database configuration
│       └── init.sql                # PostgreSQL schema and initial data
│
├──  docs/                        # Comprehensive project documentation
│   ├──  README.md                # Documentation index and navigation
│   ├──  system_analysis_and_fixes.md # Technical analysis and status
│   ├──  legal/                   # Legal documents and licensing
│   │   └── LICENSE                 # Full restricted use license text
│   ├──  policies/                # Policies and guidelines
│   │   ├── SECURITY.md             # Security policy and violation reporting
│   │   └── USAGE_VERIFICATION.md   # Usage verification requirements
│   └──  templates/               # Documentation templates
│       └──  ISSUE_TEMPLATE/      # Backup of GitHub issue templates
│
├──  scrapers/                    # Data extraction and processing
│   ├── 🐍 etl_pipeline.py          # Main ETL orchestrator and data pipeline
│   ├── 🐍 daad_scraper.py          # DAAD API integration (working)
│   ├── 🐍 hrk_scraper.py           # HRK website scraper (needs fixes)
│   ├── 🐍 accreditation_scraper.py # Accreditation Council scraper (placeholder)
│   └──  requirements.txt         # Python dependencies
│
├──  scripts/                     # Utility and automation scripts
│   └──  run-etl.sh               # Manual ETL pipeline execution
│
├──  tests/                       # Test suite (future implementation)
│   └── (test files will go here)
│
└──  workspace/                   # Node-RED workspace and flows
    ├──  flows.json               # Node-RED flow definitions
    ├──  flows_cred.json          # Node-RED credentials (gitignored)
    ├──  settings.js              # Node-RED configuration
    └──  lib/                     # Node-RED libraries and modules
```

##  Design Principles

### **1. Separation of Concerns**
- **Source code** (`scrapers/`) - Data extraction logic
- **Configuration** (`config/`) - Environment and setup files  
- **Documentation** (`docs/`) - All project documentation
- **Infrastructure** (`docker-compose.yml`, `Dockerfile`) - Deployment setup
- **Automation** (`.github/`) - CI/CD and repository management

### **2. Professional Standards**
- **Clear naming** - Descriptive file and directory names
- **Logical grouping** - Related files organized together
- **Standard conventions** - Following GitHub and open-source best practices
- **Comprehensive docs** - Documentation for every component

### **3. Legal Protection**
- **License visibility** - License terms prominently displayed
- **Usage monitoring** - Automated tracking of repository activity
- **Permission process** - Clear workflow for usage requests
- **Policy enforcement** - Automated responses and notifications

## File Categories

### ** Core Functionality**
| File | Purpose | Status |
|------|---------|--------|
| `scrapers/etl_pipeline.py` | Main data processing pipeline | Working |
| `scrapers/daad_scraper.py` | DAAD API integration | Working |
| `scrapers/hrk_scraper.py` | HRK website scraper | Needs fixes |
| `config/database/init.sql` | Database schema | Working |

### Documentation
| File | Purpose | Audience |
|------|---------|----------|
| `README.md` | Project overview | Everyone |
| `docs/system_analysis_and_fixes.md` | Technical details | Developers |
| `docs/legal/LICENSE` | Usage terms | Users |
| `CONTRIBUTING.md` | Contribution guidelines | Contributors |

### Legal & Policy
| File | Purpose | Enforcement |
|------|---------|-------------|
| `docs/legal/LICENSE` | Full license terms | Legal binding |
| `docs/policies/SECURITY.md` | Security reporting | Policy |
| `docs/policies/USAGE_VERIFICATION.md` | Usage requirements | Automated |
| `.github/workflows/monitor-usage.yml` | Activity monitoring | Automated |

### ** Infrastructure**
| File | Purpose | Environment |
|------|---------|-------------|
| `docker-compose.yml` | Service orchestration | All |
| `Dockerfile` | Container definition | All |
| `.env` | Environment config | Local/Production |
| `scripts/run-etl.sh` | Manual execution | Operations |

##  Getting Started

### **For Users**
1. Read [README.md](./README.md) for project overview
2. Check [docs/legal/LICENSE](./docs/legal/LICENSE) for usage terms
3. Submit [Usage Request](../../issues/new/choose) if needed

### **For Contributors**
1. Read [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines
2. Check [docs/system_analysis_and_fixes.md](./docs/system_analysis_and_fixes.md) for technical details
3. Follow the development setup instructions

### **For Operators**
1. Use `docker-compose up -d --build` to start services
2. Run `scripts/run-etl.sh` for manual data updates
3. Access Node-RED at `http://localhost:1880/ui`

## Support

- **Documentation**: Check `docs/` directory first
- **Issues**: Use GitHub Issues with appropriate templates  
- **Security**: Follow [Security Policy](./docs/policies/SECURITY.md)
- **Licensing**: See [Usage Verification](./docs/policies/USAGE_VERIFICATION.md)

---

This structure ensures professional organization, legal protection, and easy navigation for all stakeholders.