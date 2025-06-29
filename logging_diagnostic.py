#!/usr/bin/env python3

"""
COMPREHENSIVE LOGGING DIAGNOSTIC SCRIPT
======================================
This script analyzes the exact state of logging across all endpoints
and identifies specific issues with their logging mechanisms.

Run with: python3 logging_diagnostic.py
"""

import os
import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(title):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{title.center(60)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}")

def print_section(title):
    print(f"\n{Colors.BOLD}{Colors.BLUE}[{title}]{Colors.END}")

def print_success(msg):
    print(f"{Colors.GREEN}✅ {msg}{Colors.END}")

def print_error(msg):
    print(f"{Colors.RED}❌ {msg}{Colors.END}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.END}")

def print_info(msg):
    print(f"{Colors.CYAN}ℹ️  {msg}{Colors.END}")

def get_file_info(filepath):
    """Get file information including size, modification time, and existence"""
    try:
        path = Path(filepath)
        if path.exists():
            stat = path.stat()
            return {
                'exists': True,
                'size': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime),
                'size_mb': round(stat.st_size / (1024*1024), 2) if stat.st_size > 1024*1024 else None,
                'size_kb': round(stat.st_size / 1024, 2) if stat.st_size > 1024 else None
            }
        else:
            return {'exists': False}
    except Exception as e:
        return {'exists': False, 'error': str(e)}

def check_json_validity(filepath):
    """Check if JSON file is valid and return basic info"""
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        return {
            'valid': True,
            'type': type(data).__name__,
            'keys': list(data.keys()) if isinstance(data, dict) else None,
            'length': len(data) if isinstance(data, (list, dict)) else None
        }
    except json.JSONDecodeError as e:
        return {'valid': False, 'error': f'JSON Error: {e}'}
    except Exception as e:
        return {'valid': False, 'error': f'Read Error: {e}'}

def analyze_endpoint_logging():
    """Analyze logging for each endpoint"""
    
    endpoints = {
        'live.py': {
            'log_path': '/workspaces/TMUX_FINAL_SPORTS/logs/live/live.json',
            'pattern': 'accumulating',
            'expected_keys': ['log_metadata', 'fetch_history']
        },
        'details.py': {
            'log_path': '/workspaces/TMUX_FINAL_SPORTS/logs/details/details.json',
            'pattern': 'standard',
            'expected_keys': ['api_response', 'fetch_timestamp']
        },
        'odds.py': {
            'log_path': '/workspaces/TMUX_FINAL_SPORTS/logs/odds/odds.json',
            'pattern': 'standard',
            'expected_keys': ['api_response', 'fetch_timestamp']
        },
        'teams.py': {
            'log_path': '/workspaces/TMUX_FINAL_SPORTS/cache/teams/teams_cache.json',
            'pattern': 'caching',
            'expected_keys': ['cache_metadata', 'teams']
        },
        'competitions.py': {
            'log_path': '/workspaces/TMUX_FINAL_SPORTS/cache/competitions/competitions_cache.json',
            'pattern': 'caching',
            'expected_keys': ['cache_metadata', 'competitions']
        },
        'countries.py': {
            'log_path': '/workspaces/TMUX_FINAL_SPORTS/cache/countries/countries_cache.json',
            'pattern': 'caching',
            'expected_keys': ['cache_metadata', 'countries']
        }
    }
    
    results = {}
    
    for endpoint, config in endpoints.items():
        print_section(f"Analyzing {endpoint}")
        
        # Check file existence and basic info
        file_info = get_file_info(config['log_path'])
        results[endpoint] = {'file_info': file_info, 'config': config}
        
        if not file_info['exists']:
            print_error(f"Log file missing: {config['log_path']}")
            results[endpoint]['status'] = 'MISSING_FILE'
            continue
            
        # Display file info
        size_str = ""
        if file_info.get('size_mb'):
            size_str = f"{file_info['size_mb']} MB"
        elif file_info.get('size_kb'):
            size_str = f"{file_info['size_kb']} KB"
        else:
            size_str = f"{file_info['size']} bytes"
            
        print_info(f"File exists: {size_str}, modified: {file_info['modified']}")
        
        # Check JSON validity
        json_info = check_json_validity(config['log_path'])
        results[endpoint]['json_info'] = json_info
        
        if not json_info['valid']:
            print_error(f"Invalid JSON: {json_info['error']}")
            results[endpoint]['status'] = 'INVALID_JSON'
            continue
            
        # Check structure
        missing_keys = []
        if json_info['keys']:
            for expected_key in config['expected_keys']:
                if expected_key not in json_info['keys']:
                    missing_keys.append(expected_key)
                    
        if missing_keys:
            print_warning(f"Missing expected keys: {missing_keys}")
            results[endpoint]['missing_keys'] = missing_keys
            results[endpoint]['status'] = 'STRUCTURE_ISSUE'
        else:
            print_success(f"Valid {config['pattern']} logging structure")
            results[endpoint]['status'] = 'WORKING'
            
        # Pattern-specific checks
        if config['pattern'] == 'accumulating' and json_info['keys']:
            if 'fetch_history' in json_info['keys']:
                try:
                    with open(config['log_path'], 'r') as f:
                        data = json.load(f)
                    fetch_count = len(data.get('fetch_history', []))
                    print_info(f"Fetch history contains {fetch_count} entries")
                    results[endpoint]['fetch_count'] = fetch_count
                except:
                    pass
                    
        elif config['pattern'] == 'caching' and json_info['keys']:
            try:
                with open(config['log_path'], 'r') as f:
                    data = json.load(f)
                cache_data = data.get(config['expected_keys'][1], {})
                if isinstance(cache_data, dict):
                    print_info(f"Cache contains {len(cache_data)} entries")
                    results[endpoint]['cache_count'] = len(cache_data)
            except:
                pass
    
    return results

