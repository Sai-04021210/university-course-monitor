#!/bin/bash
# Manual ETL runner script

echo "Starting ETL pipeline for Course Monitor..."
echo "Timestamp: $(date)"

# Run the ETL pipeline inside the container
docker-compose exec -T nodered python3 /opt/scrapers/etl_pipeline.py

if [ $? -eq 0 ]; then
    echo "✅ ETL pipeline completed successfully"
else
    echo "❌ ETL pipeline failed"
    exit 1
fi