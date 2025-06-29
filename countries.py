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
# IDENTIFIER REFERENCE - COUNTRIES.PY
# ========================================
# INPUT IDs: None (global endpoint, no parameters required)
# OUTPUT IDs: country_id, category_id -> cross-reference lookup table
# PIPELINE: Independent global endpoint -> country_id lookup for teams.py, competitions.py
# ========================================

"""
Fetches country information from /country/list
Global lookup table for country_id -> name/flag mapping

JSON Schema Reference - /country/list (VALIDATED & CONFIRMED):
{
  "code": "integer",
  "results": [
    {
      "id": "string",             // Country id (unique identifier)
      "category_id": "string",    // Category id (regional grouping)
      "name": "string",           // Country name
      "logo": "string",           // Country logo/flag URL
      "updated_at": "integer"     // Update time (timestamp)
    }
  ]
}

EXAMPLE RESPONSE (CONFIRMED - 2024-06-18):
{
  "code": 0,
  "results": [
    {
      "id": "kp3glrw7hwqdyjv",
      "category_id": "49vjxm8ghgr6odg",
      "name": "England",
      "logo": "https://img.thesports.com/football/country/916957927a5ee63e040631bd442ada34.png",
      "updated_at": 1620815091
    },
    {
      "id": "49vjxm8ghgr6odg",
      "category_id": "49vjxm8ghgr6odg",
      "name": "Italy",
      "logo": "https://img.thesports.com/football/country/58f599d7d16dda6c6f89841d3c16e16f.png",
      "updated_at": 1620815092
    },
    {
      "id": "0gx7lm7ph0m2wdk",
      "category_id": "49vjxm8ghgr6odg",
      "name": "Spain",
      "logo": "https://img.thesports.com/football/country/ad7318c3ee868ab198d5a21fb370393e.png",
      "updated_at": 1620815093
    }
  ]
}

EXTRACTED IDENTIFIERS FOR PIPELINE REFERENCE:
============================================
INPUT IDENTIFIERS (Required for this endpoint):
- None (global endpoint requiring no input IDs)

OUTPUT IDENTIFIERS (Available for cross-reference):
- country_id -> primary key for country lookup
- category_id -> regional/continental grouping identifier

EXAMPLE ID EXTRACTION FROM CONFIRMED RESPONSE:
- England: country_id="kp3glrw7hwqdyjv", category_id="49vjxm8ghgr6odg"
- Italy: country_id="49vjxm8ghgr6odg", category_id="49vjxm8ghgr6odg"
- Spain: country_id="0gx7lm7ph0m2wdk", category_id="49vjxm8ghgr6odg"
- Total countries: 212 available for lookup

CROSS-REFERENCE USAGE:
- teams.py -> country_id lookup -> country name/flag
- competitions.py -> country_id lookup -> host country info
- Global lookup table for country_id resolution across all endpoints

PIPELINE FLOW:
Independent global endpoint -> country_id:name mapping for teams.py, competitions.py

# ✅ COUNTRIES.PY - CONFIRMED PATCH & SCHEMA - DO NOT MODIFY
"""

import asyncio
import aiohttp
import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any
# Removed logging_utils dependency - keeping only print statements for logging

async def fetch_countries() -> List[Dict[str, Any]]:
    """Fetch complete country list - no ID required"""
    
    user = os.getenv('THESPORTS_USER')
    secret = os.getenv('THESPORTS_SECRET')
    
    if not user or not secret:
        error_msg = "THESPORTS_USER and THESPORTS_SECRET environment variables required"
        print(f"ERROR: {error_msg}")
        return []
    
    url = "https://api.thesports.com/v1/football/country/list"
    params = {
        'user': user,
        'secret': secret
    }
    
    request_data = {
        "url": url,
        "method": "GET",
        "params": {"user": "***", "secret": "***"}
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if 'err' in data:
                        error_msg = f"API Error: {data['err']}"
                        print(error_msg)
                        return []
                    
                    countries = data.get('results', [])
                    print(f"Fetched {len(countries)} countries")
                    
                    return countries
                else:
                    error_msg = f"HTTP Error: {response.status}"
                    print(error_msg)
                    return []
                    
        except Exception as e:
            error_msg = f"Request failed: {e}"
            print(error_msg)
            return []

def load_country_cache() -> Dict[str, Any]:
    """Load existing country cache or return empty cache structure"""
    cache_file = '/workspaces/TMUX_FINAL_SPORTS/cache/countries/countries_cache.json'
    
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
                "total_countries": 0,
                "cache_duration_hours": 24
            },
            "countries": {}
        }

def save_country_cache(cache: Dict[str, Any]):
    """Save country cache"""
    cache_file = '/workspaces/TMUX_FINAL_SPORTS/cache/countries/countries_cache.json'
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(cache_file), exist_ok=True)
    
    # Update metadata
    cache["cache_metadata"]["last_updated"] = datetime.now().isoformat()
    cache["cache_metadata"]["total_countries"] = len(cache["countries"])
    
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

async def process_countries():
    """Fetch and process country data with smart caching"""
    
    print("Processing global country list...")
    
    # Load existing cache
    cache = load_country_cache()
    cache_is_fresh = is_cache_fresh(cache)
    
    # Check if we need to fetch fresh data
    if cache_is_fresh and cache.get("countries"):
        print(f"Cache is fresh. Using cached data for {len(cache['countries'])} countries.")
        country_data = cache["countries"]
        api_calls = 0
        cache_hits = len(country_data)
        
        # Log cached countries
        for country_id, country in country_data.items():
            name = country.get('name', 'Unknown')
            print(f"Country {country_id}: {name} [CACHED]")
    else:
        print("Cache is stale or empty. Fetching fresh country data...")
        
        countries = await fetch_countries()
        
        if not countries:
            print("No country data retrieved")
            return
        
        # Process into country_id -> country_data mapping
        country_data = {}
        
        for country in countries:
            country_id = country.get('id')
            if country_id:
                country_data[str(country_id)] = country
                
                # Log fresh country info
                name = country.get('name', 'Unknown')
                logo = country.get('logo', 'N/A')
                
                print(f"Country {country_id}: {name} - Logo: {logo} [FRESH]")
        
        # Update cache with fresh data
        cache["countries"] = country_data
        save_country_cache(cache)
        
        api_calls = 1
        cache_hits = 0
    
    print(f"Country data processing complete:")
    print(f"  - Cache hits: {cache_hits}")
    print(f"  - API calls: {api_calls}")
    print(f"  - Total countries: {len(country_data)}")
    
    # Save country data for backward compatibility
    with open('/tmp/country_data.json', 'w') as f:
        json.dump(country_data, f)
    
    print("All data fetching completed - pipeline finished!")

async def main():
    """Main entry point"""
    print("Starting country data fetch...")
    await process_countries()
    print("Country fetch completed")

if __name__ == "__main__":
    asyncio.run(main())

# NY Eastern Time Footer
from datetime import datetime
import pytz
ny_tz = pytz.timezone('US/Eastern')
ny_time = datetime.now(ny_tz)
print(f"\n--- Generated: {ny_time.strftime('%m/%d/%Y %I:%M %p')} EST ---")