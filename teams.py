#!/usr/bin/env python3

# ========================================
# IDENTIFIER REFERENCE - TEAMS.PY
# ========================================
# INPUT IDs: home_team_id, away_team_id (from details.py) -> used as 'uuid' parameter
# OUTPUT IDs: coach_id, venue_id, country_id, competition_id -> future reference
# PIPELINE: details.py -> team_ids -> teams.py -> coach_id, venue_id, country_id data
# ========================================

"""
Fetches team information from /team/additional/list
Processes team names, logos, coach, market value data

JSON Schema Reference - /team/additional/list (VALIDATED & CONFIRMED):
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
      "id": "string",             // Team id
      "competition_id": "string", // Competition id (league team belongs to, not cup related)
      "country_id": "string",     // Country id
      "name": "string",           // Team name
      "short_name": "string",     // Team abbreviation
      "logo": "string",           // Team logo URL
      "national": "integer",      // Is national team: 1=Yes, 0=No
      "country_logo": "string",   // National team logo (exists for national teams)
      "foundation_time": "integer", // Established timestamp
      "website": "string",        // Team official website
      "coach_id": "string",       // Coach id
      "venue_id": "string",       // Venue id
      "market_value": "integer",  // Market value
      "market_value_currency": "string", // Market value currency symbol
      "total_players": "integer", // Total players (-1 means no data)
      "foreign_players": "integer", // Non-local players (-1 means no data)
      "national_players": "integer", // National team players (-1 means no data)
      "uid": "string",            // Team id after duplicate merge (optional)
      "virtual": "integer",       // Is placeholder team: 1=Yes, 0=No
      "gender": "integer",        // Gender: 1=Male, 2=Female
      "updated_at": "integer"     // Update time (timestamp)
    }
  ]
}

EXAMPLE RESPONSE (CONFIRMED - 2024-06-18):
{
  "code": 0,
  "query": {"total": 1, "type": "uuid", "uuid": "y0or5jh4njpqwzv"},
  "results": [{
    "id": "y0or5jh4njpqwzv",
    "competition_id": "v2y8m4zhydql074",
    "country_id": "l965mkyh42r1ge4",
    "name": "Montevideo City Torque",
    "short_name": "Torque",
    "logo": "https://img.thesports.com/football/team/bb5004650a388d73f47cc3ca08623cc8.png",
    "national": 0,
    "coach_id": "9k82rekhkndrepz",
    "venue_id": "gpxwrxlh0zjryk0",
    "market_value": 7400000,
    "market_value_currency": "€",
    "total_players": 22,
    "foreign_players": 8,
    "national_players": 2,
    "virtual": 0,
    "gender": 1,
    "updated_at": 1749614205
  }]
}

EXTRACTED IDENTIFIERS FOR PIPELINE REFERENCE:
============================================
INPUT IDENTIFIERS (Required for this endpoint):
- home_team_id, away_team_id (from details.py) -> used as 'uuid' parameter

OUTPUT IDENTIFIERS (Available for future reference):
- coach_id -> future coach information lookups
- venue_id -> future venue information lookups  
- country_id -> cross-reference with countries.py
- competition_id -> cross-reference with competitions.py

EXAMPLE ID EXTRACTION FROM CONFIRMED RESPONSE:
- coach_id: "9k82rekhkndrepz"
- venue_id: "gpxwrxlh0zjryk0"
- country_id: "l965mkyh42r1ge4"
- competition_id: "v2y8m4zhydql074"

PIPELINE FLOW:
details.py -> home_team_id, away_team_id -> teams.py -> coach_id, venue_id, country_id data

# ✅ TEAMS.PY - CONFIRMED PATCH & SCHEMA - DO NOT MODIFY
"""

import asyncio
import aiohttp
import os
import json
import shutil
from datetime import datetime, timedelta
from typing import List, Dict, Any
# Removed logging_utils dependency - keeping only print statements for logging

async def fetch_team_info(team_id: str) -> Dict[str, Any]:
    """Fetch team information for a specific team ID"""
    
    user = os.getenv('THESPORTS_USER')
    secret = os.getenv('THESPORTS_SECRET')
    
    url = "https://api.thesports.com/v1/football/team/additional/list"
    params = {
        'user': user,
        'secret': secret,
        'uuid': team_id
    }
    
    request_data = {
        "url": url,
        "method": "GET",
        "params": {"user": "***", "secret": "***", "uuid": team_id}
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if 'err' in data:
                        error_msg = f"API Error for team {team_id}: {data['err']}"
                        print(error_msg)
                        return {}
                    
                    results = data.get('results', [])
                    if results:
                        return results[0]  # First element as per spec
                    else:
                        error_msg = f"No results for team {team_id}"
                        print(error_msg)
                
                return {}
        except Exception as e:
            error_msg = f"Request failed for team {team_id}: {e}"
            print(error_msg)
            return {}

def load_team_cache() -> Dict[str, Any]:
    """Load existing team cache or return empty cache structure"""
    cache_file = '/workspaces/TMUX_FINAL_SPORTS/cache/teams/teams_cache.json'
    
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
                "total_teams": 0,
                "cache_duration_hours": 24
            },
            "teams": {}
        }

