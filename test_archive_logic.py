#!/usr/bin/env python3
"""
Test to pinpoint current archiving logic locations
This will identify exactly where archiving code exists in each file
"""

import os
import re
import glob
from typing import List, Dict, Any

def find_archive_logic() -> Dict[str, Any]:
    """Find all archiving logic in Python files"""
    
    results = {
        "files_with_archive_logic": [],
        "archive_patterns_found": [],
        "archive_directories_created": [],
        "rotation_logic": [],
        "no_archive_logic": []
    }
    
    # Archive-related patterns to search for
    archive_patterns = [
        r'archive.*=',
        r'archive_dir',
        r'archive_file',
        r'archive.*\.json',
        r'shutil\.copy',
        r'shutil\.copy2',
        r'\.makedirs.*archive',
        r'glob\.glob.*archive',
        r'archive.*timestamp',
        r'rotation',
        r'files_to_remove',
        r'keep.*last.*\d+',
        r'remove.*old.*file',
        r'os\.remove',
        r'len.*archive.*>',
        r'\[-\d+:\]',  # Array slicing for rotation
        r'archive.*exist'
    ]
    
    # Main Python files to check
    main_files = [
        'live.py', 'details.py', 'odds.py', 'teams.py', 
        'competitions.py', 'countries.py', 'merge.py'
    ]
    
    print("🔍 Scanning for archive logic locations...")
    print("=" * 70)
    
    for file_path in main_files:
        if not os.path.exists(file_path):
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            file_archive_info = {
                "file": file_path,
                "archive_logic": [],
                "line_details": []
            }
            
            has_archive_logic = False
            
            # Check each pattern
            for pattern in archive_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    # Find line number
                    line_num = content[:match.start()].count('\n') + 1
                    line_content = lines[line_num - 1].strip()
                    
                    match_info = {
                        "line": line_num,
                        "pattern": pattern,
                        "match": match.group(),
                        "line_content": line_content,
                        "context_start": max(1, line_num - 2),
                        "context_end": min(len(lines), line_num + 2)
                    }
                    
                    file_archive_info["archive_logic"].append(match_info)
                    file_archive_info["line_details"].append(f"Line {line_num}: {line_content}")
                    has_archive_logic = True
                    
                    # Categorize by type
                    if 'archive_dir' in match.group().lower() or 'makedirs' in match.group().lower():
                        results["archive_directories_created"].append(match_info)
                    elif any(word in match.group().lower() for word in ['rotation', 'remove', 'files_to_remove', '[-']):
                        results["rotation_logic"].append(match_info)
                    else:
                        results["archive_patterns_found"].append(match_info)
            
            # Categorize file
            if has_archive_logic:
                results["files_with_archive_logic"].append(file_archive_info)
            else:
                results["no_archive_logic"].append(file_path)
                
        except Exception as e:
            print(f"❌ Error reading {file_path}: {e}")
    
    return results

