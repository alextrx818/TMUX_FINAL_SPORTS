#!/usr/bin/env python3
"""
Comprehensive Live.py Logging Logic Analysis
Extract and test every detail of the current logging implementation
"""

import json
import os
import re
from datetime import datetime
import pytz
from pathlib import Path

def extract_live_logging_code():
    """Extract the exact logging code from live.py"""
    
    print("🔍 EXTRACTING LIVE.PY LOGGING CODE")
    print("=" * 50)
    
    with open('live.py', 'r') as f:
        content = f.read()
        lines = content.split('\n')
    
    # Find logging-related sections
    logging_sections = {
        'imports': [],
        'constants': [],
        'accumulating_logic': [],
        'file_operations': [],
        'timestamp_logic': [],
        'rotation_logic': [],
        'metadata_logic': []
    }
    
    in_logging_section = False
    current_section = []
    
    for i, line in enumerate(lines, 1):
        line_content = line.strip()
        
        # Track imports related to logging
        if any(keyword in line_content for keyword in ['import pytz', 'import json', 'from datetime']):
            logging_sections['imports'].append(f"Line {i}: {line}")
        
        # Track timezone and timestamp logic
        if any(keyword in line_content for keyword in ['pytz.timezone', 'datetime.now', 'strftime']):
            logging_sections['timestamp_logic'].append(f"Line {i}: {line}")
        
        # Track accumulating JSON dump section
        if "ACCUMULATING JSON DUMP" in line_content:
            in_logging_section = True
            current_section = []
        
        if in_logging_section:
            current_section.append(f"Line {i}: {line}")
            
            # End of logging section
            if line_content.startswith('print(f"Accumulated fetch'):
                logging_sections['accumulating_logic'] = current_section.copy()
                in_logging_section = False
        
        # Track file operations
        if any(keyword in line_content for keyword in ['open(', 'json.dump', 'json.load']):
            logging_sections['file_operations'].append(f"Line {i}: {line}")
        
        # Track rotation logic
        if any(keyword in line_content for keyword in ['max_history', 'len(accumulated_log', 'rotated log']):
            logging_sections['rotation_logic'].append(f"Line {i}: {line}")
        
        # Track metadata updates
        if any(keyword in line_content for keyword in ['log_metadata', 'total_fetches', 'first_fetch', 'last_fetch']):
            logging_sections['metadata_logic'].append(f"Line {i}: {line}")
    
    return logging_sections

def analyze_live_json_structure():
    """Analyze the current live.json structure"""
    
    print("\n📄 ANALYZING LIVE.JSON STRUCTURE")
    print("=" * 50)
    
    live_json_path = '/workspaces/TMUX_FINAL_SPORTS/logs/live/live.json'
    
    if not os.path.exists(live_json_path):
        print("❌ live.json does not exist")
        return {}
    
    try:
        with open(live_json_path, 'r') as f:
            data = json.load(f)
        
        analysis = {
            'file_size_bytes': os.path.getsize(live_json_path),
            'structure_type': 'unknown',
            'top_level_keys': list(data.keys()) if isinstance(data, dict) else [],
            'metadata': {},
            'fetch_history_analysis': {},
            'sample_fetch_entry': None
        }
        
        # Analyze structure
        if isinstance(data, dict):
            if 'fetch_history' in data:
                analysis['structure_type'] = 'accumulating_v1.0'
                
                # Analyze metadata
                if 'log_metadata' in data:
                    analysis['metadata'] = data['log_metadata']
                
                # Analyze fetch history
                fetch_history = data.get('fetch_history', [])
                analysis['fetch_history_analysis'] = {
                    'total_entries': len(fetch_history),
                    'entry_structure': [],
                    'fetch_id_pattern': 'unknown',
                    'timestamp_formats': set(),
                    'api_response_included': False
                }
                
                if fetch_history:
                    # Analyze first entry structure
                    first_entry = fetch_history[0]
                    analysis['sample_fetch_entry'] = first_entry
                    analysis['fetch_history_analysis']['entry_structure'] = list(first_entry.keys())
                    
                    # Check for API response
                    if 'api_response' in first_entry:
                        analysis['fetch_history_analysis']['api_response_included'] = True
                    
                    # Analyze fetch ID patterns
                    fetch_ids = [entry.get('fetch_id', '') for entry in fetch_history[:5]]
                    analysis['fetch_history_analysis']['sample_fetch_ids'] = fetch_ids
                    
                    # Analyze timestamp formats
                    timestamps = [entry.get('fetch_timestamp', '') for entry in fetch_history[:5]]
                    analysis['fetch_history_analysis']['sample_timestamps'] = timestamps
            
            elif 'api_response' in data:
                analysis['structure_type'] = 'simple_overwrite'
            else:
                analysis['structure_type'] = 'custom_format'
        
        return analysis
        
    except Exception as e:
        print(f"❌ Error analyzing live.json: {e}")
        return {}

