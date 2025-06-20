#!/usr/bin/env python3

# ========================================
# IDENTIFIER REFERENCE - COMPETITIONS.PY
# ========================================
# INPUT IDs: competition_id (from details.py) -> used as 'uuid' parameter
# OUTPUT IDs: category_id, country_id, cur_season_id, cur_stage_id, team_ids -> future reference
# PIPELINE: details.py -> competition_id -> competitions.py -> category_id, season_id, team_ids data
# ========================================

"""
Fetches competition information from /competition/additional/list
Processes league names, logos, current season data

JSON Schema Reference - /competition/additional/list (VALIDATED & CONFIRMED):
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
      "id": "string",             // Competition id
      "category_id": "string",    // Category id
      "country_id": "string",     // Country id
      "name": "string",           // Competition name
      "short_name": "string",     // Competition abbreviation
      "logo": "string",           // Competition logo URL
      "type": "integer",          // Competition type: 0=unknown, 1=league, 2=cup, 3=friendly
      "cur_season_id": "string",  // Current season id
      "cur_stage_id": "string",   // Current stage id
      "cur_round": "integer",     // Current round
      "round_count": "integer",   // Total rounds
      "title_holder": [           // Defending champion array[2]
        "string",                 // [0] Team id
        "integer"                 // [1] Championships count
      ],
      "most_titles": [            // Most winning team array[2]
        [                         // [0] Array of team ids
          "string"                // Team id
        ],
        "integer"                 // [1] Championships count
      ],
      "newcomers": [              // Promoted/relegated teams array[2]
        [                         // [0] Promoted teams array
          "string"                // Team id (from lower division)
        ],
        [                         // [1] Relegated teams array  
          "string"                // Team id (to lower division)
        ]
      ],
      "divisions": [              // Competition level array[2]
        [                         // [0] Higher level competition ids array
          "string"                // Competition id
        ],
        [                         // [1] Lower level competition ids array
          "string"                // Competition id
        ]
      ],
      "host": {                   // Host information
        "country": "string",      // Country name
        "city": "string"          // City (may not exist)
      },
      "primary_color": "string",  // Main color (hex code)
      "secondary_color": "string", // Secondary color (hex code)
      "updated_at": "integer"     // Update time (timestamp)
    }
  ]
}

EXAMPLE RESPONSE (CONFIRMED - 2024-06-18):
{
  "code": 0,
  "query": {"total": 1, "type": "uuid", "uuid": "v2y8m4zhydql074"},
  "results": [{
    "id": "v2y8m4zhydql074",
    "category_id": "0gx7lm7ph0m2wdk",
    "country_id": "l965mkyh42r1ge4",
    "name": "Uruguay Primera Division",
    "short_name": "URU Primera Division",
    "logo": "https://img.thesports.com/football/competition/57bb4f7957510c2da5fd076e75618f5f.png",
    "type": 1,
    "cur_season_id": "gy0or5jhv9pqwzv",
    "cur_stage_id": "y0or5jhwwwxqwzv",
    "cur_round": 5,
    "round_count": 7,
    "title_holder": ["k82rekhv9xprepz", 49],
    "most_titles": [["l7oqdehnnoyr510"], 49],
    "newcomers": [["dn1m1ghno2vmoep", "kdj2ryoh678q1zp", "8y39mp1hlxkmojx"], []],
    "divisions": [[], ["vl7oqdeh4ydr510"]],
    "host": {"country": "Uruguay"},
    "primary_color": "#0f4798",
    "secondary_color": "#c39d00",
    "updated_at": 1750201344
  }]
}

EXTRACTED IDENTIFIERS FOR PIPELINE REFERENCE:
============================================
INPUT IDENTIFIERS (Required for this endpoint):
- competition_id (from details.py) -> used as 'uuid' parameter

OUTPUT IDENTIFIERS (Available for future reference):
- category_id -> future category information lookups
- country_id -> cross-reference with countries.py
- cur_season_id -> future season information lookups
- cur_stage_id -> future stage information lookups
- title_holder[0] -> defending champion team_id
- most_titles[0][0] -> most successful team_id
- newcomers arrays -> promoted/relegated team_ids
- divisions arrays -> related competition_ids

EXAMPLE ID EXTRACTION FROM CONFIRMED RESPONSE:
- category_id: "0gx7lm7ph0m2wdk"
- country_id: "l965mkyh42r1ge4"
- cur_season_id: "gy0or5jhv9pqwzv"
- cur_stage_id: "y0or5jhwwwxqwzv"
- title_holder team: "k82rekhv9xprepz" (49 titles)
- most_titles team: "l7oqdehnnoyr510" (49 titles)
- promoted teams: ["dn1m1ghno2vmoep", "kdj2ryoh678q1zp", "8y39mp1hlxkmojx"]
- lower division: "vl7oqdeh4ydr510"

PIPELINE FLOW:
details.py -> competition_id -> competitions.py -> category_id, season_id, team_ids data

# ✅ COMPETITIONS.PY - CONFIRMED PATCH & SCHEMA - DO NOT MODIFY
"""

