#!/usr/bin/env python3

# ========================================
# CENTRALIZED LOGGING SYSTEM REMOVAL NOTE
# ========================================
# This project previously used a centralized logging system with shared configuration files
# (logging_utils.py, loggingconfig.py, etc.) that was removed due to path confusion and
# complexity. Each endpoint file now contains its own independent, hardcoded logging logic
# that is specific to that file's requirements. No centralized logging imports remain.
# ========================================

# ========================================
# PIPELINE CALLING STANDARD - LIVE.PY
# ========================================
# POSITION: Entry point → details.py + odds.py (parallel)
# CALLS NEXT: trigger_next_stage() → subprocess.run(['python3', 'details.py'], check=True)
#                                  → subprocess.run(['python3', 'odds.py'], check=True)
# PATTERN: Standard pipeline pattern with try/except CalledProcessError handling
# ========================================

# ========================================
# IDENTIFIER REFERENCE - LIVE.PY
# ========================================
# INPUT IDs: None (global endpoint)
# OUTPUT IDs: id (match_id) -> details.py, odds.py
# PIPELINE: live.py -> match_id -> details.py, odds.py
# ========================================

# ========================================
# VAR (VIDEO ASSISTANT REFEREE) CODE DEFINITIONS
# ========================================
# VAR incidents appear in incidents[] array with "type": 28
# 
# var_reason (WHY VAR was triggered):
# 1 = Goal awarded
# 2 = Goal not awarded  
# 3 = Penalty awarded
# 4 = Penalty not awarded
# 5 = Red card given
# 6 = Card upgrade
# 7 = Mistaken identity
# 0 = Other
#
# var_result (WHAT the VAR decision was):
# 1 = Goal confirmed
# 2 = Goal cancelled
# 3 = Penalty confirmed
# 4 = Penalty cancelled
# 5 = Red card confirmed
# 6 = Red card cancelled
# 7 = Card upgrade confirmed
# 8 = Card upgrade cancelled
# 9 = Original decision
# 10 = Original decision changed
# 0 = Unknown
# ========================================

"""
Main entry point - fetches live match data from /match/detail_live
Extracts match IDs and triggers the next stage of the pipeline

JSON Schema Reference - /match/detail_live (VALIDATED & CONFIRMED):
{
  "code": "integer",
  "results": [
    {
      "id": "string",           // Match id (e.g., "3glrw7hnw74wqdy")
      "score": [                // Array[6] containing match details
        "string",               // [0] Match id (duplicate of above)
        "integer",              // [1] Match status (2=live, 3=finished, etc.)
        [                       // [2] Home team stats array[7]
          "integer",            // [0] Home Team Score (regular time)
          "integer",            // [1] Home Team Halftime score  
          "integer",            // [2] Home Team Red cards
          "integer",            // [3] Home Team Yellow cards
          "integer",            // [4] Home Team Corners (-1 means no data)
          "integer",            // [5] Home Team Overtime score (120 min)
          "integer"             // [6] Home Team Penalty shootout score
        ],
        [                       // [3] Away team stats array[7] 
          "integer",            // [0] Away Team Score (regular time)
          "integer",            // [1] Away Team Halftime score
          "integer",            // [2] Away Team Red cards  
          "integer",            // [3] Away Team Yellow cards
          "integer",            // [4] Away Team Corners (-1 means no data)
          "integer",            // [5] Away Team Overtime score (120 min)
          "integer"             // [6] Away Team Penalty shootout score
        ],
        "integer",              // [4] Kick-off timestamp (e.g., 1750278547)
        "string"                // [5] Compatible ignore (usually empty string)
      ],
      "stats": [                // Array of match statistics
        {
          "type": "integer",    // Stat type (4=shots, 25=possession%, etc.)
          "home": "integer",    // Home team value
          "away": "integer"     // Away team value
        }
      ],
      "incidents": [],          // Array of match events (goals, cards, etc.)
      "tlive": []              // Array of live text commentary
    }
  ]
}

EXAMPLE RESPONSE (CONFIRMED - 2024-06-18):
{
  "id": "3glrw7hnw74wqdy",
  "score": ["3glrw7hnw74wqdy", 2, [0,0,0,0,0,0,0], [0,0,0,0,0,0,0], 1750278547, ""],
  "stats": [{"type": 25, "home": 48, "away": 52}],  // Possession 48%-52%
  "incidents": [],
  "tlive": []
}

# ✅ LIVE.PY - CONFIRMED PATCH & SCHEMA - DO NOT MODIFY

EXTRACTED IDENTIFIERS FOR PIPELINE REFERENCE:
============================================
INPUT IDENTIFIERS (Required for this endpoint):
- None (global live matches endpoint)

OUTPUT IDENTIFIERS (Available for subsequent endpoints):
- id -> use as match_id in details.py and odds.py
- Additional IDs in score array (but use main 'id' field)

EXAMPLE ID EXTRACTION FROM CONFIRMED RESPONSE:
- id: "3glrw7hnw74wqdy" -> primary match identifier

PIPELINE FLOW:
live.py -> id (match_id) -> details.py, odds.py
"""

