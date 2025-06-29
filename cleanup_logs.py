#!/usr/bin/env python3
"""
Cleanup script to remove excessive archive log files
Keeps only the most recent 10 archive files per endpoint
"""

import os
import glob
from datetime import datetime

def cleanup_archive_logs():
    """Clean up excessive archive log files"""
    endpoints = ['live', 'details', 'odds', 'teams', 'competitions', 'countries']
    total_removed = 0
    
    print("🧹 CLEANING UP EXCESSIVE ARCHIVE LOG FILES")
    print("=" * 60)
    
    for endpoint in endpoints:
        archive_dir = f"logs/{endpoint}/archive"
        
        if not os.path.exists(archive_dir):
            print(f"{endpoint:12}: No archive directory")
            continue
            
        # Get all JSON files in archive directory
        archive_files = glob.glob(f"{archive_dir}/*.json")
        
        if len(archive_files) <= 10:
            print(f"{endpoint:12}: {len(archive_files)} files (keeping all)")
            continue
        
        # Sort by modification time (newest first)
        archive_files.sort(key=os.path.getmtime, reverse=True)
        
        # Keep only the 10 most recent files
        files_to_keep = archive_files[:10]
        files_to_remove = archive_files[10:]
        
        print(f"{endpoint:12}: {len(archive_files)} files -> keeping {len(files_to_keep)}, removing {len(files_to_remove)}")
        
        # Remove old files
        for file_path in files_to_remove:
            try:
                os.remove(file_path)
                total_removed += 1
            except Exception as e:
                print(f"  ❌ Error removing {file_path}: {e}")
    
    print("=" * 60)
    print(f"🗑️  Total files removed: {total_removed}")
    print("✅ Cleanup completed!")

def verify_primary_logs():
    """Verify primary log files are intact"""
    print("\n📋 VERIFYING PRIMARY LOG FILES")
    print("=" * 40)
    
    endpoints = [
        ('live', 'logs/live/live.json'),
        ('details', 'logs/details/details.json'),
        ('odds', 'logs/odds/odds.json'),
        ('teams', 'logs/teams/teams.json'),
        ('competitions', 'logs/competitions/competitions.json'),
        ('countries', 'logs/countries/countries.json')
    ]
    
    for endpoint, log_file in endpoints:
        if os.path.exists(log_file):
            size = os.path.getsize(log_file)
            print(f"{endpoint:12}: ✅ {size:,} bytes")
        else:
            print(f"{endpoint:12}: ❌ MISSING")

if __name__ == "__main__":
    cleanup_archive_logs()
    verify_primary_logs()
    
    print(f"\n📊 Final archive counts:")
    os.system("python3 test_logging_endpoints.py | grep 'archive files:'")