def save_team_cache(cache: Dict[str, Any]):
    """Save team cache with archive backup"""
    cache_file = '/workspaces/TMUX_FINAL_SPORTS/cache/teams/teams_cache.json'
    archive_dir = '/workspaces/TMUX_FINAL_SPORTS/cache/teams/archive'
    
    # Ensure directories exist
    os.makedirs(os.path.dirname(cache_file), exist_ok=True)
    os.makedirs(archive_dir, exist_ok=True)
    
    # Archive existing cache if it exists
    if os.path.exists(cache_file):
        today = datetime.now().strftime('%Y%m%d')
        archive_file = f"{archive_dir}/teams_cache_{today}.json"
        if not os.path.exists(archive_file):  # Only archive once per day
            shutil.copy2(cache_file, archive_file)
            print(f"Archived previous teams cache to {archive_file}")
    
    # Update metadata
    cache["cache_metadata"]["last_updated"] = datetime.now().isoformat()
    cache["cache_metadata"]["total_teams"] = len(cache["teams"])
    
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

def get_stale_team_ids(team_ids: List[str], cache: Dict[str, Any]) -> List[str]:
    """Get list of team IDs that need fresh API calls"""
    cache_teams = cache.get("teams", {})
    stale_ids = []
    
    for team_id in team_ids:
        if team_id not in cache_teams:
            stale_ids.append(team_id)  # Missing from cache
            continue
            
        # Check if individual team data is stale (compare API updated_at)
        cached_team = cache_teams[team_id]
        if "data" not in cached_team:
            stale_ids.append(team_id)
            continue
            
        # For teams, we trust 24-hour cache unless explicitly stale
        team_cache_time = datetime.fromisoformat(cached_team.get("fetched_at", "1900-01-01T00:00:00"))
        if datetime.now() - team_cache_time > timedelta(hours=24):
            stale_ids.append(team_id)
    
    return stale_ids

async def process_team_data():
    """Load team IDs and fetch information with smart caching"""
    
    try:
        with open('/tmp/team_ids.json', 'r') as f:
            team_ids = json.load(f)
    except FileNotFoundError:
        print("No team IDs file found")
        return
    
    if not team_ids:
        print("No team IDs to process")
        return
    
    print(f"Processing team info for {len(team_ids)} teams...")
    
    # Load existing cache
    cache = load_team_cache()
    cache_is_fresh = is_cache_fresh(cache)
    
    # Determine which teams need fresh API calls
    if cache_is_fresh:
        stale_team_ids = get_stale_team_ids(team_ids, cache)
        print(f"Cache is fresh. Only fetching {len(stale_team_ids)} stale/missing teams.")
    else:
        stale_team_ids = team_ids
        print(f"Cache is stale. Fetching all {len(stale_team_ids)} teams.")
    
    # Fetch only stale teams from API
    fresh_team_data = {}
    if stale_team_ids:
        print(f"Making API calls for {len(stale_team_ids)} teams...")
        
        # Create semaphore to limit concurrent requests (reduced for cache updates)
        semaphore = asyncio.Semaphore(15)
        
        async def fetch_with_semaphore(team_id):
            async with semaphore:
                return team_id, await fetch_team_info(team_id)
        
        # Fetch stale team data concurrently
        tasks = [fetch_with_semaphore(team_id) for team_id in stale_team_ids]
        team_results = await asyncio.gather(*tasks)
        
        # Process fresh API results
        for team_id, team_info in team_results:
            if team_info:
                fresh_team_data[team_id] = {
                    "data": team_info,
                    "fetched_at": datetime.now().isoformat(),
                    "api_updated_at": team_info.get("updated_at")
                }
    
    # Merge cached and fresh data
    final_team_data = {}
    cache_hits = 0
    api_calls = 0
    
    for team_id in team_ids:
        if team_id in fresh_team_data:
            # Use fresh API data
            final_team_data[team_id] = fresh_team_data[team_id]["data"]
            cache["teams"][team_id] = fresh_team_data[team_id]  # Update cache
            api_calls += 1
            
            # Log fresh data
            team_info = fresh_team_data[team_id]["data"]
            team_name = team_info.get('name', 'Unknown')
            short_name = team_info.get('short_name', 'N/A')
            market_value = team_info.get('market_value', 'N/A')
            print(f"Team {team_id}: {team_name} ({short_name}) - Value: {market_value} [FRESH]")
            
        elif team_id in cache.get("teams", {}):
            # Use cached data
            cached_team = cache["teams"][team_id]
            if "data" in cached_team:
                final_team_data[team_id] = cached_team["data"]
                cache_hits += 1
                
                # Log cached data
                team_info = cached_team["data"]
                team_name = team_info.get('name', 'Unknown')
                print(f"Team {team_id}: {team_name} [CACHED]")
    
    print(f"Team data processing complete:")
    print(f"  - Cache hits: {cache_hits}")
    print(f"  - API calls: {api_calls}")
    print(f"  - Total teams: {len(final_team_data)}")
    
    # Save updated cache
    if fresh_team_data:  # Only save if we have new data
        save_team_cache(cache)
    
    # Save team data for backward compatibility
    with open('/tmp/team_data.json', 'w') as f:
        json.dump(final_team_data, f)

async def main():
    """Main entry point"""
    print("Starting team data fetch...")
    await process_team_data()
    print("Team fetch completed")

if __name__ == "__main__":
    asyncio.run(main())

# NY Eastern Time Footer
from datetime import datetime
import pytz
ny_tz = pytz.timezone('US/Eastern')
ny_time = datetime.now(ny_tz)
print(f"\n--- Generated: {ny_time.strftime('%m/%d/%Y %I:%M %p')} EST ---")