# Automation & Scheduling Guide

## 🤖 **Current Automation Status**

Your system is **partially automated** with the following capabilities:

### ✅ **What's Working Automatically**
- **ETL Pipeline**: Complete automated data processing
- **Data Validation**: Automatic filtering and deduplication
- **Database Updates**: Automatic insertion and updates
- **Error Handling**: Robust error recovery and logging
- **Docker Integration**: Containerized execution environment

### ⚠️ **What Needs Manual Setup**
- **Scheduled Execution**: Currently requires manual trigger
- **Node-RED Flows**: Need configuration for automatic scheduling
- **Monitoring Alerts**: Optional notification system

## 🕐 **Setting Up Automatic Scheduling**

### **Option 1: Node-RED Scheduler (Recommended)**

1. **Access Node-RED Dashboard**
   ```bash
   open http://localhost:1880
   ```

2. **Create Scheduled Flow**
   - Drag an "inject" node (for timing)
   - Set repeat interval (daily/weekly)
   - Connect to "exec" node
   - Configure command: `python3 /opt/scrapers/etl_pipeline.py`

3. **Example Flow Configuration**
   ```json
   {
     "inject": {
       "repeat": "86400",  // 24 hours in seconds
       "crontab": "0 2 * * *"  // Daily at 2 AM
     },
     "exec": {
       "command": "python3 /opt/scrapers/etl_pipeline.py",
       "cwd": "/opt/scrapers"
     }
   }
   ```

### **Option 2: System Cron Job**

1. **Create Cron Script**
   ```bash
   # Create automation script
   cat > /usr/local/bin/course-monitor-update.sh << 'EOF'
   #!/bin/bash
   cd /path/to/university-course-monitor
   docker exec node-red python3 /opt/scrapers/etl_pipeline.py
   EOF
   
   chmod +x /usr/local/bin/course-monitor-update.sh
   ```

2. **Add to Crontab**
   ```bash
   # Edit crontab
   crontab -e
   
   # Add daily run at 2 AM
   0 2 * * * /usr/local/bin/course-monitor-update.sh >> /var/log/course-monitor.log 2>&1
   ```

### **Option 3: Docker Compose with Scheduler**

Add a scheduler service to your `docker-compose.yml`:

```yaml
services:
  scheduler:
    image: mcuadros/ofelia:latest
    depends_on:
      - node-red
    command: daemon --docker
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
    labels:
      ofelia.job-exec.course-monitor.schedule: "0 2 * * *"
      ofelia.job-exec.course-monitor.container: "node-red"
      ofelia.job-exec.course-monitor.command: "python3 /opt/scrapers/etl_pipeline.py"
```

## 📅 **Recommended Scheduling Strategy**

### **Optimal Schedule**
```
┌─────────────┬─────────────┬─────────────┬─────────────┐
│   Source    │ Frequency   │    Time     │   Reason    │
├─────────────┼─────────────┼─────────────┼─────────────┤
│ DAAD API    │ Daily       │ 2:00 AM     │ Lightweight │
│ HRK Scraper │ Weekly      │ Sunday 3:00 │ Resource    │
│ Full ETL    │ Weekly      │ Sunday 4:00 │ Complete    │
│ Health Check│ Hourly      │ Every hour  │ Monitoring  │
└─────────────┴─────────────┴─────────────┴─────────────┘
```

### **Cron Schedule Examples**
```bash
# Daily DAAD update at 2 AM
0 2 * * * docker exec node-red python3 /opt/scrapers/daad_scraper.py

# Weekly full ETL on Sunday at 3 AM
0 3 * * 0 docker exec node-red python3 /opt/scrapers/etl_pipeline.py

# Monthly deep clean on 1st at 1 AM
0 1 1 * * docker exec node-red python3 /opt/scrapers/maintenance.py
```

## 🔔 **Monitoring & Notifications**

### **Log Monitoring**
```bash
# Monitor ETL logs in real-time
docker exec node-red tail -f /tmp/etl.log

# Check for errors
docker exec node-red grep -i error /tmp/etl.log

# Monitor system resources
docker stats
```

### **Email Notifications (Optional)**
Add to Node-RED flow for email alerts:

```javascript
// Email notification node
if (msg.payload.includes("ERROR")) {
    msg.to = "admin@yourdomain.com";
    msg.subject = "Course Monitor Alert";
    msg.payload = "ETL Pipeline encountered an error";
    return msg;
}
```

## 📊 **Performance Optimization**

### **Resource Management**
- **Memory**: HRK scraper uses ~2GB RAM during execution
- **CPU**: Chrome browser automation is CPU-intensive
- **Disk**: Database grows ~100MB per full ETL run
- **Network**: Respectful delays prevent rate limiting

### **Optimization Tips**
1. **Schedule during off-peak hours** (2-4 AM)
2. **Limit HRK to 50 pages** for faster execution
3. **Use SSD storage** for database performance
4. **Monitor Docker resource limits**

## 🛠️ **Manual Operations**

### **On-Demand Updates**
```bash
# Full ETL pipeline
docker exec node-red python3 /opt/scrapers/etl_pipeline.py

# Individual scrapers
docker exec node-red python3 /opt/scrapers/daad_scraper.py
docker exec node-red python3 /opt/scrapers/hrk_scraper.py

# Database maintenance
docker exec postgres psql -U course_user -d course_monitor -c "VACUUM ANALYZE;"
```

### **System Maintenance**
```bash
# Update Docker images
docker compose pull && docker compose up -d

# Clean up old data
docker exec postgres psql -U course_user -d course_monitor -c "DELETE FROM programmes WHERE updated_at < NOW() - INTERVAL '6 months';"

# Backup database
docker exec postgres pg_dump -U course_user course_monitor > backup_$(date +%Y%m%d).sql
```

## 🚨 **Troubleshooting Automation**

### **Common Issues**

1. **Chrome Driver Fails**
   ```bash
   # Check Chrome installation
   docker exec node-red chromium-browser --version
   
   # Restart container
   docker compose restart node-red
   ```

2. **Database Connection Issues**
   ```bash
   # Check database status
   docker exec postgres pg_isready -U course_user
   
   # Restart database
   docker compose restart postgres
   ```

3. **Memory Issues**
   ```bash
   # Check memory usage
   docker stats --no-stream
   
   # Increase Docker memory limit
   # Edit Docker Desktop settings or docker-compose.yml
   ```

### **Recovery Procedures**
1. **Failed ETL Run**: Check logs, restart containers, retry
2. **Data Corruption**: Restore from backup, re-run ETL
3. **System Overload**: Reduce scraping frequency, optimize queries

## 📈 **Monitoring Dashboard**

### **Key Metrics to Track**
- ETL execution time (target: <30 minutes)
- Success rate (target: >95%)
- Data freshness (last update timestamp)
- System resource usage
- Error frequency

### **Health Check Script**
```bash
#!/bin/bash
# health-check.sh
echo "=== Course Monitor Health Check ==="
echo "Docker containers:"
docker compose ps

echo "Database connection:"
docker exec postgres pg_isready -U course_user

echo "Last ETL run:"
docker exec postgres psql -U course_user -d course_monitor -c "SELECT MAX(updated_at) FROM programmes;"

echo "Programme count:"
docker exec postgres psql -U course_user -d course_monitor -c "SELECT COUNT(*) FROM programmes WHERE is_active=true;"
```

---

**Next Steps for Full Automation:**
1. Choose your preferred scheduling method
2. Configure Node-RED flows or cron jobs
3. Set up monitoring and alerts
4. Test the automated schedule
5. Monitor performance and adjust as needed

Your system is **production-ready** and just needs the final scheduling configuration!
