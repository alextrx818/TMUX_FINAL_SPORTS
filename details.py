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
# PIPELINE CALLING STANDARD - DETAILS.PY
# ========================================
# POSITION: live.py → details.py → teams.py + competitions.py + countries.py → merge.py
# CALLS NEXT: trigger_next_stage() → subprocess.run(['python3', 'teams.py'], check=True)
#                                  → subprocess.run(['python3', 'competitions.py'], check=True)
#                                  → subprocess.run(['python3', 'countries.py'], check=True)
#                                  → subprocess.run(['python3', 'merge.py'], check=True)
# PATTERN: Standard pipeline pattern with try/except CalledProcessError handling
# ========================================

# ========================================
# IDENTIFIER REFERENCE - DETAILS.PY
# ========================================
# INPUT IDs: match_id (from live.py) -> used as 'uuid' parameter
# OUTPUT IDs: home_team_id, away_team_id -> teams.py | competition_id -> competitions.py
# PIPELINE: live.py -> match_id -> details.py -> team_ids, competition_id -> teams.py, competitions.py
# ========================================

"""
Fetches detailed match information from /match/recent/list
Extracts team and competition IDs for next stage

JSON Schema Reference - /match/recent/list (VALIDATED & CONFIRMED):
{
  "code": "integer",
  "query": {
    "total": "integer",           // Total amount of data returned
    "type": "string",             // Query type: "uuid", "page", "time", default "page"
    "uuid": "string",             // UUID query value (exists for uuid queries)
    "page": "integer",            // Page query value (exists for page queries)
    "time": "integer",            // Time query value, timestamp format (exists for time queries)
    "min_time": "integer",        // Smallest time in data (updated_at value, time queries)
    "max_time": "integer"         // Largest time in data (updated_at value, time queries)
  },
  "results": [
    {
      "id": "string",             // Match id
      "season_id": "string",      // Season id
      "competition_id": "string", // Competition id  
      "home_team_id": "string",   // Home team id
      "away_team_id": "string",   // Away team id
      "status_id": "integer",     // Match status (see Status Code -> Match Status)
      "match_time": "integer",    // Match time (timestamp)
      "venue_id": "string",       // Venue id
      "referee_id": "string",     // Referee id
      "neutral": "integer",       // Is neutral venue: 1=Yes, 0=No
      "note": "string",           // Remarks
      "home_scores": [            // Home team scores array[7]
        "integer",                // [0] Score (regular time)
        "integer",                // [1] Halftime score
        "integer",                // [2] Red cards
        "integer",                // [3] Yellow cards
        "integer",                // [4] Corners (-1 means no data)
        "integer",                // [5] Overtime score (120 min, including regular)
        "integer"                 // [6] Penalty shootout score
      ],
      "away_scores": [            // Away team scores array[7]
        "integer",                // [0] Score (regular time)
        "integer",                // [1] Halftime score
        "integer",                // [2] Red cards
        "integer",                // [3] Yellow cards
        "integer",                // [4] Corners (-1 means no data)
        "integer",                // [5] Overtime score (120 min, including regular)
        "integer"                 // [6] Penalty shootout score
      ],
      "home_position": "string",  // Home team ranking
      "away_position": "string",  // Away team ranking
      "coverage": {
        "mlive": "integer",       // Has animation: 1=yes, 0=no
        "lineup": "integer"       // Has lineup: 1=yes, 0=no
      },
      "round": {
        "stage_id": "string",     // Stage id
        "group_num": "integer",   // Group number: 1=A, 2=B, etc.
        "round_num": "integer"    // Round number
      },
      "related_id": "string",     // Match id of other round in double round (optional)
      "agg_score": [              // Total score of two rounds (optional)
        "integer",                // [0] Home team aggregate score
        "integer"                 // [1] Away team aggregate score
      ],
      "environment": {            // Match environment (if data available)
        "weather": "integer",     // Weather id (1=Partially cloudy, 2=Cloudy, etc.)
        "pressure": "string",     // Air pressure (e.g., "768mmHg")
        "temperature": "string",  // Temperature (e.g., "12°C")
        "wind": "string",         // Wind speed (e.g., "3.4m/s")
        "humidity": "string"      // Humidity (e.g., "77%")
      },
      "tbd": "integer",           // Time to be determined: 1=Yes (optional)
      "has_ot": "integer",        // Has overtime: 1=Yes (optional)
      "ended": "integer",         // End time (optional)
      "team_reverse": "integer",  // Host/away positions opposite: 1=Yes (optional)
      "updated_at": "integer"     // Update time (timestamp)
    }
  ]
}

EXAMPLE RESPONSE (CONFIRMED - 2024-06-18):
{
  "code": 0,
  "query": {"total": 1, "type": "uuid", "uuid": "3glrw7hnw74wqdy"},
  "results": [{
    "id": "3glrw7hnw74wqdy",
    "season_id": "gy0or5jhv9pqwzv",
    "competition_id": "v2y8m4zhydql074",
    "home_team_id": "y0or5jh4njpqwzv",
    "away_team_id": "p3glrw7hv1wqdyj",
    "status_id": 2,
    "match_time": 1750278600,
    "home_scores": [0,0,0,0,0,0,0],
    "away_scores": [0,0,0,0,0,0,0],
    "coverage": {"mlive": 1, "lineup": 1},
    "round": {"stage_id": "y0or5jhwwwxqwzv", "round_num": 5, "group_num": 0},
    "environment": {"weather": 8, "pressure": "768mmHg", "temperature": "12°C", "wind": "3.4m/s", "humidity": "77%"},
    "updated_at": 1750278625
  }]
}

# ✅ DETAILS.PY - CONFIRMED PATCH & SCHEMA - DO NOT MODIFY

EXTRACTED IDENTIFIERS FOR PIPELINE REFERENCE:
============================================
INPUT IDENTIFIERS (Required for this endpoint):
- match_id (from live.py) -> used as 'uuid' parameter

OUTPUT IDENTIFIERS (Available for subsequent endpoints):
- home_team_id -> use in teams.py
- away_team_id -> use in teams.py  
- competition_id -> use in competitions.py
- season_id -> future use
- venue_id -> future use
- referee_id -> future use
- stage_id (in round object) -> future use

EXAMPLE ID EXTRACTION FROM CONFIRMED RESPONSE:
- home_team_id: "y0or5jh4njpqwzv"
- away_team_id: "p3glrw7hv1wqdyj"
- competition_id: "v2y8m4zhydql074"
- season_id: "gy0or5jhv9pqwzv"
- venue_id: "kn54qllhk01qvy9"
- referee_id: "gpxwrxlh217ryk0"
- stage_id: "y0or5jhwwwxqwzv"

PIPELINE FLOW:
live.py -> match_id -> details.py -> home_team_id, away_team_id, competition_id -> teams.py, competitions.py
"""

