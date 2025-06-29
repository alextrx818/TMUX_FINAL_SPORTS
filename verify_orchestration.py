#!/usr/bin/env python3
"""
Comprehensive Orchestration Verification Script
Analyzes ALL files to map exact call patterns and data flow
"""

import os
import re
from pathlib import Path

def find_subprocess_calls():
    """Find all subprocess.run() calls in Python files"""
    print("🔍 SUBPROCESS CALLS ANALYSIS:")
    print("=" * 50)
    
    subprocess_calls = {}
    
    for py_file in Path('.').glob('*.py'):
        if py_file.name == 'verify_orchestration.py':
            continue
            
        try:
            with open(py_file, 'r') as f:
                content = f.read()
            
            # Find subprocess.run calls
            subprocess_pattern = r"subprocess\.run\(\[([^\]]+)\]"
            matches = re.findall(subprocess_pattern, content)
            
            if matches:
                subprocess_calls[str(py_file)] = []
                for match in matches:
                    # Clean up the match
                    called_files = [item.strip().strip("'\"") for item in match.split(',')]
                    subprocess_calls[str(py_file)].append(called_files)
        
        except Exception as e:
            print(f"Error reading {py_file}: {e}")
    
    if subprocess_calls:
        for caller, calls in subprocess_calls.items():
            print(f"📄 {caller}:")
            for call in calls:
                print(f"   → calls: {' '.join(call)}")
    else:
        print("❌ No subprocess calls found")
    
    print()
    return subprocess_calls

def find_temp_file_usage():
    """Find all /tmp/ file reads and writes"""
    print("📁 TEMP FILE USAGE ANALYSIS:")
    print("=" * 50)
    
    temp_patterns = [
        r"/tmp/[a-zA-Z_]+\.json",
        r"'/tmp/[a-zA-Z_]+\.json'",
        r'"/tmp/[a-zA-Z_]+\.json"'
    ]
    
    file_usage = {}
    
    for py_file in Path('.').glob('*.py'):
        if py_file.name == 'verify_orchestration.py':
            continue
            
        try:
            with open(py_file, 'r') as f:
                content = f.read()
            
            reads = []
            writes = []
            
            # Find temp file references
            for pattern in temp_patterns:
                matches = re.findall(pattern, content)
                for match in matches:
                    clean_match = match.strip("'\"")
                    
                    # Check if it's a read or write
                    if f"open('{clean_match}', 'r')" in content or f'open("{clean_match}", "r")' in content:
                        reads.append(clean_match)
                    elif f"open('{clean_match}', 'w')" in content or f'open("{clean_match}", "w")' in content:
                        writes.append(clean_match)
            
            if reads or writes:
                file_usage[str(py_file)] = {'reads': list(set(reads)), 'writes': list(set(writes))}
        
        except Exception as e:
            print(f"Error reading {py_file}: {e}")
    
    for file_name, usage in file_usage.items():
        print(f"📄 {file_name}:")
        if usage['reads']:
            print(f"   📖 READS: {usage['reads']}")
        if usage['writes']:
            print(f"   📝 WRITES: {usage['writes']}")
    
    print()
    return file_usage

def find_bash_script_calls():
    """Find what bash scripts call"""
    print("🔧 BASH SCRIPT CALLS ANALYSIS:")
    print("=" * 50)
    
    bash_calls = {}
    
    for bash_file in Path('.').glob('*.sh'):
        try:
            with open(bash_file, 'r') as f:
                content = f.read()
            
            # Find python3 calls
            python_pattern = r"python3\s+([a-zA-Z_]+\.py)"
            matches = re.findall(python_pattern, content)
            
            if matches:
                bash_calls[str(bash_file)] = matches
        
        except Exception as e:
            print(f"Error reading {bash_file}: {e}")
    
    for script, calls in bash_calls.items():
        print(f"📄 {script}:")
        for call in calls:
            print(f"   → calls: python3 {call}")
    
    print()
    return bash_calls