import asyncio
import aiohttp
import os
import json
import subprocess
from typing import List, Dict, Any
from datetime import datetime

async def fetch_live_matches() -> List[Dict[str, Any]]:
    """Fetch live match data from /match/detail_live endpoint"""
    
    user = os.getenv('THESPORTS_USER')
    secret = os.getenv('THESPORTS_SECRET')
    
    if not user or not secret:
        print(f"ERROR: THESPORTS_USER and THESPORTS_SECRET environment variables required")
        return []
    
    url = "https://api.thesports.com/v1/football/match/detail_live"
    params = {
        'user': user,
        'secret': secret
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # ACCUMULATING JSON DUMP with historical preservation
                    import pytz
                    ny_tz = pytz.timezone('US/Eastern')
                    ny_time = datetime.now(ny_tz)
                    timestamp = ny_time.strftime('%m/%d/%Y %I:%M:%S %p')
                    
                    # Create new fetch entry
                    new_fetch_entry = {
                        "fetch_id": ny_time.strftime('%Y%m%d_%H%M%S'),
                        "api_response": data,
                        "fetch_timestamp": f"{timestamp} EST",
                        "match_count": len(data.get('results', [])),
                        "fetch_unix_time": int(ny_time.timestamp())
                    }
                    
                    live_log_file = '/workspaces/TMUX_FINAL_SPORTS/logs/live/live.json'
                    
                    # Load existing accumulating log or create new structure
                    try:
                        if os.path.exists(live_log_file):
                            with open(live_log_file, 'r') as f:
                                existing_log = json.load(f)
                            # Handle migration from old format
                            if "fetch_history" not in existing_log:
                                # Convert old format to new accumulating format
                                old_entry = {
                                    "fetch_id": "migration_" + ny_time.strftime('%Y%m%d_%H%M%S'),
                                    "api_response": existing_log.get("api_response", {}),
                                    "fetch_timestamp": existing_log.get("fetch_timestamp", "Migration Entry"),
                                    "match_count": len(existing_log.get("api_response", {}).get("results", [])),
                                    "fetch_unix_time": int(ny_time.timestamp()) - 60  # 1 minute earlier
                                }
                                accumulated_log = {
                                    "log_metadata": {
                                        "total_fetches": 1,
                                        "first_fetch": old_entry["fetch_timestamp"],
                                        "last_fetch": new_fetch_entry["fetch_timestamp"],
                                        "log_format": "accumulating_v1.0"
                                    },
                                    "fetch_history": [old_entry]
                                }
                            else:
                                accumulated_log = existing_log
                        else:
                            # Create new accumulating log structure
                            accumulated_log = {
                                "log_metadata": {
                                    "total_fetches": 0,
                                    "first_fetch": new_fetch_entry["fetch_timestamp"],
                                    "last_fetch": new_fetch_entry["fetch_timestamp"],
                                    "log_format": "accumulating_v1.0"
                                },
                                "fetch_history": []
                            }
                    except Exception as e:
                        print(f"Error loading existing log, creating fresh: {e}")
                        accumulated_log = {
                            "log_metadata": {
                                "total_fetches": 0,
                                "first_fetch": new_fetch_entry["fetch_timestamp"],
                                "last_fetch": new_fetch_entry["fetch_timestamp"],
                                "log_format": "accumulating_v1.0"
                            },
                            "fetch_history": []
                        }
                    
                    # Add new fetch to history
                    accumulated_log["fetch_history"].append(new_fetch_entry)
                    
                    # Update metadata
                    accumulated_log["log_metadata"]["total_fetches"] = len(accumulated_log["fetch_history"])
                    accumulated_log["log_metadata"]["last_fetch"] = new_fetch_entry["fetch_timestamp"]
                    if accumulated_log["log_metadata"]["total_fetches"] == 1:
                        accumulated_log["log_metadata"]["first_fetch"] = new_fetch_entry["fetch_timestamp"]
                    
                    # Keep only last 100 fetches to prevent file size explosion (configurable)
                    max_history = 100
                    if len(accumulated_log["fetch_history"]) > max_history:
                        accumulated_log["fetch_history"] = accumulated_log["fetch_history"][-max_history:]
                        accumulated_log["log_metadata"]["total_fetches"] = max_history
                        accumulated_log["log_metadata"]["first_fetch"] = accumulated_log["fetch_history"][0]["fetch_timestamp"]
                        print(f"Rotated log history, keeping last {max_history} fetches")
                    
                    # Save accumulated log
                    with open(live_log_file, 'w') as f:
                        json.dump(accumulated_log, f, indent=2)
                    
                    print(f"Accumulated fetch #{accumulated_log['log_metadata']['total_fetches']} - {len(data.get('results', []))} matches")
                    
                    if 'err' in data:
                        print(f"API Error: {data['err']}")
                        return []
                    
                    matches = data.get('results', [])
                    print(f"Fetched {len(matches)} live matches")
                    
                    # Extract match IDs for next stage
                    match_ids = [match.get('id') for match in matches if match.get('id')]
                    print(f"Found {len(match_ids)} match IDs: {match_ids[:5]}...")
                    
                    return matches
                else:
                    print(f"HTTP Error: {response.status}")
                    return []
                    
        except Exception as e:
            print(f"Request failed: {e}")
            return []

def trigger_next_stage(match_data: List[Dict[str, Any]]):
    """Call the next files in the pipeline"""
    if not match_data:
        print("No match data to process")
        return
    
    # Add timestamp to the data
    from datetime import datetime
    import pytz
    ny_tz = pytz.timezone('US/Eastern')
    ny_time = datetime.now(ny_tz)
    
    # Create data with timestamp at the end
    live_data_with_timestamp = {
        "matches": match_data,
        "fetch_completed": {
            "timestamp": ny_time.strftime('%m/%d/%Y %I:%M:%S %p'),
            "timezone": "NYC",
            "total_matches": len(match_data),
            "endpoint": "live.py",
            "status": "success"
        }
    }
    
    # Save match data with timestamp for next stages
    with open('/tmp/live_matches.json', 'w') as f:
        json.dump(live_data_with_timestamp, f, indent=2)
    
    print("Triggering details and odds fetching...")
    
    # Call details.py and odds.py (they will run in parallel)
    try:
        subprocess.run(['python3', 'details.py'], check=True)
        subprocess.run(['python3', 'odds.py'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error calling next stage: {e}")

async def main():
    """Main entry point"""
    print("Starting live match fetch...")
    
    live_matches = await fetch_live_matches()
    
    if live_matches:
        trigger_next_stage(live_matches)
        print("Live fetch completed successfully")
    else:
        print("Live fetch failed")

if __name__ == "__main__":
    asyncio.run(main())

# Live Match Data Fetch Completion - New York Standard Time
from datetime import datetime
import pytz
ny_tz = pytz.timezone('US/Eastern')
ny_time = datetime.now(ny_tz)
print(f"\n--- Live.py fetch completed: {ny_time.strftime('%m/%d/%Y %I:%M %p')} NYC ---")
print(f"--- Live matches data saved to live.json: {ny_time.strftime('%m/%d/%Y %I:%M:%S %p')} ---")