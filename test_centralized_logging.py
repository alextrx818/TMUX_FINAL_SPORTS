#!/usr/bin/env python3
"""
Comprehensive test to find ALL traces of centralized logging references
This will identify any imports or calls to shared logging configuration files
"""

import os
import re
import glob
from typing import List, Dict, Any

def find_centralized_logging_references() -> Dict[str, Any]:
    """Find all references to centralized logging in Python files"""
    
    results = {
        "centralized_imports": [],
        "centralized_calls": [],
        "logging_config_files": [],
        "suspicious_patterns": [],
        "clean_files": [],
        "problematic_files": []
    }
    
    # Known centralized logging patterns to search for
    centralized_patterns = [
        r'from\s+logging_utils\s+import',
        r'import\s+logging_utils',
        r'from\s+loggingconfig\s+import',
        r'import\s+loggingconfig', 
        r'from\s+log_config\s+import',
        r'import\s+log_config',
        r'from\s+logger\s+import',
        r'import\s+logger\b',
        r'create_logger\(',
        r'setup_logging\(',
        r'configure_logging\(',
        r'get_logger\(',
        r'Logger\(',
        r'logging_utils\.',
        r'loggingconfig\.',
        r'log_config\.'
    ]
    
    # Find all Python files
    python_files = []
    for pattern in ['*.py', '**/*.py']:
        python_files.extend(glob.glob(pattern, recursive=True))
    
    # Remove duplicates and sort
    python_files = sorted(list(set(python_files)))
    
    print("🔍 Scanning for centralized logging references...")
    print(f"📁 Found {len(python_files)} Python files to scan")
    print("=" * 60)
    
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            file_issues = []
            
            # Check each pattern
            for pattern in centralized_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    # Find line number
                    line_num = content[:match.start()].count('\n') + 1
                    line_content = lines[line_num - 1].strip()
                    
                    issue = {
                        "file": file_path,
                        "line": line_num,
                        "pattern": pattern,
                        "match": match.group(),
                        "line_content": line_content
                    }
                    
                    if 'import' in pattern:
                        results["centralized_imports"].append(issue)
                    elif any(x in pattern for x in ['create_logger', 'setup_logging', 'configure_logging', 'get_logger']):
                        results["centralized_calls"].append(issue)
                    else:
                        results["suspicious_patterns"].append(issue)
                    
                    file_issues.append(issue)
            
            # Check if file itself is a logging config file
            filename = os.path.basename(file_path).lower()
            if any(name in filename for name in ['logging_utils', 'loggingconfig', 'log_config', 'logger_config']):
                results["logging_config_files"].append({
                    "file": file_path,
                    "reason": "Filename suggests centralized logging config"
                })
                file_issues.append({"type": "config_file"})
            
            # Categorize file
            if file_issues:
                results["problematic_files"].append({
                    "file": file_path,
                    "issues": len(file_issues),
                    "details": file_issues
                })
            else:
                results["clean_files"].append(file_path)
                
        except Exception as e:
            print(f"❌ Error reading {file_path}: {e}")
    
    return results

def print_detailed_report(results: Dict[str, Any]):
    """Print comprehensive report of findings"""
    
    print("\n" + "="*60)
    print("🚨 CENTRALIZED LOGGING DETECTION REPORT")
    print("="*60)
    
    # Summary
    total_issues = (len(results["centralized_imports"]) + 
                   len(results["centralized_calls"]) + 
                   len(results["logging_config_files"]) + 
                   len(results["suspicious_patterns"]))
    
    print(f"\n📊 SUMMARY:")
    print(f"   • Total files scanned: {len(results['clean_files']) + len(results['problematic_files'])}")
    print(f"   • Clean files: {len(results['clean_files'])}")
    print(f"   • Problematic files: {len(results['problematic_files'])}")
    print(f"   • Total issues found: {total_issues}")
    
    # Centralized imports
    if results["centralized_imports"]:
        print(f"\n🔴 CENTRALIZED IMPORTS FOUND ({len(results['centralized_imports'])}):")
        for issue in results["centralized_imports"]:
            print(f"   📄 {issue['file']}:{issue['line']}")
            print(f"      Pattern: {issue['pattern']}")
            print(f"      Code: {issue['line_content']}")
            print(f"      Match: '{issue['match']}'")
            print()
    
    # Centralized calls
    if results["centralized_calls"]:
        print(f"\n🟡 CENTRALIZED FUNCTION CALLS ({len(results['centralized_calls'])}):")
        for issue in results["centralized_calls"]:
            print(f"   📄 {issue['file']}:{issue['line']}")
            print(f"      Pattern: {issue['pattern']}")
            print(f"      Code: {issue['line_content']}")
            print(f"      Match: '{issue['match']}'")
            print()
    
    # Config files
    if results["logging_config_files"]:
        print(f"\n🟠 LOGGING CONFIG FILES ({len(results['logging_config_files'])}):")
        for issue in results["logging_config_files"]:
            print(f"   📄 {issue['file']}")
            print(f"      Reason: {issue['reason']}")
            print()
    
    # Suspicious patterns
    if results["suspicious_patterns"]:
        print(f"\n🟣 SUSPICIOUS PATTERNS ({len(results['suspicious_patterns'])}):")
        for issue in results["suspicious_patterns"]:
            print(f"   📄 {issue['file']}:{issue['line']}")
            print(f"      Pattern: {issue['pattern']}")
            print(f"      Code: {issue['line_content']}")
            print(f"      Match: '{issue['match']}'")
            print()
    
    # Files needing fixes
    if results["problematic_files"]:
        print(f"\n🛠️  FILES NEEDING FIXES:")
        for file_info in results["problematic_files"]:
            print(f"   📄 {file_info['file']} ({file_info['issues']} issues)")
    
    # Clean files (summary)
    if results["clean_files"]:
        print(f"\n✅ CLEAN FILES ({len(results['clean_files'])}):")
        clean_main_files = [f for f in results["clean_files"] if not f.startswith('.') and '/' not in f]
        if clean_main_files:
            print(f"   Main files: {', '.join(clean_main_files[:10])}")
            if len(clean_main_files) > 10:
                print(f"   ... and {len(clean_main_files) - 10} more")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    if total_issues > 0:
        print("   1. Remove all centralized logging imports")
        print("   2. Replace centralized logger calls with direct print() statements")
        print("   3. Delete centralized logging config files if they exist")
        print("   4. Hardcode logging logic directly into each file")
    else:
        print("   🎉 No centralized logging found! All files are independent.")
    
    print("\n" + "="*60)

def main():
    """Run the comprehensive centralized logging detection test"""
    print("🚀 Starting comprehensive centralized logging detection...")
    
    # Run the scan
    results = find_centralized_logging_references()
    
    # Print detailed report
    print_detailed_report(results)
    
    # Return exit code based on findings
    total_issues = (len(results["centralized_imports"]) + 
                   len(results["centralized_calls"]) + 
                   len(results["logging_config_files"]))
    
    if total_issues > 0:
        print(f"\n❌ FAILED: Found {total_issues} centralized logging references")
        return 1
    else:
        print(f"\n✅ PASSED: No centralized logging references found")
        return 0

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)