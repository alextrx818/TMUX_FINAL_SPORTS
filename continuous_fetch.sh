#!/bin/bash

# Continuous Sports API Pipeline Fetcher
# Runs the complete pipeline every 60+ seconds minimum spacing
# Usage: ./continuous_fetch.sh

echo "🚀 Starting Continuous Sports API Pipeline..."
echo "📊 Minimum 60 seconds between fetches"
echo "🔄 Pipeline will run indefinitely until killed (Ctrl+C)"
echo "📂 Logs will be stored in logs/ directory"
echo ""

# Counter for tracking runs
RUN_COUNT=0

# Function to handle cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping continuous pipeline..."
    echo "📈 Total runs completed: $RUN_COUNT"
    echo "👋 Goodbye!"
    exit 0
}

# Trap Ctrl+C (SIGINT) and SIGTERM
trap cleanup SIGINT SIGTERM

while true; do
    RUN_COUNT=$((RUN_COUNT + 1))
    
    echo "==============================================="
    echo "🔥 RUN #$RUN_COUNT - $(date '+%m/%d/%Y %I:%M:%S %p')"
    echo "==============================================="
    
    # Record start time
    START_TIME=$(date +%s)
    
    # Run the complete pipeline starting with live.py
    echo "▶️  Starting pipeline..."
    python3 live.py
    
    # Record end time
    END_TIME=$(date +%s)
    DURATION=$((END_TIME - START_TIME))
    
    echo ""
    echo "✅ Pipeline run #$RUN_COUNT completed in ${DURATION} seconds"
    
    # Calculate sleep time (minimum 60 seconds)
    if [ $DURATION -lt 60 ]; then
        SLEEP_TIME=$((60 - DURATION))
        echo "⏱️  Waiting ${SLEEP_TIME} seconds to maintain 60-second minimum spacing..."
        sleep $SLEEP_TIME
    else
        echo "⚡ Pipeline took ${DURATION}s (>60s), starting next run immediately..."
    fi
    
    echo "🔄 Next run starting now..."
    echo ""
done