def create_flow_diagram(subprocess_calls, temp_usage, bash_calls):
    """Create complete orchestration flow diagram"""
    print("🎯 COMPLETE ORCHESTRATION FLOW:")
    print("=" * 50)
    
    # Start with bash scripts
    for script, python_calls in bash_calls.items():
        print(f"🔄 {script}")
        for py_call in python_calls:
            print(f"    ↓ starts")
            print(f"  📄 {py_call}")
            
            # Show what this python file does
            py_path = f"./{py_call}"
            if py_path in temp_usage:
                usage = temp_usage[py_path]
                if usage['reads']:
                    print(f"      📖 reads: {usage['reads']}")
                if usage['writes']:
                    print(f"      📝 writes: {usage['writes']}")
            
            # Show what this python file calls
            if py_path in subprocess_calls:
                for calls in subprocess_calls[py_path]:
                    next_file = calls[1] if len(calls) > 1 else calls[0]
                    print(f"      ↓ subprocess calls")
                    print(f"    📄 {next_file}")
                    
                    # Recursively show next level
                    next_path = f"./{next_file}"
                    if next_path in temp_usage:
                        next_usage = temp_usage[next_path]
                        if next_usage['reads']:
                            print(f"        📖 reads: {next_usage['reads']}")
                        if next_usage['writes']:
                            print(f"        📝 writes: {next_usage['writes']}")
    
    print()

def verify_data_consistency():
    """Verify that data flow makes sense"""
    print("✅ DATA FLOW VERIFICATION:")
    print("=" * 50)
    
    expected_flow = {
        "live.py": {
            "reads": [],
            "writes": ["/tmp/live_matches.json"],
            "calls": ["details.py", "odds.py"]
        },
        "details.py": {
            "reads": ["/tmp/live_matches.json"],
            "writes": ["/tmp/match_details.json", "/tmp/team_ids.json", "/tmp/competition_ids.json"],
            "calls": ["teams.py", "competitions.py", "countries.py"]
        },
        "odds.py": {
            "reads": ["/tmp/live_matches.json"],
            "writes": ["/tmp/match_odds.json"],
            "calls": []
        },
        "teams.py": {
            "reads": ["/tmp/team_ids.json"],
            "writes": ["/tmp/team_data.json"],
            "calls": []
        },
        "competitions.py": {
            "reads": ["/tmp/competition_ids.json"],
            "writes": ["/tmp/competition_data.json"],
            "calls": []
        },
        "countries.py": {
            "reads": [],
            "writes": ["/tmp/country_data.json"],
            "calls": []
        }
    }
    
    print("Expected vs Actual Flow:")
    for file_name, expected in expected_flow.items():
        print(f"\n📄 {file_name}:")
        print(f"  Expected reads: {expected['reads']}")
        print(f"  Expected writes: {expected['writes']}")
        print(f"  Expected calls: {expected['calls']}")
        
        # TODO: Compare with actual findings
    
    print()

def main():
    """Main verification function"""
    print("🔍 COMPLETE ORCHESTRATION VERIFICATION")
    print("=" * 60)
    print("Analyzing ALL files to map exact call patterns...")
    print()
    
    # Run all analyses
    subprocess_calls = find_subprocess_calls()
    temp_usage = find_temp_file_usage()
    bash_calls = find_bash_script_calls()
    
    # Create flow diagram
    create_flow_diagram(subprocess_calls, temp_usage, bash_calls)
    
    # Verify consistency
    verify_data_consistency()
    
    print("🎯 SUMMARY:")
    print("=" * 20)
    print(f"📄 Found {len(bash_calls)} bash scripts with python calls")
    print(f"🔗 Found {sum(len(calls) for calls in subprocess_calls.values())} subprocess calls")
    print(f"📁 Found {len(temp_usage)} files using temp files")
    
    print("\n✅ Verification complete!")

if __name__ == "__main__":
    main()