def test_logging_behavior():
    """Test the exact logging behavior by simulating the logic"""
    
    print("\n🧪 TESTING LOGGING BEHAVIOR SIMULATION")
    print("=" * 50)
    
    # Simulate the timezone logic
    ny_tz = pytz.timezone('US/Eastern')
    ny_time = datetime.now(ny_tz)
    timestamp = ny_time.strftime('%m/%d/%Y %I:%M:%S %p')
    
    test_results = {
        'timezone_simulation': {
            'timezone': str(ny_tz),
            'current_time': str(ny_time),
            'formatted_timestamp': f"{timestamp} EST",
            'fetch_id_format': ny_time.strftime('%Y%m%d_%H%M%S'),
            'unix_timestamp': int(ny_time.timestamp())
        },
        'entry_structure_test': {},
        'rotation_logic_test': {},
        'metadata_update_test': {}
    }
    
    # Test entry structure creation
    mock_api_data = {
        "code": 0,
        "results": [
            {"id": "test_match_1", "score": []},
            {"id": "test_match_2", "score": []}
        ]
    }
    
    new_fetch_entry = {
        "fetch_id": ny_time.strftime('%Y%m%d_%H%M%S'),
        "api_response": mock_api_data,
        "fetch_timestamp": f"{timestamp} EST",
        "match_count": len(mock_api_data.get('results', [])),
        "fetch_unix_time": int(ny_time.timestamp())
    }
    
    test_results['entry_structure_test'] = {
        'entry_keys': list(new_fetch_entry.keys()),
        'entry_example': new_fetch_entry,
        'match_count_calculation': f"len(data.get('results', [])) = {len(mock_api_data.get('results', []))}"
    }
    
    # Test rotation logic
    max_history = 100
    mock_history = [f"entry_{i}" for i in range(150)]  # Simulate 150 entries
    
    if len(mock_history) > max_history:
        rotated_history = mock_history[-max_history:]
        rotation_occurred = True
    else:
        rotated_history = mock_history
        rotation_occurred = False
    
    test_results['rotation_logic_test'] = {
        'max_history_limit': max_history,
        'mock_entries_before': len(mock_history),
        'entries_after_rotation': len(rotated_history),
        'rotation_occurred': rotation_occurred,
        'rotation_logic': f"if len(fetch_history) > {max_history}: fetch_history = fetch_history[-{max_history}:]"
    }
    
    # Test metadata update logic
    mock_metadata = {
        "total_fetches": 0,
        "first_fetch": new_fetch_entry["fetch_timestamp"],
        "last_fetch": new_fetch_entry["fetch_timestamp"],
        "log_format": "accumulating_v1.0"
    }
    
    # Simulate adding new entry
    mock_fetch_history = [new_fetch_entry]
    mock_metadata["total_fetches"] = len(mock_fetch_history)
    mock_metadata["last_fetch"] = new_fetch_entry["fetch_timestamp"]
    
    test_results['metadata_update_test'] = {
        'metadata_structure': mock_metadata,
        'update_logic': {
            'total_fetches': 'len(accumulated_log["fetch_history"])',
            'last_fetch': 'new_fetch_entry["fetch_timestamp"]',
            'first_fetch_update': 'Only updated when total_fetches == 1'
        }
    }
    
    return test_results

