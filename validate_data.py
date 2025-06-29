#!/usr/bin/env python3
"""
Data validation script to check the quality and structure of fetched data
"""

import json
import os
from typing import Dict, Any, List

def validate_json_file(filepath: str, expected_keys: List[str] = None) -> Dict[str, Any]:
    """Validate a JSON file exists and has expected structure"""
    result = {
        'exists': False,
        'valid_json': False,
        'size_bytes': 0,
        'record_count': 0,
        'has_expected_keys': False,
        'sample_data': None,
        'errors': []
    }
    
    try:
        # Check if file exists
        if not os.path.exists(filepath):
            result['errors'].append("File does not exist")
            return result
        
        result['exists'] = True
        result['size_bytes'] = os.path.getsize(filepath)
        
        # Try to load JSON
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        result['valid_json'] = True
        
        # Count records
        if isinstance(data, list):
            result['record_count'] = len(data)
            result['sample_data'] = data[0] if data else None
        elif isinstance(data, dict):
            result['record_count'] = len(data)
            result['sample_data'] = list(data.values())[0] if data else None
        
        # Check expected keys if provided
        if expected_keys and result['sample_data']:
            if isinstance(result['sample_data'], dict):
                has_keys = all(key in result['sample_data'] for key in expected_keys)
                result['has_expected_keys'] = has_keys
                if not has_keys:
                    missing_keys = [key for key in expected_keys if key not in result['sample_data']]
                    result['errors'].append(f"Missing keys: {missing_keys}")
        
    except json.JSONDecodeError as e:
        result['errors'].append(f"Invalid JSON: {e}")
    except Exception as e:
        result['errors'].append(f"Unexpected error: {e}")
    
    return result

def main():
    """Main validation function"""
    print("🔍 Data Validation Report")
    print("=" * 50)
    
    # Define expected file structures
    validations = [
        {
            'file': '/tmp/live_matches.json',
            'name': 'Live Matches',
            'expected_keys': ['id', 'status_id']
        },
        {
            'file': '/tmp/match_details.json',
            'name': 'Match Details',
            'expected_keys': ['id', 'home_team_id', 'away_team_id']
        },
        {
            'file': '/tmp/match_odds.json',
            'name': 'Match Odds',
            'expected_keys': None  # Structure varies
        },
        {
            'file': '/tmp/team_data.json',
            'name': 'Team Data',
            'expected_keys': ['name', 'short_name']
        },
        {
            'file': '/tmp/competition_data.json',
            'name': 'Competition Data',
            'expected_keys': ['name']
        },
        {
            'file': '/tmp/country_data.json',
            'name': 'Country Data',
            'expected_keys': ['name']
        }
    ]
    
    total_size = 0
    total_records = 0
    all_valid = True
    
    for validation in validations:
        result = validate_json_file(validation['file'], validation.get('expected_keys'))
        
        print(f"\n📄 {validation['name']}")
        print(f"   {'✅' if result['exists'] else '❌'} File exists: {result['exists']}")
        print(f"   {'✅' if result['valid_json'] else '❌'} Valid JSON: {result['valid_json']}")
        print(f"   📊 Records: {result['record_count']}")
        print(f"   💾 Size: {result['size_bytes']:,} bytes")
        
        if validation.get('expected_keys'):
            print(f"   {'✅' if result['has_expected_keys'] else '❌'} Has expected keys: {result['has_expected_keys']}")
        
        if result['errors']:
            print(f"   ❗ Errors: {', '.join(result['errors'])}")
            all_valid = False
        
        total_size += result['size_bytes']
        total_records += result['record_count']
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 VALIDATION SUMMARY")
    print("=" * 50)
    print(f"📈 Total Records: {total_records:,}")
    print(f"💾 Total Size: {total_size:,} bytes ({total_size/1024/1024:.2f} MB)")
    print(f"✅ All Valid: {all_valid}")
    
    if all_valid:
        print("\n🎉 All data files are valid and contain expected data!")
    else:
        print("\n⚠️  Some data files have issues - check errors above")
    
    # Pipeline flow validation
    print(f"\n🔄 PIPELINE FLOW VALIDATION")
    print("=" * 30)
    
    # Check if we have the ID mapping files
    id_files = [
        ('/tmp/team_ids.json', 'Team IDs'),
        ('/tmp/competition_ids.json', 'Competition IDs')
    ]
    
    for id_file, name in id_files:
        if os.path.exists(id_file):
            with open(id_file, 'r') as f:
                ids = json.load(f)
            print(f"✅ {name}: {len(ids)} unique IDs extracted")
        else:
            print(f"❌ {name}: ID file missing")

if __name__ == "__main__":
    main()