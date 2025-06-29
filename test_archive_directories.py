#!/usr/bin/env python3
"""
Comprehensive Archive Directory Analysis Script
Tests the current status of archive directories and checks for any code references
"""

import os
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple, Any

def check_archive_directories() -> Dict[str, Any]:
    """Check status of all archive directories"""
    
    print("🔍 CHECKING ARCHIVE DIRECTORIES STATUS")
    print("=" * 60)
    
    # Expected archive directories based on user's examples
    expected_archives = [
        '/workspaces/TMUX_FINAL_SPORTS/logs/competitions/archive',
        '/workspaces/TMUX_FINAL_SPORTS/logs/details/archive', 
        '/workspaces/TMUX_FINAL_SPORTS/logs/odds/archive',
        '/workspaces/TMUX_FINAL_SPORTS/logs/teams/archive',
        '/workspaces/TMUX_FINAL_SPORTS/logs/countries/archive',
        '/workspaces/TMUX_FINAL_SPORTS/logs/live/archive'
    ]
    
    archive_status = {}
    
    for archive_path in expected_archives:
        endpoint_name = archive_path.split('/')[-2]  # Extract endpoint name
        
        status_info = {
            'exists': os.path.exists(archive_path),
            'is_directory': os.path.isdir(archive_path) if os.path.exists(archive_path) else False,
            'file_count': 0,
            'files': [],
            'total_size_bytes': 0,
            'last_modified': None
        }
        
        if os.path.exists(archive_path) and os.path.isdir(archive_path):
            try:
                files = list(os.listdir(archive_path))
                status_info['file_count'] = len(files)
                status_info['files'] = files[:10]  # First 10 files
                
                # Calculate total size and get last modified
                total_size = 0
                last_mod_time = 0
                
                for file in files:
                    file_path = os.path.join(archive_path, file)
                    if os.path.isfile(file_path):
                        file_size = os.path.getsize(file_path)
                        total_size += file_size
                        mod_time = os.path.getmtime(file_path)
                        if mod_time > last_mod_time:
                            last_mod_time = mod_time
                
                status_info['total_size_bytes'] = total_size
                if last_mod_time > 0:
                    from datetime import datetime
                    status_info['last_modified'] = datetime.fromtimestamp(last_mod_time).strftime('%Y-%m-%d %H:%M:%S')
                    
            except Exception as e:
                status_info['error'] = str(e)
        
        archive_status[endpoint_name] = status_info
        
        # Print status for each directory
        print(f"\n📁 {endpoint_name.upper()} ARCHIVE:")
        print(f"   Path: {archive_path}")
        print(f"   Exists: {'✅' if status_info['exists'] else '❌'}")
        
        if status_info['exists']:
            print(f"   Is Directory: {'✅' if status_info['is_directory'] else '❌'}")
            print(f"   File Count: {status_info['file_count']}")
            print(f"   Total Size: {status_info['total_size_bytes']:,} bytes")
            if status_info['last_modified']:
                print(f"   Last Modified: {status_info['last_modified']}")
            if status_info['files']:
                print(f"   Sample Files: {status_info['files'][:5]}")
    
    return archive_status

def scan_code_for_archive_references() -> Dict[str, List[Dict[str, Any]]]:
    """Scan all Python files for archive directory references"""
    
    print(f"\n🔍 SCANNING CODE FOR ARCHIVE REFERENCES")
    print("=" * 60)
    
    # Archive-related patterns to search for
    archive_patterns = [
        r'archive_dir\s*=',
        r'archive.*path',
        r'logs/\w+/archive',
        r'\.*/archive',
        r'archive.*\.json',
        r'shutil\.copy.*archive',
        r'os\.makedirs.*archive',
        r'archive.*directory',
        r'/archive/',
        r'backup.*archive',
        r'rotation.*archive'
    ]
    
    combined_pattern = '|'.join(f'({pattern})' for pattern in archive_patterns)
    regex = re.compile(combined_pattern, re.IGNORECASE)
    
    results = {}
    
    # Find all Python files
    python_files = list(Path('.').glob('*.py'))
    
    print(f"Scanning {len(python_files)} Python files...")
    
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            file_matches = []
            
            for line_num, line in enumerate(lines, 1):
                if regex.search(line):
                    match_info = {
                        'line_number': line_num,
                        'code_line': line.strip(),
                        'context_before': lines[max(0, line_num-2):line_num-1],
                        'context_after': lines[line_num:min(len(lines), line_num+2)]
                    }
                    file_matches.append(match_info)
            
            if file_matches:
                results[str(file_path)] = file_matches
                
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
    
    # Print results
    if results:
        print(f"\n🚨 FOUND ARCHIVE REFERENCES IN CODE:")
        for file_path, matches in results.items():
            print(f"\n📄 {file_path} ({len(matches)} matches):")
            for match in matches:
                print(f"   Line {match['line_number']}: {match['code_line']}")
    else:
        print(f"\n✅ NO ARCHIVE REFERENCES FOUND IN CODE")
    
    return results

