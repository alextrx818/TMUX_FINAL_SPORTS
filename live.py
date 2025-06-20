#!/usr/bin/env python3

# ========================================
# IDENTIFIER REFERENCE - LIVE.PY
# ========================================
# INPUT IDs: None (global endpoint)
# OUTPUT IDs: id (match_id) -> details.py, odds.py
# PIPELINE: live.py -> match_id -> details.py, odds.py
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
                    
                    # RAW JSON DUMP with timestamp
                    import pytz
                    ny_tz = pytz.timezone('US/Eastern')
                    ny_time = datetime.now(ny_tz)
                    timestamp = ny_time.strftime('%m/%d/%Y %I:%M:%S %p')
                    data_with_timestamp = {
                        "api_response": data,
                        "fetch_timestamp": f"{timestamp} EST"
                    }
                    with open('/workspaces/TMUX_FINAL_SPORTS/logs/live/live.json', 'w') as f:
                        json.dump(data_with_timestamp, f, indent=2)
                    
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