#!/usr/bin/env python3

# ========================================
# CENTRALIZED LOGGING SYSTEM REMOVAL NOTE
# ========================================
# This script was used to analyze centralized logging before it was removed.
# The centralized logging system (logging_utils.py, loggingconfig.py, etc.) was 
# completely removed. Each endpoint now has independent, hardcoded logging logic.
# This script is kept for historical reference but should not be used.
# ========================================

"""
DEPRECATED: Comprehensive Logging Analysis Script
This script is no longer relevant as centralized logging was removed.
Each endpoint file now contains its own independent, hardcoded logging logic.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple

def extract_logging_lines() -> Dict[str, List[Tuple[int, str]]]:
    """Extract all logging-related lines from Python files"""
    
    logging_patterns = [
        r'logger',
        r'logging',
        r'log_request',
        r'create_logger',
        r'EndpointLogger',
        r'print\(',
        r'\.log\(',
        r'from.*logging',
        r'import.*logging',
    ]
    
    combined_pattern = '|'.join(f'({pattern})' for pattern in logging_patterns)
    regex = re.compile(combined_pattern, re.IGNORECASE)
    
    results = {}
    
    # Find all Python files
    python_files = list(Path('.').glob('*.py'))
    
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            matching_lines = []
            for line_num, line in enumerate(lines, 1):
                if regex.search(line):
                    matching_lines.append((line_num, line.strip()))
            
            if matching_lines:
                results[str(file_path)] = matching_lines
                
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
    
    return results

def analyze_logging_structure():
    """Analyze the current logging structure"""
    
    analysis = {
        'log_directories': [],
        'log_files': [],
        'archive_files': 0,
        'total_log_size': 0
    }
    
    # Check logs directory structure
    logs_dir = Path('logs')
    if logs_dir.exists():
        for item in logs_dir.rglob('*'):
            if item.is_dir():
                analysis['log_directories'].append(str(item))
            elif item.is_file() and item.suffix == '.json':
                analysis['log_files'].append(str(item))
                if 'archive' in str(item):
                    analysis['archive_files'] += 1
                try:
                    analysis['total_log_size'] += item.stat().st_size
                except:
                    pass
    
    return analysis

def test_logging_functionality():
    """Test if logging is working correctly"""
    
    test_results = {
        'import_tests': {},
        'logger_creation': {},
        'file_creation': {}
    }
    
    # Test 1: Can we import logging_utils?
    try:
        from logging_utils import create_logger, EndpointLogger
        test_results['import_tests']['logging_utils'] = 'SUCCESS'
    except Exception as e:
        test_results['import_tests']['logging_utils'] = f'FAILED: {e}'
    
    # Test 2: Can we create a logger?
    try:
        test_logger = create_logger('test_endpoint')
        test_results['logger_creation']['create_logger'] = 'SUCCESS'
        
        # Test 3: Can we log a request?
        test_request = {
            'url': 'https://test.com',
            'method': 'GET',
            'params': {'test': 'value'}
        }
        
        test_response = {
            'code': 0,
            'results': [{'test': 'data'}]
        }
        
        test_logger.log_request(test_request, test_response, 'success')
        test_results['file_creation']['log_request'] = 'SUCCESS'
        
        # Check if file was created
        test_log_file = Path('logs/test_endpoint/test_endpoint.json')
        if test_log_file.exists():
            test_results['file_creation']['file_exists'] = 'SUCCESS'
        else:
            test_results['file_creation']['file_exists'] = 'FAILED: Log file not created'
            
    except Exception as e:
        test_results['logger_creation']['create_logger'] = f'FAILED: {e}'
        test_results['file_creation']['log_request'] = f'FAILED: {e}'
    
    return test_results

def main():
    """Main analysis function"""
    
    print("🔍 LOGGING ANALYSIS REPORT")
    print("=" * 50)
    
    # 1. Extract all logging-related code
    print("\n📝 LOGGING CODE EXTRACTION:")
    print("-" * 30)
    
    logging_lines = extract_logging_lines()
    
    total_logging_lines = 0
    for file_path, lines in logging_lines.items():
        print(f"\n📄 {file_path} ({len(lines)} lines):")
        for line_num, line in lines:
            print(f"  {line_num:3d}: {line}")
            total_logging_lines += 1
    
    print(f"\n📊 Total logging-related lines: {total_logging_lines}")
    
    # 2. Analyze logging structure
    print("\n🏗️  LOGGING STRUCTURE ANALYSIS:")
    print("-" * 30)
    
    structure = analyze_logging_structure()
    
    print(f"📁 Log directories: {len(structure['log_directories'])}")
    for directory in structure['log_directories']:
        print(f"  - {directory}")
    
    print(f"\n📄 Log files: {len(structure['log_files'])}")
    for log_file in structure['log_files'][:10]:  # Show first 10
        print(f"  - {log_file}")
    if len(structure['log_files']) > 10:
        print(f"  ... and {len(structure['log_files']) - 10} more")
    
    print(f"\n📦 Archive files: {structure['archive_files']}")
    print(f"💾 Total log size: {structure['total_log_size'] / (1024*1024):.2f} MB")
    
    # 3. Test logging functionality
    print("\n🧪 LOGGING FUNCTIONALITY TEST:")
    print("-" * 30)
    
    test_results = test_logging_functionality()
    
    print("🔗 Import Tests:")
    for test, result in test_results['import_tests'].items():
        status = "✅" if "SUCCESS" in result else "❌"
        print(f"  {status} {test}: {result}")
    
    print("\n🏭 Logger Creation Tests:")
    for test, result in test_results['logger_creation'].items():
        status = "✅" if "SUCCESS" in result else "❌"
        print(f"  {status} {test}: {result}")
    
    print("\n📝 File Creation Tests:")
    for test, result in test_results['file_creation'].items():
        status = "✅" if "SUCCESS" in result else "❌"
        print(f"  {status} {test}: {result}")
    
    # 4. Summary and recommendations
    print("\n📋 SUMMARY & RECOMMENDATIONS:")
    print("-" * 30)
    
    issues_found = []
    
    # Check for common issues
    if any("FAILED" in str(result) for result in test_results['import_tests'].values()):
        issues_found.append("❌ Import failures detected")
    
    if any("FAILED" in str(result) for result in test_results['logger_creation'].values()):
        issues_found.append("❌ Logger creation failures detected")
    
    if any("FAILED" in str(result) for result in test_results['file_creation'].values()):
        issues_found.append("❌ Log file creation failures detected")
    
    if structure['total_log_size'] > 100 * 1024 * 1024:  # > 100MB
        issues_found.append("⚠️  Large log files detected (>100MB)")
    
    if structure['archive_files'] > 1000:
        issues_found.append("⚠️  Excessive archive files (>1000)")
    
    if issues_found:
        print("🚨 ISSUES FOUND:")
        for issue in issues_found:
            print(f"  {issue}")
    else:
        print("✅ No major issues detected!")
    
    print(f"\n📈 Statistics:")
    print(f"  - Total Python files with logging: {len(logging_lines)}")
    print(f"  - Total logging-related lines: {total_logging_lines}")
    print(f"  - Total log directories: {len(structure['log_directories'])}")
    print(f"  - Total log files: {len(structure['log_files'])}")

if __name__ == "__main__":
    main()