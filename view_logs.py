#!/usr/bin/env python3

# ========================================
# CENTRALIZED LOGGING SYSTEM REMOVAL NOTE
# ========================================
# This project previously used a centralized logging system with shared configuration files
# (logging_utils.py, loggingconfig.py, etc.) that was removed due to path confusion and
# complexity. Each endpoint file now contains its own independent, hardcoded logging logic
# that is specific to that file's requirements. No centralized logging imports remain.
# ========================================

"""
Log viewer utility for API endpoint logs - simplified to work with independent logging
View basic log files for each endpoint (hardcoded to each file)
"""

import json
import os

def view_endpoint_logs(endpoint_name: str):
    """View basic log info for a specific endpoint (independent logging only)"""
    log_file = f"logs/{endpoint_name}/{endpoint_name}.json"
    
    print(f"\n📊 {endpoint_name.upper()} ENDPOINT LOGS")
    print("=" * 40)
    
    if os.path.exists(log_file):
        try:
            with open(log_file, 'r') as f:
                data = json.load(f)
            
            if isinstance(data, dict):
                # Check for accumulating log format (like live.py)
                if "fetch_history" in data:
                    fetch_count = len(data["fetch_history"])
                    last_fetch = data["log_metadata"]["last_fetch"] if "log_metadata" in data else "Unknown"
                    print(f"Total fetches: {fetch_count}")
                    print(f"Last fetch: {last_fetch}")
                # Check for API response format
                elif "api_response" in data:
                    print("Contains API response data")
                else:
                    print("Log file exists with custom format")
            elif isinstance(data, list):
                print(f"Contains {len(data)} log entries")
            else:
                print("Log file exists")
                
        except Exception as e:
            print(f"Error reading log file: {e}")
    else:
        print("No logs found")

def main():
    """Show logs for all endpoints"""
    endpoints = ['live', 'details', 'odds', 'teams', 'competitions', 'countries']
    
    print("🔍 API ENDPOINT LOGGING SUMMARY (Independent Logging)")
    print("=" * 50)
    
    for endpoint in endpoints:
        view_endpoint_logs(endpoint)

if __name__ == "__main__":
    main()