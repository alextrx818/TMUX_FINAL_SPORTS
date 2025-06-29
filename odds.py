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
# IDENTIFIER REFERENCE - ODDS.PY
# ========================================
# INPUT IDs: match_id (from live.py) -> used as 'uuid' parameter
# OUTPUT IDs: company_id (keys) -> future reference for bookmaker info
# PIPELINE: live.py -> match_id -> odds.py -> company_id data
# ========================================

# ─────────────────────────  ODDS FIELD MAP  ──────────────────────────
# Each key is the market type returned by /odds/history.
# Value = dict with:
#   • 'label'   – plain-English market name
#   • 'columns' – the sequence of figures returned by the API (array positions 2,3,4)
#   • 'notes'   – quick reminder of what each column means
# VERIFIED AGAINST REAL API DATA: 2024-06-18
ODDS_FIELD_MAP = {
    "asia": {  # Asian-Handicap market (positions 2,3,4 in array[8])
        "label":   "Asian Handicap (Spread)",
        "columns": ["home_odds", "handicap", "away_odds"],
        "notes":   "Home win price, goal spread (+ = home gives goals, – = away gives), Away win price"
    },
    "eu": {  # 1×2 / Money-line market (positions 2,3,4 in array[8])
        "label":   "European 1×2 (Money-line)",
        "columns": ["home_odds", "draw_odds", "away_odds"],
        "notes":   "Decimal odds for outright Home win, Draw, Away win"
    },
    "bs": {  # Goals Over / Under (positions 2,3,4 in array[8])
        "label":   "Total Goals (Over / Under)",
        "columns": ["over_odds", "total", "under_odds"],
        "notes":   "Price for Over, goal-line, price for Under"
    },
    "cr": {  # Corner-kick totals (positions 2,3,4 in array[8])
        "label":   "Total Corners (Over / Under)",
        "columns": ["over_odds", "total", "under_odds"],
        "notes":   "Same layout as 'bs' but handicap = total corners"
    }
}
# CONFIRMED EXAMPLES FROM API:
# asia: [timestamp, "20", 1.05, 0.75, 0.75, 2, 0, "0-0"] -> home_odds=1.05, handicap=0.75, away_odds=0.75
# eu:   [timestamp, "20", 1.8, 3.25, 5.0, 2, 0, "0-0"]   -> home_odds=1.8, draw_odds=3.25, away_odds=5.0
# bs:   [timestamp, "21", 1.0, 2.0, 0.8, 2, 0, "0-0"]    -> over_odds=1.0, total=2.0, under_odds=0.8
# cr:   [timestamp, "19", 1.0, 9.5, 0.72, 2, 0, "1-1"]   -> over_odds=1.0, total=9.5, under_odds=0.72
# ─────────────────────────────────────────────────────────────────────

"""
Fetches odds history from /odds/history for each match
Processes bookmaker odds data (asia, eu, bs, cr arrays)

JSON Schema Reference - /odds/history (VALIDATED & CONFIRMED):
{
  "code": "integer",
  "results": {
    "company_id": {              // Key is odds company id (see status code -> Odds Company ID)
      "asia": [                  // Asia handicap odds array (see ODDS_FIELD_MAP above)
        [                        // Asia compensation data array[8]
          "integer",             // [0] Change time (timestamp)
          "string",              // [1] Time of match (empty before start)
          "float",               // [2] Home win odds (home_odds)
          "float",               // [3] Handicap (positive=home lets away, negative=away lets home)
          "float",               // [4] Away win odds (away_odds)
          "integer",             // [5] Match status (see Status Code -> Match Status)
          "integer",             // [6] Sealed disk: 0=No, 1=Yes
          "string"               // [7] Score: "home-away"
        ]
      ],
      "eu": [                    // European 1X2 odds array (see ODDS_FIELD_MAP above)
        [                        // Euro compensation data array[8]
          "integer",             // [0] Change time (timestamp)
          "string",              // [1] Time of match (empty before start)
          "float",               // [2] Home win odds (home_odds)
          "float",               // [3] Draw odds (draw_odds)
          "float",               // [4] Away win odds (away_odds)
          "integer",             // [5] Match status (see Status Code -> Match Status)
          "integer",             // [6] Sealed disk: 0=No, 1=Yes
          "string"               // [7] Score: "home-away"
        ]
      ],
      "bs": [                    // Over/Under (Big/Small) odds array (see ODDS_FIELD_MAP above)
        [                        // Size ball data array[8]
          "integer",             // [0] Change time (timestamp)
          "string",              // [1] Time of match (empty before start)
          "float",               // [2] Over odds (over_odds)
          "float",               // [3] Handicap line (total)
          "float",               // [4] Under odds (under_odds)
          "integer",             // [5] Match status (see Status Code -> Match Status)
          "integer",             // [6] Sealed disk: 0=No, 1=Yes
          "string"               // [7] Score: "home-away"
        ]
      ],
      "cr": [                    // Corner kicks odds array (see ODDS_FIELD_MAP above)
        [                        // Corner data array[8]
          "integer",             // [0] Change time (timestamp)
          "string",              // [1] Time of match (empty before start)
          "float",               // [2] Over odds (over_odds)
          "float",               // [3] Handicap line (total)
          "float",               // [4] Under odds (under_odds)
          "integer",             // [5] Match status (see Status Code -> Match Status)
          "integer",             // [6] Sealed disk: 0=No, 1=Yes
          "string"               // [7] Corner ratio: "home-away"
        ]
      ]
    }
  }
}

EXAMPLE RESPONSE (CONFIRMED - 2024-06-18):
{
  "code": 0,
  "results": {
    "2": {                       // Company ID 2
      "asia": [[1750279256, "12", 0.95, 0.75, 0.85, 2, 0, "0-0"]],
      "eu": [[1750279256, "12", 1.72, 3.4, 4.5, 2, 0, "0-0"]],
      "bs": [[1750279343, "14", 0.9, 2.0, 0.9, 2, 0, "0-0"]],
      "cr": [[1750279336, "14", 0.8, 7.5, 1.0, 2, 0, "0-0"]]
    },
    "3": { /* Company ID 3 data */ },
    "4": { /* Company ID 4 data */ }
  }
}

EXTRACTED IDENTIFIERS FOR PIPELINE REFERENCE:
============================================
INPUT IDENTIFIERS (Required for this endpoint):
- match_id (from live.py) -> used as 'uuid' parameter

OUTPUT IDENTIFIERS (Available for future reference):
- company_id (dictionary keys) -> bookmaker company identifiers
- Example company IDs: "2", "3", "4", etc.

PIPELINE FLOW:
live.py -> match_id -> odds.py -> company_id odds data

# ✅ ODDS.PY - CONFIRMED PATCH & SCHEMA - DO NOT MODIFY
"""