def extract_exact_code_blocks():
    """Extract the exact code blocks from live.py with line numbers"""
    
    print("\n📝 EXACT CODE BLOCKS FROM LIVE.PY")
    print("=" * 50)
    
    with open('live.py', 'r') as f:
        lines = f.readlines()
    
    code_blocks = {
        'timezone_setup': [],
        'entry_creation': [],
        'file_loading': [],
        'migration_logic': [],
        'history_append': [],
        'metadata_update': [],
        'rotation_logic': [],
        'file_saving': []
    }
    
    # Define line ranges for each block (based on live.py structure)
    ranges = {
        'timezone_setup': (125, 130),
        'entry_creation': (131, 138),
        'file_loading': (142, 189),
        'migration_logic': (147, 166),
        'history_append': (191, 193),
        'metadata_update': (194, 206),
        'rotation_logic': (200, 207),
        'file_saving': (208, 212)
    }
    
    for block_name, (start, end) in ranges.items():
        for i in range(start - 1, min(end, len(lines))):
            if i < len(lines):
                code_blocks[block_name].append(f"Line {i+1}: {lines[i].rstrip()}")
    
    return code_blocks

def main():
    """Main analysis function"""
    
    print("🔬 COMPREHENSIVE LIVE.PY LOGGING ANALYSIS")
    print("=" * 60)
    
    # 1. Extract logging code
    logging_sections = extract_live_logging_code()
    
    for section_name, code_lines in logging_sections.items():
        if code_lines:
            print(f"\n📋 {section_name.upper().replace('_', ' ')}:")
            print("-" * 40)
            for line in code_lines:
                print(f"  {line}")
    
    # 2. Analyze live.json structure
    json_analysis = analyze_live_json_structure()
    
    if json_analysis:
        print(f"\n📊 JSON ANALYSIS RESULTS:")
        print("-" * 40)
        print(f"File size: {json_analysis['file_size_bytes']:,} bytes")
        print(f"Structure type: {json_analysis['structure_type']}")
        print(f"Top-level keys: {json_analysis['top_level_keys']}")
        
        if json_analysis.get('metadata'):
            print(f"\nMetadata:")
            for key, value in json_analysis['metadata'].items():
                print(f"  {key}: {value}")
        
        if json_analysis.get('fetch_history_analysis'):
            fha = json_analysis['fetch_history_analysis']
            print(f"\nFetch History Analysis:")
            print(f"  Total entries: {fha['total_entries']}")
            print(f"  Entry structure: {fha['entry_structure']}")
            print(f"  API response included: {fha['api_response_included']}")
            if fha.get('sample_fetch_ids'):
                print(f"  Sample fetch IDs: {fha['sample_fetch_ids']}")
            if fha.get('sample_timestamps'):
                print(f"  Sample timestamps: {fha['sample_timestamps']}")
    
    # 3. Test logging behavior
    test_results = test_logging_behavior()
    
    print(f"\n🧪 BEHAVIOR TEST RESULTS:")
    print("-" * 40)
    
    for test_name, results in test_results.items():
        print(f"\n{test_name.upper().replace('_', ' ')}:")
        if isinstance(results, dict):
            for key, value in results.items():
                if isinstance(value, dict):
                    print(f"  {key}:")
                    for sub_key, sub_value in value.items():
                        print(f"    {sub_key}: {sub_value}")
                else:
                    print(f"  {key}: {value}")
        else:
            print(f"  {results}")
    
    # 4. Extract exact code blocks
    code_blocks = extract_exact_code_blocks()
    
    print(f"\n💻 EXACT CODE IMPLEMENTATION:")
    print("-" * 40)
    
    for block_name, code_lines in code_blocks.items():
        if code_lines:
            print(f"\n{block_name.upper().replace('_', ' ')}:")
            for line in code_lines:
                print(f"  {line}")
    
    print(f"\n✅ COMPLETE LOGGING ANALYSIS FINISHED")
    print("=" * 60)

if __name__ == "__main__":
    main()