#!/usr/bin/env python3

"""
ALERTS CENTRAL PIPELINE STAGE
==============================
Source: alerts.json (from alerts.py)
Purpose: Central data aggregation and analysis with independent field-by-field processing
Output: /workspaces/TMUX_FINAL_SPORTS/logs/alerts_central/alerts_central.json

RESOLUTION NOTE - Odds Structure Filtering Failure - 06/29/2025 06:25 EST:
Problem: User reported odds structures still appearing in alerts_central.json despite claimed filtering.
Root Cause: Catch-all loop in extract_match_fields() was passing through ALL remaining fields including 'odds' structure.
Solution: Added explicit filtering array ['odds'] to prevent odds structure from being passed through in the catch-all field processing loop.
Technical Fix: Fixed at lines 142-146 by adding filtered_out_fields=['odds'] condition to field processing loop.
Lesson: Always check catch-all loops for unintended pass-through when implementing field filtering.

FILTER IMPLEMENTATION - details_status_id Range Filter - 06/29/2025 06:28 EST:
Requirement: Filter out any matches with details_status_id outside the 2-10 range.
Analysis: Found details_status_id values: 2, 3, 4, 8, 9 (keep) and 13 (filter out - 179 records).
Implementation: Added status_id range check before field-by-field processing at lines 324-327.
Expected Result: ~179 records with status_id=13 will be filtered out, keeping ~1,415 records.

Architecture Compliance:
- Single source dependency: alerts.json only
- Field-by-field extraction: Every field consciously identified and processed
- Optional task assignment: Transform fields with tasks, pass-through fields without tasks
- Independent error handling: Self-contained error recovery
- Accumulating log pattern: 50-fetch rotation with archive management
- Self-contained logging: Hardcoded paths, independent directory management
"""

import json
import os
import sys
import subprocess
from datetime import datetime
from typing import Dict, List, Any, Optional
import pytz

