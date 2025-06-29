#!/usr/bin/env python3

# ========================================
# CENTRALIZED LOGGING SYSTEM REMOVAL NOTE
# ========================================
# This script was used to extract centralized logging code before it was removed.
# The centralized logging system (logging_utils.py, loggingconfig.py, etc.) was 
# completely removed. Each endpoint now has independent, hardcoded logging logic.
# This script is kept for historical reference but should not be used.
# ========================================

"""
DEPRECATED: Extract ONLY the logging implementation code from all Python files
This script is no longer relevant as centralized logging was removed.
Each endpoint file now contains its own independent, hardcoded logging logic.
"""

import re
from pathlib import Path

def extract_pure_logging_code():
    """Extract only the core logging implementation code"""
    
    # Patterns for actual logging implementation (not analysis/testing)
    logging_code_patterns = [
        r'class.*Logger',
        r'def.*log',
        r'logger\s*=',
        r'\.log_request\(',
        r'create_logger\(',
        r'from logging_utils import',
        r'import logging',
        r'logging\.',
        r'EndpointLogger',
        r'def.*logging',
    ]
    
    combined_pattern = '|'.join(f'({pattern})' for pattern in logging_code_patterns)
    regex = re.compile(combined_pattern, re.IGNORECASE)
    
    results = {}
    
    # Find all Python files
    python_files = list(Path('.').glob('*.py'))
    
    for file_path in python_files:
        # Skip analysis/test files
        if any(skip in str(file_path) for skip in ['analyze', 'test_', 'validate', 'view_', 'cleanup']):
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            logging_code_lines = []
            for line_num, line in enumerate(lines, 1):
                if regex.search(line):
                    # Get surrounding context (2 lines before and after)
                    start_idx = max(0, line_num - 3)
                    end_idx = min(len(lines), line_num + 2)
                    
                    context_lines = []
                    for i in range(start_idx, end_idx):
                        prefix = ">>>" if i == line_num - 1 else "   "
                        context_lines.append(f"{prefix} {i+1:3d}: {lines[i].rstrip()}")
                    
                    logging_code_lines.append({
                        'line_num': line_num,
                        'code': line.strip(),
                        'context': context_lines
                    })
            
            if logging_code_lines:
                results[str(file_path)] = logging_code_lines
                
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
    
    return results

def main():
    """Extract and display pure logging code"""
    
    print("🔧 LOGGING CODE EXTRACTION")
    print("=" * 50)
    print("Extracting ONLY logging implementation code (no analysis/testing)")
    
    logging_code = extract_pure_logging_code()
    
    total_code_lines = 0
    
    for file_path, code_blocks in logging_code.items():
        print(f"\n📄 {file_path}")
        print("-" * 40)
        
        for block in code_blocks:
            print(f"\nLine {block['line_num']}: {block['code']}")
            print("Context:")
            for context_line in block['context']:
                print(context_line)
            print()
            total_code_lines += 1
    
    print(f"\n📊 Total logging code lines found: {total_code_lines}")

if __name__ == "__main__":
    main()