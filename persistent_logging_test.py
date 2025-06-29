#!/usr/bin/env python3

"""
PERSISTENT LOGGING TEST SCRIPT
=============================
Tests and proves which endpoints have persistent JSON logging to /logs/ directory
and which endpoints are missing this logging functionality.
"""

import os
import json
from pathlib import Path
from datetime import datetime

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(title):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{title.center(80)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.END}")

def print_section(title):
    print(f"\n{Colors.BOLD}{Colors.BLUE}[{title}]{Colors.END}")

def print_success(msg):
    print(f"{Colors.GREEN}✅ {msg}{Colors.END}")

def print_error(msg):
    print(f"{Colors.RED}❌ {msg}{Colors.END}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.END}")

def check_file_exists_and_info(filepath):
    """Check if file exists and return basic info"""
    try:
        path = Path(filepath)
        if path.exists():
            stat = path.stat()
            size_mb = round(stat.st_size / (1024*1024), 2) if stat.st_size > 1024*1024 else None
            size_kb = round(stat.st_size / 1024, 2) if stat.st_size > 1024 else None
            size_str = f"{size_mb} MB" if size_mb else f"{size_kb} KB" if size_kb else f"{stat.st_size} bytes"
            
            return {
                'exists': True,
                'size': stat.st_size,
                'size_str': size_str,
                'modified': datetime.fromtimestamp(stat.st_mtime)
            }
        else:
            return {'exists': False}
    except Exception as e:
        return {'exists': False, 'error': str(e)}

def test_endpoint_logging():
    """Test each endpoint for persistent logging to /logs/ directory"""
    
    print_header("PERSISTENT LOGGING TEST FOR ALL ENDPOINTS")
    
    # Define endpoints and their expected persistent log paths
    endpoints = {
        'live.py': {
            'persistent_log': '/workspaces/TMUX_FINAL_SPORTS/logs/live/live.json',
            'temp_file': '/tmp/live_matches.json',
            'expected_pattern': 'accumulating'
        },
        'details.py': {
            'persistent_log': '/workspaces/TMUX_FINAL_SPORTS/logs/details/details.json',
            'temp_file': '/tmp/match_details.json',
            'expected_pattern': 'standard'
        },
        'odds.py': {
            'persistent_log': '/workspaces/TMUX_FINAL_SPORTS/logs/odds/odds.json',
            'temp_file': '/tmp/match_odds.json',
            'expected_pattern': 'standard'
        },
        'teams.py': {
            'persistent_log': '/workspaces/TMUX_FINAL_SPORTS/cache/teams/teams_cache.json',
            'temp_file': '/tmp/team_data.json',
            'expected_pattern': 'caching'
        },
        'competitions.py': {
            'persistent_log': '/workspaces/TMUX_FINAL_SPORTS/cache/competitions/competitions_cache.json',
            'temp_file': '/tmp/competition_data.json',
            'expected_pattern': 'caching'
        },
        'countries.py': {
            'persistent_log': '/workspaces/TMUX_FINAL_SPORTS/cache/countries/countries_cache.json',
            'temp_file': '/tmp/country_data.json',
            'expected_pattern': 'caching'
        }
    }
    
    results = {}
    
    for endpoint, paths in endpoints.items():
        print_section(f"Testing {endpoint}")
        
        # Check persistent log file
        persistent_info = check_file_exists_and_info(paths['persistent_log'])
        temp_info = check_file_exists_and_info(paths['temp_file'])
        
        if persistent_info['exists']:
            print_success(f"Persistent log EXISTS: {paths['persistent_log']}")
            print(f"    📊 Size: {persistent_info['size_str']}")
            print(f"    🕒 Modified: {persistent_info['modified']}")
            
            # Check if it's actually in /logs/ directory (not cache)
            is_in_logs = '/logs/' in paths['persistent_log']
            if is_in_logs:
                print_success(f"    ✅ Located in /logs/ directory (TRUE PERSISTENT LOGGING)")
            else:
                print_warning(f"    ⚠️  Located in /cache/ directory (CACHE-BASED PERSISTENCE)")
            
            results[endpoint] = {
                'persistent_exists': True,
                'in_logs_directory': is_in_logs,
                'pattern': paths['expected_pattern'],
                'status': 'HAS_PERSISTENT_LOGGING' if is_in_logs else 'CACHE_BASED_LOGGING'
            }
        else:
            print_error(f"Persistent log MISSING: {paths['persistent_log']}")
            results[endpoint] = {
                'persistent_exists': False,
                'in_logs_directory': False,
                'pattern': paths['expected_pattern'],
                'status': 'NO_PERSISTENT_LOGGING'
            }
        
        # Check temp file
        if temp_info['exists']:
            print_success(f"Temp file exists: {paths['temp_file']} ({temp_info['size_str']})")
        else:
            print_warning(f"Temp file missing: {paths['temp_file']}")
        
        print()
    
    return results