def check_pipeline_execution():
    """Check if pipeline is currently running"""
    print_section("Pipeline Execution Status")
    
    try:
        # Check for background processes
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        processes = result.stdout
        
        pipeline_processes = []
        for line in processes.split('\n'):
            if any(script in line for script in ['continuous_fetch.sh', 'background_runner.sh', 'live.py', 'details.py', 'odds.py']):
                if 'grep' not in line:  # Exclude grep matches
                    pipeline_processes.append(line.strip())
        
        if pipeline_processes:
            print_success(f"Found {len(pipeline_processes)} pipeline process(es)")
            for proc in pipeline_processes:
                print_info(f"  {proc}")
        else:
            print_warning("No pipeline processes found running")
            
        return pipeline_processes
        
    except Exception as e:
        print_error(f"Error checking processes: {e}")
        return []

def check_temp_files():
    """Check temporary files created during pipeline execution"""
    print_section("Temporary Files Analysis")
    
    temp_files = [
        '/tmp/live_matches.json',
        '/tmp/match_details.json',
        '/tmp/match_odds.json'
    ]
    
    temp_results = {}
    
    for temp_file in temp_files:
        file_info = get_file_info(temp_file)
        temp_results[temp_file] = file_info
        
        if file_info['exists']:
            # Check age
            age = datetime.now() - file_info['modified']
            if age < timedelta(minutes=5):
                print_success(f"{temp_file}: Fresh ({age.seconds}s old)")
            elif age < timedelta(hours=1):
                print_info(f"{temp_file}: Recent ({age.seconds//60}m old)")
            else:
                print_warning(f"{temp_file}: Stale ({age.seconds//3600}h old)")
        else:
            print_error(f"{temp_file}: Missing")
    
    return temp_results

def check_logging_code():
    """Check if logging code exists in the Python files"""
    print_section("Logging Code Analysis")
    
    files_to_check = [
        '/workspaces/TMUX_FINAL_SPORTS/live.py',
        '/workspaces/TMUX_FINAL_SPORTS/details.py', 
        '/workspaces/TMUX_FINAL_SPORTS/odds.py',
        '/workspaces/TMUX_FINAL_SPORTS/teams.py',
        '/workspaces/TMUX_FINAL_SPORTS/competitions.py',
        '/workspaces/TMUX_FINAL_SPORTS/countries.py'
    ]
    
    logging_patterns = [
        'json.dump',
        'with open',
        'save_to_log',
        'logging',
        '.json'
    ]
    
    code_results = {}
    
    for file_path in files_to_check:
        filename = os.path.basename(file_path)
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            found_patterns = []
            for pattern in logging_patterns:
                if pattern in content:
                    count = content.count(pattern)
                    found_patterns.append(f"{pattern}({count})")
            
            if found_patterns:
                print_success(f"{filename}: {', '.join(found_patterns)}")
                code_results[filename] = {'status': 'HAS_LOGGING', 'patterns': found_patterns}
            else:
                print_warning(f"{filename}: No logging patterns found")
                code_results[filename] = {'status': 'NO_LOGGING', 'patterns': []}
                
        except Exception as e:
            print_error(f"{filename}: Error reading file - {e}")
            code_results[filename] = {'status': 'ERROR', 'error': str(e)}
    
    return code_results

