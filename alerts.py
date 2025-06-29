#!/usr/bin/env python3

"""
DIAGNOSTIC NOTE - FIELD EXTRACTION FIX
=====================================
Issue Resolved: Field extraction disconnect - 06/29/2025 05:08 EST

Problem: Over/Under arrays were being identified in odds data but flattened fields were not appearing in output.
Root Cause: Field name conflict between 'match_status' from Over/Under array and existing match data structure.

Solution: Changed Over/Under array[5] field from 'match_status' to 'overunder_match_status' to prevent field conflicts.

General Application for Future Field Extraction Issues:
1) Verify field name uniqueness to prevent conflicts
2) Check that array identification AND field assignment are both working  
3) Look for field processing order issues that might cause overwrites
4) Test extraction logic with actual data arrays

Technical Details: Over/Under flattening code was functional but 'match_status' field assignment was being 
overwritten by existing match data processing. Fix ensures unique field names for all flattened array elements.

STATUS ID REFERENCE
==================
Status IDs found in the 'details_status_id' field of match data:

| Status ID | Meaning | Description |
|-----------|---------|-------------|
| 0 | Abnormal | Abnormal (suggest hiding) |
| 1 | Not started | Match has not started yet |
| 2 | First half | Match is in first half |
| 3 | Half-time | Match is at half-time break |
| 4 | Second half | Match is in second half |
| 5 | Overtime | Match is in overtime |
| 6 | Overtime (deprecated) | Overtime (deprecated status) |
| 7 | Penalty Shoot-out | Match is in penalty shoot-out |
| 8 | End | Match has ended |
| 9 | Delay | Match is delayed |
| 10 | Interrupt | Match is interrupted |
| 11 | Cut in half | Match was cut in half |
| 12 | Cancel | Match was cancelled |
| 13 | To be determined | Match time/status to be determined |

UPDATED KEY (for reference):
- 2: First Half
- 3: Half-time  
- 4: Second Half
- 5: Overtime
- 6: Overtime (deprecated)
- 7: Penalty Shoot-out
- 8: End
- 9: Delay
- 10: Interrupt

Most common status IDs in current data: 2 (First half), 3 (Half-time), 4 (Second half), 8 (End), 9 (Delay), 13 (TBD)
"""

import json
import os
import sys
import subprocess
from datetime import datetime
from typing import Dict, List, Any, Optional
import pytz

