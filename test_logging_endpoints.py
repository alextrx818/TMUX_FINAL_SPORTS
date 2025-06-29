#!/usr/bin/env python3
"""
Test script to verify each endpoint logs to its correct JSON file
Expected mapping:
- live.py -> logs/live/live.json
- details.py -> logs/details/details.json  
- odds.py -> logs/odds/odds.json
- teams.py -> logs/teams/teams.json
- competitions.py -> logs/competitions/competitions.json
- countries.py -> logs/countries/countries.json
"""

import os
import json
import asyncio
from datetime import datetime

def check_log_file(endpoint_name, expected_file):
    """Check if endpoint has correct log file and show recent entries"""
    print(f"\n{'='*60}")
    print(f"TESTING: {endpoint_name.upper()}.PY -> {expected_file}")
    print('='*60)
    
    if os.path.exists(expected_file):
        try:
            with open(expected_file, 'r') as f:
                logs = json.load(f)
            
            print(f"✅ Log file exists: {expected_file}")
            print(f"📊 Total log entries: {len(logs)}")
            
            if logs:
                recent_log = logs[0]  # Most recent (first in array)
                print(f"🕐 Most recent entry: {recent_log.get('timestamp', 'N/A')}")
                print(f"🎯 Endpoint: {recent_log.get('endpoint', 'N/A')}")
                print(f"✅ Status: {recent_log.get('status', 'N/A')}")
                
                # Verify endpoint name matches
                logged_endpoint = recent_log.get('endpoint', '')
                if logged_endpoint == endpoint_name:
                    print(f"✅ CORRECT: Endpoint name matches ({logged_endpoint})")
                else:
                    print(f"❌ ERROR: Expected '{endpoint_name}', found '{logged_endpoint}'")
                
                # Show request URL to verify correct API endpoint
                request = recent_log.get('request', {})
                url = request.get('url', 'N/A')
                print(f"🌐 API URL: {url}")
                
            else:
                print("⚠️  Log file is empty")
                
        except json.JSONDecodeError:
            print(f"❌ ERROR: {expected_file} contains invalid JSON")
        except Exception as e:
            print(f"❌ ERROR reading {expected_file}: {e}")
    else:
        print(f"❌ MISSING: {expected_file} does not exist")

def count_archive_files():
    """Count archive files in each endpoint directory"""
    print(f"\n{'='*60}")
    print("ARCHIVE FILE COUNTS")
    print('='*60)
    
    endpoints = ['live', 'details', 'odds', 'teams', 'competitions', 'countries']
    total_archive_files = 0
    
    for endpoint in endpoints:
        archive_dir = f"logs/{endpoint}/archive"
        if os.path.exists(archive_dir):
            archive_files = [f for f in os.listdir(archive_dir) if f.endswith('.json')]
            count = len(archive_files)
            total_archive_files += count
            print(f"{endpoint:12} archive files: {count}")
        else:
            print(f"{endpoint:12} archive dir: MISSING")
    
    print(f"{'Total':12} archive files: {total_archive_files}")
    
    if total_archive_files > 300:  # Reasonable threshold
        print(f"\n⚠️  WARNING: {total_archive_files} archive files detected!")
        print("This suggests excessive logging/archiving. Consider cleanup.")

def main():
    """Main test function"""
    print("🧪 ENDPOINT LOGGING VERIFICATION TEST")
    print(f"📅 Test run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test each endpoint -> log file mapping
    test_cases = [
        ('live', 'logs/live/live.json'),
        ('details', 'logs/details/details.json'),
        ('odds', 'logs/odds/odds.json'),
        ('teams', 'logs/teams/teams.json'),
        ('competitions', 'logs/competitions/competitions.json'),
        ('countries', 'logs/countries/countries.json')
    ]
    
    for endpoint_name, expected_file in test_cases:
        check_log_file(endpoint_name, expected_file)
    
    # Check archive file counts
    count_archive_files()
    
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print('='*60)
    print("✅ Each endpoint should log to its own named JSON file")
    print("✅ Primary logs: live.json, details.json, odds.json, teams.json, competitions.json, countries.json")
    print("✅ Archive rotation happens after 50 entries per endpoint")
    print("✅ Archive files are timestamped and stored in archive/ subdirectories")

if __name__ == "__main__":
    main()