def print_archive_report(results: Dict[str, Any]):
    """Print detailed report of archive logic locations"""
    
    print("\n" + "="*70)
    print("📁 ARCHIVE LOGIC LOCATION REPORT")
    print("="*70)
    
    # Summary
    total_files_checked = len(results["files_with_archive_logic"]) + len(results["no_archive_logic"])
    total_archive_references = (len(results["archive_patterns_found"]) + 
                              len(results["archive_directories_created"]) + 
                              len(results["rotation_logic"]))
    
    print(f"\n📊 SUMMARY:")
    print(f"   • Total files checked: {total_files_checked}")
    print(f"   • Files WITH archive logic: {len(results['files_with_archive_logic'])}")
    print(f"   • Files WITHOUT archive logic: {len(results['no_archive_logic'])}")
    print(f"   • Total archive code references: {total_archive_references}")
    
    # Files with archive logic
    if results["files_with_archive_logic"]:
        print(f"\n🗂️ FILES WITH ARCHIVE LOGIC:")
        for file_info in results["files_with_archive_logic"]:
            print(f"\n   📄 {file_info['file']} ({len(file_info['archive_logic'])} references)")
            
            # Group by line numbers for cleaner display
            line_groups = {}
            for logic in file_info['archive_logic']:
                line_num = logic['line']
                if line_num not in line_groups:
                    line_groups[line_num] = []
                line_groups[line_num].append(logic)
            
            # Display by line number
            for line_num in sorted(line_groups.keys()):
                logic_items = line_groups[line_num]
                first_item = logic_items[0]
                print(f"      Line {line_num}: {first_item['line_content']}")
                if len(logic_items) > 1:
                    print(f"         (matches {len(logic_items)} patterns)")
    
    # Archive directory creation
    if results["archive_directories_created"]:
        print(f"\n📂 ARCHIVE DIRECTORY CREATION LOGIC:")
        for logic in results["archive_directories_created"]:
            print(f"   📄 {logic['file'] if 'file' in logic else 'Unknown'}:{logic['line']}")
            print(f"      Code: {logic['line_content']}")
            print(f"      Pattern: {logic['pattern']}")
            print()
    
    # Rotation logic
    if results["rotation_logic"]:
        print(f"\n🔄 ROTATION LOGIC FOUND:")
        for logic in results["rotation_logic"]:
            print(f"   📄 {logic['file'] if 'file' in logic else 'Unknown'}:{logic['line']}")
            print(f"      Code: {logic['line_content']}")
            print(f"      Pattern: {logic['pattern']}")
            print()
    
    # Files without archive logic
    if results["no_archive_logic"]:
        print(f"\n❌ FILES WITHOUT ARCHIVE LOGIC:")
        for file_path in results["no_archive_logic"]:
            print(f"   📄 {file_path}")
    
    # Detailed line-by-line breakdown
    print(f"\n🔍 DETAILED LINE-BY-LINE BREAKDOWN:")
    for file_info in results["files_with_archive_logic"]:
        print(f"\n   📄 {file_info['file']}:")
        for detail in file_info["line_details"]:
            print(f"      {detail}")
    
    print("\n" + "="*70)

def check_actual_archive_dirs():
    """Check which archive directories actually exist"""
    print(f"\n🗂️ ACTUAL ARCHIVE DIRECTORIES ON DISK:")
    
    archive_paths = [
        "/workspaces/TMUX_FINAL_SPORTS/logs/details/archive",
        "/workspaces/TMUX_FINAL_SPORTS/logs/odds/archive", 
        "/workspaces/TMUX_FINAL_SPORTS/logs/live/archive",
        "/workspaces/TMUX_FINAL_SPORTS/cache/teams/archive",
        "/workspaces/TMUX_FINAL_SPORTS/cache/competitions/archive",
        "/workspaces/TMUX_FINAL_SPORTS/cache/countries/archive",
        "/workspaces/TMUX_FINAL_SPORTS/logs/merge/archive"
    ]
    
    for path in archive_paths:
        if os.path.exists(path):
            try:
                file_count = len([f for f in os.listdir(path) if f.endswith('.json')])
                print(f"   ✅ {path} ({file_count} files)")
            except Exception as e:
                print(f"   ❌ {path} (error: {e})")
        else:
            print(f"   ❌ {path} (does not exist)")

def main():
    """Run the archive logic detection test"""
    print("🚀 Starting archive logic location detection...")
    
    # Find archive logic
    results = find_archive_logic()
    
    # Print detailed report
    print_archive_report(results)
    
    # Check actual directories
    check_actual_archive_dirs()
    
    # Summary
    files_with_archive = len(results["files_with_archive_logic"])
    total_references = (len(results["archive_patterns_found"]) + 
                       len(results["archive_directories_created"]) + 
                       len(results["rotation_logic"]))
    
    print(f"\n🎯 FINAL SUMMARY:")
    print(f"   Archive logic found in {files_with_archive} files")
    print(f"   Total archive code references: {total_references}")
    
    if files_with_archive > 0:
        print(f"\n✅ Archive logic locations identified successfully!")
        return 0
    else:
        print(f"\n❌ No archive logic found!")
        return 1

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)