def analyze_results(results):
    """Analyze test results and provide summary"""
    
    print_header("TEST RESULTS ANALYSIS")
    
    # Categorize endpoints
    has_logs_logging = []
    has_cache_logging = []
    no_persistent_logging = []
    
    for endpoint, data in results.items():
        if data['status'] == 'HAS_PERSISTENT_LOGGING':
            has_logs_logging.append(endpoint)
        elif data['status'] == 'CACHE_BASED_LOGGING':
            has_cache_logging.append(endpoint)
        else:
            no_persistent_logging.append(endpoint)
    
    print_section("ENDPOINTS WITH TRUE PERSISTENT LOGGING (/logs/ directory)")
    if has_logs_logging:
        for endpoint in has_logs_logging:
            print_success(f"{endpoint} - writes to /logs/ directory")
    else:
        print_error("No endpoints found with true persistent logging!")
    
    print_section("ENDPOINTS WITH CACHE-BASED PERSISTENCE (/cache/ directory)")
    if has_cache_logging:
        for endpoint in has_cache_logging:
            print_warning(f"{endpoint} - uses /cache/ directory for persistence")
    else:
        print("No endpoints use cache-based persistence")
    
    print_section("ENDPOINTS WITH NO PERSISTENT LOGGING")
    if no_persistent_logging:
        for endpoint in no_persistent_logging:
            print_error(f"{endpoint} - NO persistent log files found")
    else:
        print_success("All endpoints have some form of persistent logging")
    
    print_header("SUMMARY STATISTICS")
    total = len(results)
    logs_count = len(has_logs_logging)
    cache_count = len(has_cache_logging)
    none_count = len(no_persistent_logging)
    
    print(f"📊 Total endpoints tested: {total}")
    print(f"✅ Endpoints with /logs/ directory logging: {logs_count}")
    print(f"⚠️  Endpoints with /cache/ directory logging: {cache_count}")
    print(f"❌ Endpoints with NO persistent logging: {none_count}")
    
    # Test the specific claim
    print_header("TESTING SPECIFIC CLAIM")
    print(f"{Colors.BOLD}CLAIM TO TEST:{Colors.END}")
    print(f"  'odds.py is the only endpoint without persistent JSON logging to the /logs/ directory structure'")
    
    print(f"\n{Colors.BOLD}EVIDENCE:{Colors.END}")
    
    # Check if odds.py specifically lacks /logs/ directory logging
    odds_result = results.get('odds.py', {})
    if not odds_result.get('in_logs_directory', False):
        print_error(f"odds.py does NOT write to /logs/ directory")
    else:
        print_success(f"odds.py DOES write to /logs/ directory")
    
    # Check if other endpoints have /logs/ directory logging
    other_endpoints_with_logs = [ep for ep in has_logs_logging if ep != 'odds.py']
    other_endpoints_without_logs = [ep for ep in results.keys() if ep != 'odds.py' and not results[ep].get('in_logs_directory', False)]
    
    if other_endpoints_with_logs:
        print_success(f"Other endpoints WITH /logs/ logging: {', '.join(other_endpoints_with_logs)}")
    
    if other_endpoints_without_logs:
        print_warning(f"Other endpoints WITHOUT /logs/ logging: {', '.join(other_endpoints_without_logs)}")
    
    print(f"\n{Colors.BOLD}VERDICT:{Colors.END}")
    if not odds_result.get('in_logs_directory', False) and other_endpoints_with_logs:
        if len(other_endpoints_without_logs) == 0:
            print_success(f"✅ CLAIM IS TRUE: odds.py is the ONLY endpoint without /logs/ directory logging")
        else:
            print_warning(f"⚠️  CLAIM IS PARTIALLY TRUE: odds.py lacks /logs/ logging, but so do: {', '.join(other_endpoints_without_logs)}")
    else:
        print_error(f"❌ CLAIM IS FALSE: Either odds.py has /logs/ logging or other endpoints also lack it")

def main():
    """Main test function"""
    results = test_endpoint_logging()
    analyze_results(results)
    
    print(f"\n{Colors.BOLD}Test completed at {datetime.now()}{Colors.END}")

if __name__ == "__main__":
    main()