import asyncio
import aiohttp
import os
import json
from typing import List, Dict, Any

def filter_early_odds(odds_data: Dict[str, Any]) -> Dict[str, Any]:
    """Filter odds to keep only early match data (empty string to 10th minute)"""
    if not odds_data or 'results' not in odds_data:
        return odds_data
    
    filtered_results = {}
    
    for company_id, company_data in odds_data['results'].items():
        filtered_company = {}
        
        for market_type, odds_array in company_data.items():
            if isinstance(odds_array, list):
                # Filter odds: keep only entries where minute is "" or <= "10"
                filtered_odds = []
                for odds_entry in odds_array:
                    if isinstance(odds_entry, list) and len(odds_entry) > 1:
                        minute_str = str(odds_entry[1])  # Position [1] is match minute
                        # Keep if empty string or numeric value <= 10
                        if minute_str == "" or (minute_str.isdigit() and int(minute_str) <= 10):
                            filtered_odds.append(odds_entry)
                
                if filtered_odds:  # Only include if we have early odds
                    filtered_company[market_type] = filtered_odds
        
        if filtered_company:  # Only include companies with early odds
            filtered_results[company_id] = filtered_company
    
    return {
        'code': odds_data.get('code', 0),
        'results': filtered_results
    }

async def fetch_match_odds(match_id: str) -> Dict[str, Any]:
    """Fetch odds history for a specific match ID"""
    
    user = os.getenv('THESPORTS_USER')
    secret = os.getenv('THESPORTS_SECRET')
    
    url = "https://api.thesports.com/v1/football/odds/history"
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
                    
                    # Filter odds to keep only early match data (0-10 minutes)
                    filtered_data = filter_early_odds(data)
                    return filtered_data.get('results', {})
                else:
                    error_msg = f"HTTP Error {response.status} for match {match_id}"
                    print(error_msg)
                    return {}
        except Exception as e:
            error_msg = f"Request failed for match {match_id}: {e}"
            print(error_msg)
            return {}

async def process_match_odds():
    """Load match IDs and fetch odds for each"""
    
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
    
    print(f"Fetching odds for {len(match_ids)} matches...")
    
    # Create semaphore to limit concurrent requests  
    semaphore = asyncio.Semaphore(30)
    
    async def fetch_with_semaphore(match_id):
        async with semaphore:
            return match_id, await fetch_match_odds(match_id)
    
    # Fetch all match odds concurrently
    tasks = [fetch_with_semaphore(match_id) for match_id in match_ids]
    odds_results = await asyncio.gather(*tasks)
    
    # Process results into match_id -> odds mapping
    match_odds = {}
    valid_count = 0
    
    for match_id, odds_data in odds_results:
        if odds_data:
            match_odds[match_id] = odds_data
            valid_count += 1
            
            # Log summary of odds data structure
            asia_count = len(odds_data.get('asia', {}))
            eu_count = len(odds_data.get('eu', {}))
            bs_count = len(odds_data.get('bs', {}))
            cr_count = len(odds_data.get('cr', {}))
            
            print(f"Match {match_id}: asia={asia_count}, eu={eu_count}, bs={bs_count}, cr={cr_count}")
    
    print(f"Processed odds for {valid_count}/{len(match_ids)} matches")
    
    # Save odds data to temp file
    with open('/tmp/match_odds.json', 'w') as f:
        json.dump(match_odds, f)
    
    # Save to persistent log file with NY timestamp footer
    from datetime import datetime
    import pytz
    
    ny_tz = pytz.timezone('US/Eastern')
    ny_time = datetime.now(ny_tz)
    timestamp_footer = f"--- Last Updated: {ny_time.strftime('%m/%d/%Y %I:%M %p')} EST ---"
    
    # Create log entry for persistent storage
    log_entry = {
        "timestamp": ny_time.isoformat(),
        "endpoint": "odds",
        "status": "success",
        "matches_processed": valid_count,
        "total_matches": len(match_ids),
        "data": match_odds,
        "ny_timestamp": timestamp_footer
    }
    
    # Ensure logs directory exists
    os.makedirs('/workspaces/TMUX_FINAL_SPORTS/logs/odds', exist_ok=True)
    
    # Save to persistent log file
    with open('/workspaces/TMUX_FINAL_SPORTS/logs/odds/odds.json', 'w') as f:
        json.dump(log_entry, f, indent=2)

async def main():
    """Main entry point"""
    print("Starting odds fetch...")
    await process_match_odds()
    print("Odds fetch completed")

if __name__ == "__main__":
    asyncio.run(main())