def check_current_logging_paths() -> Dict[str, Any]:
    """Check what logging paths are actually being used in current code"""
    
    print(f"\n🔍 CHECKING CURRENT LOGGING PATHS IN CODE")
    print("=" * 60)
    
    # Pattern for logging file paths
    log_path_patterns = [
        r'logs/\w+/\w+\.json',
        r'/workspaces/TMUX_FINAL_SPORTS/logs/[\w/]+',
        r'live_log_file\s*=',
        r'log.*file\s*=',
        r'with\s+open\(.*/logs/',
        r'json\.dump.*logs'
    ]
    
    combined_pattern = '|'.join(f'({pattern})' for pattern in log_path_patterns)
    regex = re.compile(combined_pattern, re.IGNORECASE)
    
    current_paths = {}
    
    # Scan endpoint files specifically
    endpoint_files = ['live.py', 'details.py', 'odds.py', 'teams.py', 'competitions.py', 'countries.py', 'merge.py']
    
    for file_path in endpoint_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                
                file_paths = []
                
                for line_num, line in enumerate(lines, 1):
                    if regex.search(line):
                        # Extract actual file paths
                        path_match = re.search(r'(/workspaces/TMUX_FINAL_SPORTS/logs/[\w/]+\.json)', line)
                        if path_match:
                            file_paths.append({
                                'line_number': line_num,
                                'path': path_match.group(1),
                                'code_line': line.strip()
                            })
                
                if file_paths:
                    current_paths[file_path] = file_paths
                    
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
    
    # Print current logging paths
    print(f"\n📋 CURRENT LOGGING PATHS IN USE:")
    for file_path, paths in current_paths.items():
        print(f"\n📄 {file_path}:")
        for path_info in paths:
            print(f"   Line {path_info['line_number']}: {path_info['path']}")
            print(f"      Code: {path_info['code_line']}")
    
    return current_paths

def verify_actual_log_files() -> Dict[str, Any]:
    """Verify what log files actually exist on the filesystem"""
    
    print(f"\n🔍 VERIFYING ACTUAL LOG FILES ON FILESYSTEM")
    print("=" * 60)
    
    logs_base = '/workspaces/TMUX_FINAL_SPORTS/logs'
    
    if not os.path.exists(logs_base):
        print(f"❌ Logs directory does not exist: {logs_base}")
        return {}
    
    actual_files = {}
    
    # Walk through logs directory
    for root, dirs, files in os.walk(logs_base):
        endpoint_name = os.path.basename(root)
        
        if endpoint_name == 'logs':  # Skip the base logs directory
            continue
            
        endpoint_files = []
        
        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                file_size = os.path.getsize(file_path)
                mod_time = os.path.getmtime(file_path)
                
                from datetime import datetime
                endpoint_files.append({
                    'filename': file,
                    'full_path': file_path,
                    'size_bytes': file_size,
                    'last_modified': datetime.fromtimestamp(mod_time).strftime('%Y-%m-%d %H:%M:%S')
                })
        
        if endpoint_files:
            actual_files[endpoint_name] = {
                'directory': root,
                'files': endpoint_files
            }
    
    # Print actual files
    print(f"\n📂 ACTUAL LOG FILES FOUND:")
    for endpoint, info in actual_files.items():
        print(f"\n📁 {endpoint.upper()}:")
        print(f"   Directory: {info['directory']}")
        for file_info in info['files']:
            print(f"   📄 {file_info['filename']}")
            print(f"      Size: {file_info['size_bytes']:,} bytes")
            print(f"      Modified: {file_info['last_modified']}")
    
    return actual_files

def main():
    """Main analysis function"""
    
    print("🔬 COMPREHENSIVE ARCHIVE DIRECTORY ANALYSIS")
    print("=" * 70)
    print("Testing archive directories status and code references")
    
    # 1. Check archive directories status
    archive_status = check_archive_directories()
    
    # 2. Scan code for archive references
    code_references = scan_code_for_archive_references()
    
    # 3. Check current logging paths
    current_paths = check_current_logging_paths()
    
    # 4. Verify actual files
    actual_files = verify_actual_log_files()
    
    # Summary report
    print(f"\n📊 FINAL SUMMARY REPORT")
    print("=" * 60)
    
    print(f"\n🗂️  ARCHIVE DIRECTORIES:")
    total_archives = len(archive_status)
    existing_archives = sum(1 for status in archive_status.values() if status['exists'])
    print(f"   Total Expected: {total_archives}")
    print(f"   Actually Exist: {existing_archives}")
    print(f"   Missing: {total_archives - existing_archives}")
    
    print(f"\n💻 CODE REFERENCES:")
    total_files_with_refs = len(code_references)
    total_references = sum(len(matches) for matches in code_references.values())
    print(f"   Files with archive references: {total_files_with_refs}")
    print(f"   Total archive references found: {total_references}")
    
    print(f"\n📄 CURRENT LOGGING:")
    total_endpoint_files = len(current_paths)
    print(f"   Endpoint files with logging: {total_endpoint_files}")
    
    print(f"\n💾 ACTUAL FILES:")
    total_endpoints_with_files = len(actual_files)
    total_log_files = sum(len(info['files']) for info in actual_files.values())
    print(f"   Endpoints with log files: {total_endpoints_with_files}")
    print(f"   Total log files found: {total_log_files}")
    
    # Determine if archives are being used
    print(f"\n🎯 CONCLUSION:")
    if existing_archives == 0 and total_references == 0:
        print("   ✅ NO ARCHIVE DIRECTORIES IN USE - All removed successfully")
    elif existing_archives > 0 and total_references == 0:
        print("   ⚠️  ARCHIVE DIRECTORIES EXIST but no code references them")
    elif existing_archives > 0 and total_references > 0:
        print("   🚨 ARCHIVE DIRECTORIES EXIST and code still references them")
    else:
        print("   ❓ Mixed state - needs manual review")

if __name__ == "__main__":
    main()