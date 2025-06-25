# Contributing to University Course Monitor

Thank you for your interest in contributing! This project welcomes contributions while maintaining usage restrictions.

## 🚀 Quick Start

1. **Read the [License](./docs/legal/LICENSE)** - Understand usage terms
2. **Check [Open Issues](../../issues)** - See what needs work
3. **Submit [Usage Request](../../issues/new/choose)** - If needed for your contribution type
4. **Fork & Submit PR** - Follow standard GitHub workflow

## 🎯 Contribution Types

### **✅ Always Welcome (No Permission Needed)**
- 🐛 **Bug fixes** - Fix broken functionality
- 📝 **Documentation** - Improve docs, comments, README
- 🧪 **Tests** - Add test coverage
- 🎨 **Code quality** - Refactoring, formatting, linting
- 💡 **Feature suggestions** - Ideas and proposals (via issues)

### **⚠️ Permission Required**
- 🚀 **New features** - Major functionality additions
- 🔧 **Architecture changes** - Significant structural modifications
- 📊 **Data source additions** - New scraping targets
- 🌐 **API modifications** - External interface changes

## 📝 Contribution Process

### **1. Bug Fixes & Minor Improvements**
```bash
# Standard GitHub workflow
1. Fork the repository
2. Create feature branch: git checkout -b fix/issue-description
3. Make changes and test
4. Submit pull request
5. Await review and merge
```

### **2. Major Features**
```bash
# Requires pre-approval
1. Create issue describing the feature
2. Wait for maintainer feedback
3. Submit usage request if required
4. Get written approval
5. Follow standard PR process
```

## 🛠️ Development Setup

### **Prerequisites**
- Docker & Docker Compose
- Python 3.11+
- Node.js 16+ (for Node-RED)

### **Local Development**
```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/university-course-monitor.git
cd university-course-monitor

# Start development environment
docker compose up -d --build

# Run tests (when available)
# python -m pytest tests/

# Access services
# Node-RED: http://localhost:1880
# Database: localhost:5432
```

## 📊 Project Structure

```
university-course-monitor/
├── README.md                 # Main project documentation
├── LICENSE                   # License summary (full text in docs/)
├── CONTRIBUTING.md          # This file
├── docker-compose.yml       # Service orchestration
├── Dockerfile              # Container definition
├── .env                    # Environment configuration
├── config/                 # Configuration files
│   └── database/           # Database initialization
├── docs/                   # Documentation
│   ├── legal/             # License and legal docs
│   ├── policies/          # Usage and security policies
│   └── templates/         # Issue/PR templates
├── scrapers/              # Data extraction scripts
│   ├── etl_pipeline.py    # Main ETL orchestrator
│   ├── daad_scraper.py    # DAAD API integration
│   ├── hrk_scraper.py     # HRK website scraper
│   └── requirements.txt   # Python dependencies
├── scripts/               # Utility scripts
│   └── run-etl.sh        # Manual ETL execution
├── tests/                 # Test suite (future)
└── workspace/            # Node-RED workspace
    ├── flows.json        # Node-RED flow definitions
    └── settings.js       # Node-RED configuration
```

## 🧪 Testing Guidelines

### **Before Submitting PR**
- [ ] Code runs without errors
- [ ] Docker containers build successfully
- [ ] ETL pipeline executes cleanly
- [ ] No hardcoded credentials or sensitive data
- [ ] Documentation updated if needed
- [ ] Follows existing code style

### **Testing Checklist**
```bash
# Build and test containers
docker compose down
docker compose up -d --build

# Test ETL pipeline
docker compose exec nodered python3 /opt/scrapers/etl_pipeline.py

# Verify Node-RED loads
curl http://localhost:1880/ui

# Check database connectivity
docker compose exec postgres psql -U course_user -d course_monitor -c "\dt"
```

## 📋 Code Standards

### **Python Code**
- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Include docstrings for functions/classes
- Handle errors gracefully with logging
- No hardcoded values - use environment variables

### **Documentation**
- Update README.md if adding features
- Include inline comments for complex logic
- Update API documentation if applicable
- Keep documentation current with code changes

### **Commit Messages**
```
Format: <type>(<scope>): <description>

Examples:
fix(scrapers): handle DAAD API timeout errors
feat(etl): add data validation layer
docs(readme): update installation instructions
refactor(database): optimize query performance
```

## 🔍 Review Process

### **What We Look For**
- ✅ **Functionality** - Does it work as intended?
- ✅ **Quality** - Is the code well-written and maintainable?
- ✅ **Security** - Are there any security concerns?
- ✅ **Compatibility** - Does it work with existing system?
- ✅ **Documentation** - Is it properly documented?

### **Review Timeline**
- **Simple fixes**: 1-3 days
- **Feature additions**: 3-7 days
- **Major changes**: 1-2 weeks

## 🎖️ Recognition

Contributors will be:
- Listed in repository credits
- Mentioned in release notes
- Given appropriate GitHub repository permissions
- Considered for collaboration opportunities

## 📞 Questions?

- **General questions**: Create an issue with "question" label
- **Technical support**: Check [docs/system_analysis_and_fixes.md](./docs/system_analysis_and_fixes.md)
- **Legal/licensing**: See [docs/legal/LICENSE](./docs/legal/LICENSE)
- **Security concerns**: Follow [Security Policy](./docs/policies/SECURITY.md)

---

**Thank you for contributing to making university education more accessible! 🎓**