def load_monitoring_data() -> Optional[Dict[str, Any]]:
    """Load monitoring.json data with error handling"""
    source_file = '/workspaces/TMUX_FINAL_SPORTS/logs/monitoring/monitoring.json'
    
    try:
        if os.path.exists(source_file):
            with open(source_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            print(f"ERROR: Source file not found: {source_file}")
            return None
    except Exception as e:
        print(f"ERROR: Failed to load data: {e}")
        return None

def extract_match_fields(match: Dict[str, Any]) -> Dict[str, Any]:
    """Extract fields using systematic field-by-field processing with optional tasks"""
    
    # Initialize extracted match with ordered structure
    extracted = {}
    
    # PERMANENT RULE: FIELD ORDERING - Process fields in specific sequence
    
    # Step 1: Basic match info (F01-F03)
    for field_name in ["match_id", "timestamp", "scheduled_time_readable"]:
        if field_name in match:
            extracted[field_name] = match[field_name]
    
    # Step 2: PERMANENT RULE: Competition field flattening (F04)
    if "competition" in match and isinstance(match["competition"], dict):
        # MANDATORY TASK: Flatten competition structure to competition_name
        if "name" in match["competition"]:
            extracted["competition_name"] = str(match["competition"]["name"]).strip()
        # Do not include original nested structure
    
    # Step 3: PERMANENT RULE: Teams field flattening (F05-F06)
    if "teams" in match and isinstance(match["teams"], dict):
        # MANDATORY TASK: Flatten teams structure to home_team_name and away_team_name
        if "home" in match["teams"] and isinstance(match["teams"]["home"], dict):
            if "name" in match["teams"]["home"]:
                extracted["home_team_name"] = str(match["teams"]["home"]["name"]).strip()
        
        if "away" in match["teams"] and isinstance(match["teams"]["away"], dict):
            if "name" in match["teams"]["away"]:
                extracted["away_team_name"] = str(match["teams"]["away"]["name"]).strip()
        # Do not include original nested structure
    
    # Step 4: PERMANENT RULE: details_status_id placement (F07)
    if "details_status_id" in match:
        extracted["details_status_id"] = match["details_status_id"]
    
    # Step 4.1: PERMANENT RULE: Visual separator after details_status_id (F07.1)
    extracted[""] = ""
    
    # Step 5: Process score fields with separators
    for field_name, field_value in match.items():
        if field_name not in {"match_id", "timestamp", "scheduled_time_readable", "competition", "teams", "details_status_id", "odds", "spread_score", "match_status"}:
            extracted[field_name] = field_value
            
            # PERMANENT RULE: Add visual separator after home_corners (F10.1)
            if field_name == "home_corners":
                extracted[" "] = ""
            
            # PERMANENT RULE: Add visual separator after away_corners (F14.1)
            if field_name == "away_corners":
                extracted["  "] = ""
    
    # Step 6: PERMANENT RULE: Flatten odds arrays (spread, over/under, moneyline, and corners) - INSERT BEFORE ODDS
    if "odds" in match and isinstance(match["odds"], dict):
        # Process odds structure and flatten arrays
        spread_processed = False
        overunder_processed = False
        moneyline_processed = False
        corners_processed = False
        
        for bookmaker_id, bookmaker_data in match["odds"].items():
            if isinstance(bookmaker_data, dict):
                # Flatten spread arrays
                if not spread_processed and "spread" in bookmaker_data:
                    spread_arrays = bookmaker_data["spread"]
                    if isinstance(spread_arrays, list) and len(spread_arrays) > 0:
                        # Flatten first spread array only
                        spread_array = spread_arrays[0]
                        if isinstance(spread_array, list) and len(spread_array) >= 8:
                            # Flatten spread array to individual fields
                            extracted["spread_timestamp"] = spread_array[0]
                            extracted["spread_capture_time"] = spread_array[1]
                            extracted["spread_home_odds"] = spread_array[2]
                            extracted["spread_value"] = spread_array[3]
                            extracted["spread_away_odds"] = spread_array[4]
                            extracted["spread_match_status"] = spread_array[5]
                            # Skip spread_live_flag (index 6) - removed per user request
                            extracted["spread_game_score"] = spread_array[7]
                            extracted[":"] = ""
                            spread_processed = True
                
                # Flatten over/under arrays
                if not overunder_processed and "Over/Under" in bookmaker_data:
                    overunder_arrays = bookmaker_data["Over/Under"]
                    if isinstance(overunder_arrays, list) and len(overunder_arrays) > 0:
                        # Flatten first over/under array only
                        overunder_array = overunder_arrays[0]
                        if isinstance(overunder_array, list) and len(overunder_array) >= 8:
                            # Flatten over/under array to individual fields
                            extracted["overunder_timestamp"] = overunder_array[0]
                            extracted["overunder_capture_time"] = overunder_array[1]
                            extracted["overunder_over_odds"] = overunder_array[2]
                            extracted["overunder_total_line"] = overunder_array[3]
                            extracted["overunder_under_odds"] = overunder_array[4]
                            extracted["overunder_match_status"] = overunder_array[5]
                            # Skip indices 6 and 7 - removed per user request
                            extracted["overunder_game_score"] = overunder_array[7]
                            extracted["::"] = ""
                            overunder_processed = True
                
                # Flatten MoneyLine arrays
                if not moneyline_processed and "MoneyLine" in bookmaker_data:
                    moneyline_arrays = bookmaker_data["MoneyLine"]
                    if isinstance(moneyline_arrays, list) and len(moneyline_arrays) > 0:
                        # Flatten first MoneyLine array only
                        moneyline_array = moneyline_arrays[0]
                        if isinstance(moneyline_array, list) and len(moneyline_array) >= 8:
                            # Flatten MoneyLine array to individual fields
                            extracted["moneyline_timestamp"] = moneyline_array[0]
                            extracted["moneyline_capture_time"] = moneyline_array[1]
                            extracted["moneyline_home"] = moneyline_array[2]
                            extracted["moneyline_draw"] = moneyline_array[3]
                            extracted["moneyline_away"] = moneyline_array[4]
                            extracted["moneyline_match_status"] = moneyline_array[5]
                            # Skip index 6 - filtered per user request
                            extracted["moneyline_game_score"] = moneyline_array[7]
                            extracted[":::"] = ""
                            moneyline_processed = True
                
                # Flatten Corners arrays
                if not corners_processed and "Corners" in bookmaker_data:
                    corners_arrays = bookmaker_data["Corners"]
                    if isinstance(corners_arrays, list) and len(corners_arrays) > 0:
                        # Flatten first Corners array only
                        corners_array = corners_arrays[0]
                        if isinstance(corners_array, list) and len(corners_array) >= 8:
                            # Flatten Corners array to individual fields
                            extracted["corners_timestamp"] = corners_array[0]
                            extracted["corners_capture_time"] = corners_array[1]
                            extracted["corners_over_odds"] = corners_array[2]
                            extracted["corners_value_total_line"] = corners_array[3]
                            extracted["corners_under_odds"] = corners_array[4]
                            extracted["corners_match_status"] = corners_array[5]
                            # Skip index 6 - filtered per user request
                            extracted["corners_ratio"] = corners_array[7]
                            extracted["::::"] = ""
                            corners_processed = True
                
                # Exit early if all types processed
                if spread_processed and overunder_processed and moneyline_processed and corners_processed:
                    break
        
        # Include original odds structure after flattened fields
        extracted["odds"] = match["odds"]
    
    # Step 7: Process remaining fields (environment, var_incidents, etc.)
    for field_name, field_value in match.items():
        if field_name not in extracted and field_name not in {"match_id", "timestamp", "scheduled_time_readable", "competition", "teams", "details_status_id", "odds", "spread_score", "match_status"}:
            extracted[field_name] = field_value
    
    return extracted

def load_existing_log() -> Dict[str, Any]:
    """Load existing accumulating log or create new structure"""
    log_file = '/workspaces/TMUX_FINAL_SPORTS/logs/alerts/alerts.json'
    
    try:
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # Create new accumulating log structure
            return {
                "log_metadata": {
                    "total_fetches": 0,
                    "first_fetch": "",
                    "last_fetch": "",
                    "log_format": "accumulating_v1.0"
                },
                "fetch_history": []
            }
    except Exception as e:
        print(f"Error loading existing log: {e}")
        return {
            "log_metadata": {
                "total_fetches": 0,
                "first_fetch": "",
                "last_fetch": "",
                "log_format": "accumulating_v1.0"
            },
            "fetch_history": []
        }

def archive_old_fetches(accumulated_log: Dict[str, Any]) -> Dict[str, Any]:
    """Archive old fetches when exceeding 50 fetch limit"""
    max_history = 50
    
    if len(accumulated_log["fetch_history"]) > max_history:
        # Create archive directory
        archive_dir = '/workspaces/TMUX_FINAL_SPORTS/logs/alerts/archive'
        os.makedirs(archive_dir, exist_ok=True)
        
        # Archive excess fetches
        excess_fetches = accumulated_log["fetch_history"][:-max_history]
        ny_tz = pytz.timezone('US/Eastern')
        archive_timestamp = datetime.now(ny_tz).strftime('%Y%m%d_%H%M%S')
        archive_file = f"{archive_dir}/alerts_archive_{archive_timestamp}.json"
        
        archive_data = {
            "archive_metadata": {
                "archived_at": datetime.now(ny_tz).isoformat(),
                "archived_fetches": len(excess_fetches),
                "archive_reason": "50_fetch_rotation"
            },
            "archived_fetches": excess_fetches
        }
        
        with open(archive_file, 'w', encoding='utf-8') as f:
            json.dump(archive_data, f, indent=2, ensure_ascii=False)
        
        # Keep only last 50 fetches
        accumulated_log["fetch_history"] = accumulated_log["fetch_history"][-max_history:]
        accumulated_log["log_metadata"]["total_fetches"] = max_history
        accumulated_log["log_metadata"]["first_fetch"] = accumulated_log["fetch_history"][0]["fetch_timestamp"]
        
        print(f"Archived {len(excess_fetches)} old fetches to {archive_file}")
    
    return accumulated_log

def save_data(processed_matches: List[Dict[str, Any]]) -> bool:
    """Save data with accumulating log pattern and archive rotation"""
    
    # Load existing accumulating log
    accumulated_log = load_existing_log()
    
    # Get NY timezone
    ny_tz = pytz.timezone('US/Eastern')
    current_time = datetime.now(ny_tz)
    
    # Create new fetch entry
    new_fetch_entry = {
        "fetch_timestamp": current_time.isoformat(),
        "fetch_number": len(accumulated_log["fetch_history"]) + 1,
        "processed_data": {
            "matches": processed_matches,
            "total_matches": len(processed_matches)
        },
        "processing_metadata": {
            "source_file": "monitoring.json",
            "processing_time": current_time.strftime('%m/%d/%Y %I:%M:%S %p %Z'),
            "status": "success"
        }
    }
    
    # Add new fetch to history
    accumulated_log["fetch_history"].append(new_fetch_entry)
    
    # Update metadata
    accumulated_log["log_metadata"]["total_fetches"] = len(accumulated_log["fetch_history"])
    accumulated_log["log_metadata"]["last_fetch"] = current_time.isoformat()
    if accumulated_log["log_metadata"]["total_fetches"] == 1:
        accumulated_log["log_metadata"]["first_fetch"] = current_time.isoformat()
    
    # Archive old fetches if exceeding 50
    accumulated_log = archive_old_fetches(accumulated_log)
    
    # Ensure output directory exists
    output_dir = '/workspaces/TMUX_FINAL_SPORTS/logs/alerts'
    os.makedirs(output_dir, exist_ok=True)
    
    # Save accumulating log
    output_file = f'{output_dir}/alerts.json'
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(accumulated_log, f, indent=2, ensure_ascii=False)
        
        # MANDATORY: NY Eastern time footer (LAST LINE OF EVERY FETCH)
        ny_time_footer = current_time.strftime('%m/%d/%Y %I:%M:%S %p')
        print(f"✅ alerts.py completed: {ny_time_footer} EST")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to save data: {e}")
        return False

def trigger_next_stage():
    """Trigger next stage in pipeline: alerts_central.py"""
    try:
        subprocess.run([sys.executable, '/workspaces/TMUX_FINAL_SPORTS/alerts_central.py'], check=True)
        print("✅ Successfully triggered alerts_central.py")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to trigger alerts_central.py: {e}")

def main() -> int:
    """Main processing with field-by-field extraction"""
    print(f"🔄 Starting alerts processing...")
    
    # Load source data from previous stage
    source_data = load_monitoring_data()
    if not source_data:
        print("❌ Failed to load source data")
        return 1
    
    # Extract matches from accumulating log structure
    if "fetch_history" in source_data and source_data["fetch_history"]:
        # Get latest fetch from accumulating log
        latest_fetch = source_data["fetch_history"][-1]
        source_matches = latest_fetch.get("processed_data", {}).get("matches", [])
    else:
        # Fallback for non-accumulating log sources
        source_matches = source_data.get("matches", [])
    
    if not source_matches:
        print("❌ No matches found in source data")
        return 1
    
    print(f"📊 Processing {len(source_matches)} matches with field-by-field extraction...")
    
    # Process each match with systematic field extraction
    processed_matches = []
    for match in source_matches:
        if isinstance(match, dict):
            # MANDATORY: Field-by-field processing
            extracted_match = extract_match_fields(match)
            if extracted_match:
                processed_matches.append(extracted_match)
    
    # Save with accumulating log pattern
    if save_data(processed_matches):
        print(f"✅ Successfully processed {len(processed_matches)} matches")
        
        # Call next stage: alerts_central.py
        trigger_next_stage()
        
        return 0
    else:
        print("❌ Failed to save processed data")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)