def load_alerts_data() -> Optional[Dict[str, Any]]:
    """Load alerts.json data with error handling"""
    source_file = '/workspaces/TMUX_FINAL_SPORTS/logs/alerts/alerts.json'
    
    try:
        if os.path.exists(source_file):
            with open(source_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            print(f"ERROR: Source file not found: {source_file}")
            return None
    except Exception as e:
        print(f"ERROR: Failed to load alerts data: {e}")
        return None

def extract_match_fields(match: Dict[str, Any]) -> Dict[str, Any]:
    """Field-by-field extraction with optional task processing"""
    
    # Initialize extracted match with ordered structure
    extracted = {}
    
    # FIELD-BY-FIELD PROCESSING: Process every field consciously
    
    # Step 1: Basic match identification fields (no tasks - pass-through)
    for field_name in ["match_id", "timestamp", "scheduled_time_readable"]:
        if field_name in match:
            extracted[field_name] = match[field_name]
    
    # Step 2: Competition field (no task - pass-through)
    if "competition_name" in match:
        extracted["competition_name"] = match["competition_name"]
    
    # Step 3: Team fields (no tasks - pass-through) 
    for field_name in ["home_team_name", "away_team_name"]:
        if field_name in match:
            extracted[field_name] = match[field_name]
    
    # Step 4: Status field (no task - pass-through)
    if "details_status_id" in match:
        extracted["details_status_id"] = match["details_status_id"]
    
    # Step 5: Visual separator preservation (no task - pass-through)
    if "" in match:
        extracted[""] = match[""]
    
    # Step 6: Score fields (no tasks - pass-through)
    score_fields = ["home_score_current", "home_score_half", "home_corners", 
                   "away_score_current", "away_score_half", "away_corners"]
    for field_name in score_fields:
        if field_name in match:
            extracted[field_name] = match[field_name]
    
    # Step 7: Visual separators preservation (no tasks - pass-through)
    for separator in [" ", "  "]:
        if separator in match:
            extracted[separator] = match[separator]
    
    # Step 8: Flattened odds fields processing with interleaved colon separators (no tasks - pass-through with preservation)
    # PERMANENT RULE: Process odds groups in order: MoneyLine → Over/Under → Spread → Corners
    
    # Process MoneyLine fields (FIRST in the new order)
    moneyline_fields = ["moneyline_timestamp", "moneyline_capture_time", "moneyline_home",
                       "moneyline_draw", "moneyline_away", "moneyline_match_status", 
                       "moneyline_game_score"]
    for field_name in moneyline_fields:
        if field_name in match:
            extracted[field_name] = match[field_name]
    
    # Colon separator after moneyline_game_score
    if ":::" in match:
        extracted[":::"] = match[":::"]
    
    # Process over/under fields (SECOND in the new order)
    overunder_fields = ["overunder_timestamp", "overunder_capture_time", "overunder_over_odds",
                       "overunder_total_line", "overunder_under_odds", "overunder_match_status", 
                       "overunder_game_score"]
    for field_name in overunder_fields:
        if field_name in match:
            extracted[field_name] = match[field_name]
    
    # Colon separator after overunder_game_score
    if "::" in match:
        extracted["::"] = match["::"]
    
    # Process spread fields (THIRD in the new order)
    spread_fields = ["spread_timestamp", "spread_capture_time", "spread_home_odds", 
                    "spread_value", "spread_away_odds", "spread_match_status", "spread_game_score"]
    for field_name in spread_fields:
        if field_name in match:
            extracted[field_name] = match[field_name]
    
    # Colon separator after spread_game_score
    if ":" in match:
        extracted[":"] = match[":"]
    
    # Process Corners fields (FOURTH in the new order)
    corners_fields = ["corners_timestamp", "corners_capture_time", "corners_over_odds",
                     "corners_value_total_line", "corners_under_odds", "corners_match_status",
                     "corners_ratio"]
    for field_name in corners_fields:
        if field_name in match:
            extracted[field_name] = match[field_name]
    
    # Colon separator after corners_ratio
    if "::::" in match:
        extracted["::::"] = match["::::"]
    
    # Step 10: Original odds structure COMPLETELY FILTERED OUT
    # All odds markets (spread, Over/Under, MoneyLine, Corners) are now flattened to individual fields
    # The original nested odds structure is no longer needed - filtered out completely
    
    # Step 11: Array fields (no tasks - pass-through)
    array_fields = ["home_scores", "away_scores", "var_incidents"]
    for field_name in array_fields:
        if field_name in match:
            extracted[field_name] = match[field_name]
    
    # Step 12: Environment field (no task - pass-through)
    if "environment" in match:
        extracted["environment"] = match["environment"]
    
    # Step 13: Process any remaining fields not explicitly handled (EXCLUDING odds structure and flattened fields)
    # CRITICAL FILTER: odds structure and all explicitly processed flattened fields filtered permanently
    filtered_out_fields = ["odds", "moneyline_timestamp", "moneyline_capture_time", "moneyline_home",
                          "moneyline_draw", "moneyline_away", "moneyline_match_status", "moneyline_game_score",
                          "overunder_timestamp", "overunder_capture_time", "overunder_over_odds",
                          "overunder_total_line", "overunder_under_odds", "overunder_match_status", 
                          "overunder_game_score", "spread_timestamp", "spread_capture_time", "spread_home_odds", 
                          "spread_value", "spread_away_odds", "spread_match_status", "spread_game_score",
                          "corners_timestamp", "corners_capture_time", "corners_over_odds",
                          "corners_value_total_line", "corners_under_odds", "corners_match_status",
                          "corners_ratio", ":", "::", ":::", "::::"]
    
    for field_name, field_value in match.items():
        if field_name not in extracted and field_name not in filtered_out_fields:
            # No task assigned - pass-through preservation
            extracted[field_name] = field_value
    
    return extracted

def load_existing_log() -> Dict[str, Any]:
    """Load existing accumulating log or create new structure"""
    log_file = '/workspaces/TMUX_FINAL_SPORTS/logs/alerts_central/alerts_central.json'
    
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
        archive_dir = '/workspaces/TMUX_FINAL_SPORTS/logs/alerts_central/archive'
        os.makedirs(archive_dir, exist_ok=True)
        
        # Archive excess fetches
        excess_fetches = accumulated_log["fetch_history"][:-max_history]
        ny_tz = pytz.timezone('US/Eastern')
        archive_timestamp = datetime.now(ny_tz).strftime('%Y%m%d_%H%M%S')
        archive_file = f"{archive_dir}/alerts_central_archive_{archive_timestamp}.json"
        
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

def save_data(processed_matches: List[Dict[str, Any]], total_inplay_count: int, source_total_matches: int) -> bool:
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
            "total_matches": source_total_matches,
            "total_inplay_matches": total_inplay_count
        },
        "processing_metadata": {
            "source_file": "alerts.json",
            "processing_time": current_time.strftime('%m/%d/%Y %I:%M:%S %p %Z'),
            "status": "success",
            "pipeline_stage": "alerts_central"
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
    output_dir = '/workspaces/TMUX_FINAL_SPORTS/logs/alerts_central'
    os.makedirs(output_dir, exist_ok=True)
    
    # Save accumulating log
    output_file = f'{output_dir}/alerts_central.json'
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(accumulated_log, f, indent=2, ensure_ascii=False)
        
        # MANDATORY: NY Eastern time footer (LAST LINE OF EVERY FETCH)
        ny_time_footer = current_time.strftime('%m/%d/%Y %I:%M:%S %p')
        print(f"✅ alerts_central.py completed: {ny_time_footer} EST")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to save data: {e}")
        return False

def trigger_next_stage():
    """Trigger next stage in pipeline - currently terminal stage"""
    # alerts_central.py is currently terminal - no next stage to trigger
    # Uncomment when adding next stage:
    # try:
    #     subprocess.run([sys.executable, '/workspaces/TMUX_FINAL_SPORTS/next_stage.py'], check=True)
    #     print("✅ Successfully triggered next stage")
    # except subprocess.CalledProcessError as e:
    #     print(f"❌ Failed to trigger next stage: {e}")
    pass

def main() -> int:
    """Main processing with field-by-field extraction"""
    print(f"🔄 Starting alerts_central processing...")
    
    # Load source data from alerts.py
    source_data = load_alerts_data()
    if not source_data:
        print("❌ Failed to load alerts data")
        return 1
    
    # Extract matches from accumulating log structure
    if "fetch_history" in source_data and source_data["fetch_history"]:
        # Get latest fetch from accumulating log
        latest_fetch = source_data["fetch_history"][-1]
        source_matches = latest_fetch.get("processed_data", {}).get("matches", [])
        source_total_matches = latest_fetch.get("processed_data", {}).get("total_matches", len(source_matches))
    else:
        # Fallback for non-accumulating log sources
        source_matches = source_data.get("matches", [])
        source_total_matches = len(source_matches)
    
    if not source_matches:
        print("❌ No matches found in source data")
        return 1
    
    print(f"📊 Processing {len(source_matches)} matches with field-by-field extraction...")
    
    # Process each match with systematic field extraction
    processed_matches = []
    total_inplay_count = 0  # Count matches with in-play status IDs (2, 3, 4)
    
    for match in source_matches:
        if isinstance(match, dict):
                    # Filter by details_status_id range (2-10 only, excluding 8)
            # IMPORTANT: Only details_status_id is used for filtering. The following status fields are IGNORED:
            # - moneyline_match_status (from flattened moneyline array)
            # - corners_match_status (from flattened corners array)
            # - overunder_match_status (from flattened overunder array)  
            # - spread_match_status (from flattened spread array)
            # These are data fields only and do not affect match qualification for processing.
            status_id = match.get("details_status_id")
            if status_id is not None and (status_id < 2 or status_id > 10 or status_id == 8):
                continue  # Skip matches outside 2-10 range and status_id = 8
            
            # Count in-play matches (status IDs 2, 3, 4 within the filter range)
            if status_id in [2, 3, 4]:
                total_inplay_count += 1
            
            # MANDATORY: Field-by-field processing
            extracted_match = extract_match_fields(match)
            if extracted_match:
                processed_matches.append(extracted_match)
    
    # Save with accumulating log pattern
    if save_data(processed_matches, total_inplay_count, source_total_matches):
        print(f"✅ Successfully processed {len(processed_matches)} matches")
        
        # Call next stage if not terminal
        trigger_next_stage()
        
        return 0
    else:
        print("❌ Failed to save processed data")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)