import asyncio
import aiohttp
import os
import json
import shutil
from datetime import datetime, timedelta
from typing import List, Dict, Any
# Removed logging_utils dependency - keeping only print statements for logging

async def fetch_competition_info(competition_id: str) -> Dict[str, Any]:
    """Fetch competition information for a specific competition ID"""
    
    user = os.getenv('THESPORTS_USER')
    secret = os.getenv('THESPORTS_SECRET')
    
    url = "https://api.thesports.com/v1/football/competition/additional/list"
    params = {
        'user': user,
        'secret': secret,
        'uuid': competition_id
    }
    
    request_data = {
        "url": url,
        "method": "GET",
        "params": {"user": "***", "secret": "***", "uuid": competition_id}
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if 'err' in data:
                        error_msg = f"API Error for competition {competition_id}: {data['err']}"
                        print(error_msg)
                        return {}
                    
                    results = data.get('results', [])
                    if results:
                        return results[0]  # First element as per spec
                    else:
                        error_msg = f"No results for competition {competition_id}"
                        print(error_msg)
                    
                return {}
        except Exception as e:
            error_msg = f"Request failed for competition {competition_id}: {e}"
            print(error_msg)
            return {}

def load_competition_cache() -> Dict[str, Any]:
    """Load existing competition cache or return empty cache structure"""
    cache_file = '/workspaces/TMUX_FINAL_SPORTS/cache/competitions/competitions_cache.json'
    
    try:
        with open(cache_file, 'r') as f:
            cache = json.load(f)
            return cache
    except FileNotFoundError:
        return {
            "cache_metadata": {
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "cache_version": "1.0",
                "total_competitions": 0,
                "cache_duration_hours": 24
            },
            "competitions": {}
        }

def save_competition_cache(cache: Dict[str, Any]):
    """Save competition cache with archive backup"""
    cache_file = '/workspaces/TMUX_FINAL_SPORTS/cache/competitions/competitions_cache.json'
    archive_dir = '/workspaces/TMUX_FINAL_SPORTS/cache/competitions/archive'
    
    # Ensure directories exist
    os.makedirs(os.path.dirname(cache_file), exist_ok=True)
    os.makedirs(archive_dir, exist_ok=True)
    
    # Archive existing cache if it exists
    if os.path.exists(cache_file):
        today = datetime.now().strftime('%Y%m%d')
        archive_file = f"{archive_dir}/competitions_cache_{today}.json"
        if not os.path.exists(archive_file):  # Only archive once per day
            shutil.copy2(cache_file, archive_file)
            print(f"Archived previous competitions cache to {archive_file}")
    
    # Update metadata
    cache["cache_metadata"]["last_updated"] = datetime.now().isoformat()
    cache["cache_metadata"]["total_competitions"] = len(cache["competitions"])
    
    # Save cache
    with open(cache_file, 'w') as f:
        json.dump(cache, f, indent=2)

def is_cache_fresh(cache: Dict[str, Any], cache_duration_hours: int = 24) -> bool:
    """Check if cache is still fresh based on age"""
    try:
        last_updated = datetime.fromisoformat(cache["cache_metadata"]["last_updated"])
        cache_age = datetime.now() - last_updated
        return cache_age < timedelta(hours=cache_duration_hours)
    except (KeyError, ValueError):
        return False

def get_stale_competition_ids(competition_ids: List[str], cache: Dict[str, Any]) -> List[str]:
    """Get list of competition IDs that need fresh API calls"""
    cache_competitions = cache.get("competitions", {})
    stale_ids = []
    
    for competition_id in competition_ids:
        if competition_id not in cache_competitions:
            stale_ids.append(competition_id)  # Missing from cache
            continue
            
        # Check if individual competition data is stale (compare API updated_at)
        cached_competition = cache_competitions[competition_id]
        if "data" not in cached_competition:
            stale_ids.append(competition_id)
            continue
            
        # For competitions, we trust 24-hour cache unless explicitly stale
        comp_cache_time = datetime.fromisoformat(cached_competition.get("fetched_at", "1900-01-01T00:00:00"))
        if datetime.now() - comp_cache_time > timedelta(hours=24):
            stale_ids.append(competition_id)
    
    return stale_ids

async def process_competition_data():
    """Load competition IDs and fetch information with smart caching"""
    
    try:
        with open('/tmp/competition_ids.json', 'r') as f:
            competition_ids = json.load(f)
    except FileNotFoundError:
        print("No competition IDs file found")
        return
    
    if not competition_ids:
        print("No competition IDs to process")
        return
    
    print(f"Processing competition info for {len(competition_ids)} competitions...")
    
    # Load existing cache
    cache = load_competition_cache()
    cache_is_fresh = is_cache_fresh(cache)
    
    # Determine which competitions need fresh API calls
    if cache_is_fresh:
        stale_competition_ids = get_stale_competition_ids(competition_ids, cache)
        print(f"Cache is fresh. Only fetching {len(stale_competition_ids)} stale/missing competitions.")
    else:
        stale_competition_ids = competition_ids
        print(f"Cache is stale. Fetching all {len(stale_competition_ids)} competitions.")
    
    # Fetch only stale competitions from API
    fresh_competition_data = {}
    if stale_competition_ids:
        print(f"Making API calls for {len(stale_competition_ids)} competitions...")
        
        # Create semaphore to limit concurrent requests (reduced for cache updates)
        semaphore = asyncio.Semaphore(15)
        
        async def fetch_with_semaphore(competition_id):
            async with semaphore:
                return competition_id, await fetch_competition_info(competition_id)
        
        # Fetch stale competition data concurrently
        tasks = [fetch_with_semaphore(comp_id) for comp_id in stale_competition_ids]
        competition_results = await asyncio.gather(*tasks)
        
        # Process fresh API results
        for competition_id, comp_info in competition_results:
            if comp_info:
                fresh_competition_data[competition_id] = {
                    "data": comp_info,
                    "fetched_at": datetime.now().isoformat(),
                    "api_updated_at": comp_info.get("updated_at")
                }
    
    # Merge cached and fresh data
    final_competition_data = {}
    cache_hits = 0
    api_calls = 0
    
    for competition_id in competition_ids:
        if competition_id in fresh_competition_data:
            # Use fresh API data
            final_competition_data[competition_id] = fresh_competition_data[competition_id]["data"]
            cache["competitions"][competition_id] = fresh_competition_data[competition_id]  # Update cache
            api_calls += 1
            
            # Log fresh data
            comp_info = fresh_competition_data[competition_id]["data"]
            comp_name = comp_info.get('name', 'Unknown')
            short_name = comp_info.get('short_name', 'N/A')
            cur_season = comp_info.get('cur_season_id', 'N/A')
            print(f"Competition {competition_id}: {comp_name} ({short_name}) - Season: {cur_season} [FRESH]")
            
        elif competition_id in cache.get("competitions", {}):
            # Use cached data
            cached_competition = cache["competitions"][competition_id]
            if "data" in cached_competition:
                final_competition_data[competition_id] = cached_competition["data"]
                cache_hits += 1
                
                # Log cached data
                comp_info = cached_competition["data"]
                comp_name = comp_info.get('name', 'Unknown')
                print(f"Competition {competition_id}: {comp_name} [CACHED]")
    
    print(f"Competition data processing complete:")
    print(f"  - Cache hits: {cache_hits}")
    print(f"  - API calls: {api_calls}")
    print(f"  - Total competitions: {len(final_competition_data)}")
    
    # Save updated cache
    if fresh_competition_data:  # Only save if we have new data
        save_competition_cache(cache)
    
    # Save competition data for backward compatibility
    with open('/tmp/competition_data.json', 'w') as f:
        json.dump(final_competition_data, f)

async def main():
    """Main entry point"""
    print("Starting competition data fetch...")
    await process_competition_data()
    print("Competition fetch completed")

if __name__ == "__main__":
    asyncio.run(main())

# NY Eastern Time Footer
from datetime import datetime
import pytz
ny_tz = pytz.timezone('US/Eastern')
ny_time = datetime.now(ny_tz)
print(f"\n--- Generated: {ny_time.strftime('%m/%d/%Y %I:%M %p')} EST ---")