import asyncio
import aiohttp
import os
import json
import subprocess
from typing import List, Dict, Any, Set

async def fetch_match_details(match_id: str) -> Dict[str, Any]:
    """Fetch detailed match info for a specific match ID"""
    
    
    user = os.getenv('THESPORTS_USER')
    secret = os.getenv('THESPORTS_SECRET')
    
    url = "https://api.thesports.com/v1/football/match/recent/list"
    params = {
        'user': user,
        'secret': secret,
        'uuid': match_id
    }
    
    request_data = {
        "url": url,
        "method": "GET",
        "params": {"user": "***", "secret": "***", "uuid": match_id}
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if 'err' in data:
                        error_msg = f"API Error for match {match_id}: {data['err']}"
                        print(error_msg)
                        return {}
                    
                    results = data.get('results', [])
                    if results:
                        return results[0]  # First element as per spec
                    else:
                        error_msg = f"No results for match {match_id}"
                    
                return {}
        except Exception as e:
            error_msg = f"Request failed for match {match_id}: {e}"
            print(error_msg)
            return {}

async def process_match_details():
    """Load match IDs and fetch detailed info for each"""
    
    try:
        with open('/tmp/live_matches.json', 'r') as f:
            live_data = json.load(f)
        # Handle both old format (direct array) and new format (with timestamp)
        if isinstance(live_data, list):
            live_matches = live_data
        else:
            live_matches = live_data.get('matches', [])
    except FileNotFoundError:
        print("No live matches file found")
        return
    
    match_ids = [match.get('id') for match in live_matches if match.get('id')]
    
    if not match_ids:
        print("No match IDs to process")
        return
    
    print(f"Fetching details for {len(match_ids)} matches...")
    
    # Create semaphore to limit concurrent requests
    semaphore = asyncio.Semaphore(30)
    
    async def fetch_with_semaphore(match_id):
        async with semaphore:
            return await fetch_match_details(match_id)
    
    # Fetch all match details concurrently
    tasks = [fetch_with_semaphore(match_id) for match_id in match_ids]
    match_details = await asyncio.gather(*tasks)
    
    # Extract unique team and competition IDs
    team_ids: Set[str] = set()
    competition_ids: Set[str] = set()
    
    valid_details = []
    for detail in match_details:
        if detail:
            valid_details.append(detail)
            
            # Extract team IDs
            if 'home_team_id' in detail:
                team_ids.add(str(detail['home_team_id']))
            if 'away_team_id' in detail:
                team_ids.add(str(detail['away_team_id']))
            
            # Extract competition ID
            if 'competition_id' in detail:
                competition_ids.add(str(detail['competition_id']))
    
    print(f"Processed {len(valid_details)} match details")
    print(f"Found {len(team_ids)} unique teams: {list(team_ids)[:5]}...")
    print(f"Found {len(competition_ids)} unique competitions: {list(competition_ids)}")
    
    # Write new data with timestamp
    from datetime import datetime
    import pytz
    
    ny_tz = pytz.timezone('US/Eastern')
    ny_time = datetime.now(ny_tz)
    timestamp = ny_time.strftime('%m/%d/%Y %I:%M:%S %p')
    
    details_file = '/workspaces/TMUX_FINAL_SPORTS/logs/details/details.json'
    
    data_with_timestamp = {
        "api_response": valid_details,
        "fetch_timestamp": f"{timestamp} EST",
        "footer_completion": f"--- Details.py fetch completed: {timestamp} EST ---"
    }
    with open(details_file, 'w') as f:
        json.dump(data_with_timestamp, f, indent=2)
    
    # Save data for next stages
    with open('/tmp/match_details.json', 'w') as f:
        json.dump(valid_details, f)
    
    with open('/tmp/team_ids.json', 'w') as f:
        json.dump(list(team_ids), f)
    
    with open('/tmp/competition_ids.json', 'w') as f:
        json.dump(list(competition_ids), f)
    
    trigger_next_stage()

def trigger_next_stage():
    """Call teams and competitions fetchers, then merge all data"""
    print("Triggering team and competition fetching...")
    
    try:
        subprocess.run(['python3', 'teams.py'], check=True)
        subprocess.run(['python3', 'competitions.py'], check=True)
        subprocess.run(['python3', 'countries.py'], check=True)
        
        # Final step: merge all pipeline data
        print("Triggering final data merge...")
        subprocess.run(['python3', 'merge.py'], check=True)
        print("✅ Complete pipeline finished - merge.py executed successfully")
        
    except subprocess.CalledProcessError as e:
        print(f"Error calling next stage: {e}")

async def main():
    """Main entry point"""
    print("Starting match details fetch...")
    await process_match_details()
    print("Details fetch completed")

if __name__ == "__main__":
    asyncio.run(main())

# NY Eastern Time Footer
from datetime import datetime
import pytz
ny_tz = pytz.timezone('US/Eastern')
ny_time = datetime.now(ny_tz)
print(f"\n--- Generated: {ny_time.strftime('%m/%d/%Y %I:%M %p')} EST ---")