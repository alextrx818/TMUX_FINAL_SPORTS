#!/usr/bin/env python3

"""
Debug script to trace the exact issue in merge.py odds processing
"""

import json
import os

def debug_odds_processing():
    """Debug the odds data processing in merge.py"""
    
    print("🔍 DEBUG: Analyzing merge.py odds processing issue")
    print("="*60)
    
    # Load odds data (same way merge.py does)
    print("1. Loading odds data...")
    odds_file = '/workspaces/TMUX_FINAL_SPORTS/logs/odds/odds.json'
    
    try:
        with open(odds_file, 'r', encoding='utf-8') as f:
            odds_data = json.load(f)
        print(f"   ✅ Odds file loaded successfully")
        print(f"   📊 File size: {os.path.getsize(odds_file):,} bytes")
    except Exception as e:
        print(f"   ❌ Error loading odds file: {e}")
        return
    
    # Analyze the structure
    print("\n2. Analyzing odds data structure...")
    print(f"   📋 Top-level keys: {list(odds_data.keys())}")
    print(f"   📅 Timestamp: {odds_data.get('timestamp', 'N/A')}")
    print(f"   📈 Matches processed: {odds_data.get('matches_processed', 'N/A')}")
    print(f"   📊 Total matches: {odds_data.get('total_matches', 'N/A')}")
    
    # Check the data structure that merge.py expects vs what we have
    print("\n3. Checking data structure compatibility...")
    
    if 'data' in odds_data:
        match_data = odds_data['data']
        print(f"   ✅ Found 'data' key with {len(match_data)} matches")
        
        # Show first few match IDs
        match_ids = list(match_data.keys())[:3]
        print(f"   🎯 Sample match IDs: {match_ids}")
        
        # Show structure of first match
        if match_ids:
            first_match_id = match_ids[0]
            first_match_data = match_data[first_match_id]
            print(f"\n   📝 Structure of match '{first_match_id}':")
            print(f"      Company IDs: {list(first_match_data.keys())}")
            
            if first_match_data:
                first_company = list(first_match_data.values())[0]
                print(f"      Market types: {list(first_company.keys())}")
        
        print(f"\n   🔍 ACTUAL DATA STRUCTURE:")
        print(f"      odds_data['data'][match_id][company_id][market_type] = [[odds_arrays]]")
        
    else:
        print(f"   ❌ No 'data' key found in odds file")
    
    # Show what merge.py is expecting vs what it gets
    print("\n4. Merge.py expectations vs reality...")
    
    print(f"   🤔 MERGE.PY EXPECTS (lines 341-348):")
    print(f"      isinstance(odds_data, list) = {isinstance(odds_data, list)}")
    print(f"      Expecting: [{{'request': {{'params': {{'uuid': 'match_id'}}}}}}]")
    
    print(f"\n   🔍 WHAT WE ACTUALLY HAVE:")
    print(f"      isinstance(odds_data, dict) = {isinstance(odds_data, dict)}")
    print(f"      Structure: {{'data': {{'match_id': odds_data}}}}")
    
    # Test the broken logic from merge.py
    print("\n5. Testing merge.py logic...")
    
    # This is the broken logic from merge.py lines 341-348
    odds_by_match = {}
    if odds_data and isinstance(odds_data, list):
        print("   📝 Entering merge.py list processing logic...")
        for odds_entry in odds_data:
            if isinstance(odds_entry, dict) and 'request' in odds_entry and 'params' in odds_entry['request']:
                match_uuid = odds_entry['request']['params'].get('uuid', '')
                if match_uuid:
                    odds_by_match[match_uuid] = odds_data
        print(f"   📊 Matches found by merge.py logic: {len(odds_by_match)}")
    else:
        print("   ❌ Merge.py list processing logic SKIPPED")
        print(f"      Reason: odds_data is {type(odds_data)}, not list")
    
    # Show the correct way to process it
    print("\n6. CORRECT way to process odds data...")
    
    if 'data' in odds_data:
        correct_odds_by_match = odds_data['data']
        print(f"   ✅ Correct processing: {len(correct_odds_by_match)} matches found")
        print(f"   🎯 Sample match IDs: {list(correct_odds_by_match.keys())[:3]}")
    
    print("\n7. SOLUTION:")
    print("   🔧 Replace lines 341-348 in merge.py with:")
    print("   📝 odds_by_match = odds_data.get('data', {}) if odds_data else {}")
    
    print("\n" + "="*60)
    print("🎯 ROOT CAUSE: merge.py expects list format but gets dict format")
    print("✅ FIX: Update merge.py to read from odds_data['data'] directly")

if __name__ == "__main__":
    debug_odds_processing()