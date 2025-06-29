#!/bin/bash

# Keep Codespace Alive Script
# This script prevents idle timeout by running periodic activity

echo "🔄 Starting Keep-Alive for Codespace..."
echo "This will prevent idle timeout by running periodic commands"
echo "Press Ctrl+C to stop"

while true; do
    # Show current time and system status
    echo "⏰ $(date): Codespace active - $(uptime)"
    
    # Light system activity
    ls -la > /dev/null 2>&1
    
    # Wait 10 minutes before next ping
    sleep 600
done