def analyze_recent_activity():
    """Analyze recent logging activity"""
    print_section("Recent Activity Analysis")
    
    # Check modification times of all log files
    log_dirs = [
        '/workspaces/TMUX_FINAL_SPORTS/logs/live',
        '/workspaces/TMUX_FINAL_SPORTS/logs/details',
        '/workspaces/TMUX_FINAL_SPORTS/logs/odds',
        '/workspaces/TMUX_FINAL_SPORTS/cache/teams',
        '/workspaces/TMUX_FINAL_SPORTS/cache/competitions',
        '/workspaces/TMUX_FINAL_SPORTS/cache/countries'
    ]
    
    recent_files = []
    cutoff_time = datetime.now() - timedelta(minutes=10)
    
    for log_dir in log_dirs:
        if os.path.exists(log_dir):
            for file in os.listdir(log_dir):
                if file.endswith('.json'):
                    filepath = os.path.join(log_dir, file)
                    file_info = get_file_info(filepath)
                    if file_info['exists'] and file_info['modified'] > cutoff_time:
                        age_seconds = (datetime.now() - file_info['modified']).seconds
                        recent_files.append((filepath, age_seconds))
    
    if recent_files:
        print_success(f"Found {len(recent_files)} recently modified log files:")
        for filepath, age in sorted(recent_files, key=lambda x: x[1]):
            print_info(f"  {filepath} ({age}s ago)")
    else:
        print_warning("No log files modified in the last 10 minutes")
    
    return recent_files

def main():
    print_header("SPORTS PIPELINE LOGGING DIAGNOSTIC")
    
    # Run all diagnostic checks
    endpoint_results = analyze_endpoint_logging()
    pipeline_status = check_pipeline_execution()
    temp_results = check_temp_files()
    code_results = check_logging_code()
    recent_activity = analyze_recent_activity()
    
    # Summary report
    print_header("DIAGNOSTIC SUMMARY")
    
    # Count statuses
    working_count = sum(1 for result in endpoint_results.values() if result.get('status') == 'WORKING')
    total_endpoints = len(endpoint_results)
    
    print_section("Overall Status")
    if working_count == total_endpoints:
        print_success(f"All {total_endpoints} endpoints have working logging")
    else:
        print_error(f"Only {working_count}/{total_endpoints} endpoints have working logging")
    
    # Detailed issues
    print_section("Specific Issues Found")
    issues_found = False
    
    for endpoint, result in endpoint_results.items():
        if result.get('status') != 'WORKING':
            issues_found = True
            status = result.get('status', 'UNKNOWN')
            
            if status == 'MISSING_FILE':
                print_error(f"{endpoint}: Log file missing at {result['config']['log_path']}")
            elif status == 'INVALID_JSON':
                print_error(f"{endpoint}: Invalid JSON - {result['json_info']['error']}")
            elif status == 'STRUCTURE_ISSUE':
                missing = result.get('missing_keys', [])
                print_error(f"{endpoint}: Missing keys: {missing}")
    
    # Check for odds.py specific issue
    odds_result = endpoint_results.get('odds.py', {})
    if odds_result.get('status') == 'MISSING_FILE':
        print_section("CRITICAL ISSUE: odds.py")
        print_error("odds.py is NOT creating persistent log files!")
        print_error("This endpoint only saves to /tmp/match_odds.json (temporary)")
        print_error("SOLUTION: Add persistent logging logic to odds.py")
    
    if not issues_found:
        print_success("No specific logging issues found!")
    
    # Pipeline status
    print_section("Pipeline Status")
    if pipeline_status:
        print_success("Pipeline appears to be running")
    else:
        print_warning("Pipeline may not be running - check background_runner.sh")
    
    # Recent activity summary
    print_section("Activity Summary")
    if recent_activity:
        print_success(f"Logging activity detected in last 10 minutes")
    else:
        print_warning("No recent logging activity - pipeline may be stalled")
    
    print(f"\n{Colors.BOLD}Diagnostic completed at {datetime.now()}{Colors.END}")

if __name__ == "__main__":
    main()