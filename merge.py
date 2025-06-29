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
# PIPELINE CALLING STANDARD - MERGE.PY
# ========================================
# POSITION: teams.py/competitions.py/countries.py → merge.py → pretty_print.py
# CALLS NEXT: trigger_next_stage() → subprocess.run(['python3', 'pretty_print.py'], check=True)
# PATTERN: Standard pipeline pattern with try/except CalledProcessError handling
# ========================================

"""
merge.py - Comprehensive Match Data Merger
Merges all endpoint data (live, details, odds, teams, competitions, countries) 
into complete match summaries with resolved names and enriched metadata.
"""

import json
import os
import sys
import subprocess
import time
from datetime import datetime
import pytz
from typing import Dict, List, Any, Optional

def load_json_file(file_path: str) -> Optional[Dict[str, Any]]:
    """Load JSON file with error handling"""
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            print(f"File not found: {file_path}")
            return None
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return None

def load_cache_data(cache_type: str) -> Dict[str, Any]:
    """Load cache data (teams, competitions, countries) with fallback"""
    cache_file = f'/workspaces/TMUX_FINAL_SPORTS/cache/{cache_type}/{cache_type}_cache.json'
    cache_data = load_json_file(cache_file)
    
    if cache_data and cache_type in cache_data:
        return cache_data[cache_type]
    else:
        print(f"No {cache_type} cache data found, using empty cache")
        return {}

def resolve_team_name(team_id: str, teams_cache: Dict[str, Any]) -> Dict[str, str]:
    """Resolve team ID to team information"""
    if team_id in teams_cache and 'data' in teams_cache[team_id]:
        team_data = teams_cache[team_id]['data']
        return {
            'id': team_id,
            'name': team_data.get('name', f'Team_{team_id}'),
            'short_name': team_data.get('short_name', team_data.get('name', f'Team_{team_id}')),
            'logo': team_data.get('logo', ''),
            'country_id': team_data.get('country_id', '')
        }
    else:
        return {
            'id': team_id,
            'name': f'Team_{team_id}',
            'short_name': f'Team_{team_id}',
            'logo': '',
            'country_id': ''
        }

def resolve_competition_name(comp_id: str, competitions_cache: Dict[str, Any]) -> Dict[str, str]:
    """Resolve competition ID to competition information"""
    if comp_id in competitions_cache and 'data' in competitions_cache[comp_id]:
        comp_data = competitions_cache[comp_id]['data']
        return {
            'id': comp_id,
            'name': comp_data.get('name', f'Competition_{comp_id}'),
            'short_name': comp_data.get('short_name', comp_data.get('name', f'Competition_{comp_id}')),
            'logo': comp_data.get('logo', ''),
            'country_id': comp_data.get('country_id', '')
        }
    else:
        return {
            'id': comp_id,
            'name': f'Competition_{comp_id}',
            'short_name': f'Competition_{comp_id}',
            'logo': '',
            'country_id': ''
        }

def resolve_country_name(country_id: str, countries_cache: Dict[str, Any]) -> Dict[str, str]:
    """Resolve country ID to country information"""
    if country_id and country_id in countries_cache:
        country_data = countries_cache[country_id]
        return {
            'id': country_id,
            'name': country_data.get('name', f'Country_{country_id}'),
            'logo': country_data.get('logo', '')
        }
    else:
        return {
            'id': country_id or '',
            'name': f'Country_{country_id}' if country_id else '',
            'logo': ''
        }

def get_status_text(status_id: int) -> str:
    """Convert status ID to human-readable text"""
    status_map = {
        1: 'Not Started',
        2: 'Live',
        3: 'Finished', 
        4: 'Finished',
        8: 'Finished',
        13: 'Postponed',
        15: 'Cancelled'
    }
    return status_map.get(status_id, f'Status_{status_id}')

def get_stat_type_name(stat_type: int) -> str:
    """Convert stat type code to human-readable name"""
    stat_types = {
        2: 'Yellow Cards',
        3: 'Red Cards',
        4: 'Penalties',
        8: 'Offsides',
        21: 'Shots on Target',
        22: 'Total Shots',
        23: 'Total Passes',
        24: 'Accurate Passes',
        25: 'Possession %'
    }
    return stat_types.get(stat_type, f'Stat_Type_{stat_type}')

def get_incident_type_name(incident_type: int) -> str:
    """Convert incident type code to human-readable name"""
    incident_types = {
        1: 'Goal',
        3: 'Card',
        4: 'Red Card',
        8: 'Penalty Goal',
        9: 'Substitution',
        11: 'Half Time',
        12: 'Full Time',
        16: 'Penalty Miss',
        17: 'Own Goal',
        19: 'Added Time',
        28: 'VAR Decision'
    }
    return incident_types.get(incident_type, f'Incident_Type_{incident_type}')

def filter_odds_data(odds_data: Dict[str, Any], match_id: str) -> Dict[str, Any]:
    """Filter odds data to include only pregame through minute 10, no duplicates, prioritize Bet365 (company ID 2)"""
    if not odds_data:
        return {}
    
    # Handle the actual odds.py data structure: {company_id: {market_type: [[odds_arrays]]}}
    if not isinstance(odds_data, dict):
        return {}
    
    all_companies_odds = {}
    
    # Process each company's odds directly from odds.py structure
    for company_id, company_data in odds_data.items():
        if not isinstance(company_data, dict):
            continue
            
        filtered_company = {}
        
        # Process each market type (asia, eu, bs, cr)
        for market_type, odds_arrays in company_data.items():
            if isinstance(odds_arrays, list):
                seen_minutes = set()
                filtered_arrays = []
                
                for odds_array in odds_arrays:
                    if isinstance(odds_array, list) and len(odds_array) >= 2:
                        minute = odds_array[1]  # Match minute is at index 1
                        
                        # Filter: include "" (pregame) through "10"
                        if minute == "" or (isinstance(minute, str) and minute.isdigit() and int(minute) <= 10):
                            # Check for duplicates
                            if minute not in seen_minutes:
                                seen_minutes.add(minute)
                                filtered_arrays.append(odds_array)
                
                if filtered_arrays:
                    filtered_company[market_type] = filtered_arrays
        
        if filtered_company:
            all_companies_odds[company_id] = filtered_company
    
    # Second pass: Select preferred company (Bet365 first, then fallback)
    preferred_companies = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "13", "14", "15", "16", "17", "21", "22"]
    
    for company_id in preferred_companies:
        if company_id in all_companies_odds and all_companies_odds[company_id]:
            # Found data for this company, return only this company's odds
            return {company_id: all_companies_odds[company_id]}
    
    # If no preferred companies found, return empty
    return {}

def merge_match_data(match_id: str, live_data: Dict[str, Any], details_data: Dict[str, Any], 
                    odds_data: Dict[str, Any], teams_cache: Dict[str, Any], competitions_cache: Dict[str, Any], 
                    countries_cache: Dict[str, Any]) -> Dict[str, Any]:
    """Merge all data sources for a single match"""
    
    # Start with basic match info from details
    merged = {
        'match_id': match_id,
        'timestamp': datetime.now().isoformat(),
        'data_sources': {
            'live': live_data is not None,
            'details': details_data is not None,
            'odds': odds_data is not None,
            'teams_cache': len(teams_cache) > 0,
            'competitions_cache': len(competitions_cache) > 0,
            'countries_cache': len(countries_cache) > 0
        }
    }
    
    # Merge details data (match context)
    if details_data:
        merged.update({
            'scheduled_time': details_data.get('match_time'),
            'scheduled_time_readable': datetime.fromtimestamp(details_data.get('match_time', 0)).strftime('%Y-%m-%d %H:%M:%S') if details_data.get('match_time') else 'Unknown',
            'venue_id': details_data.get('venue_id', ''),
            'referee_id': details_data.get('referee_id', ''),
            'neutral_venue': details_data.get('neutral', 0) == 1,
            'season_id': details_data.get('season_id', ''),
            'environment': details_data.get('environment', {}),
            'round_info': details_data.get('round', {}),
            'coverage': details_data.get('coverage', {})
        })
        
        # Resolve team information
        home_team = resolve_team_name(details_data.get('home_team_id', ''), teams_cache)
        away_team = resolve_team_name(details_data.get('away_team_id', ''), teams_cache)
        
        # Resolve competition information
        competition = resolve_competition_name(details_data.get('competition_id', ''), competitions_cache)
        
        # Resolve country information for teams and competition
        home_team_country = resolve_country_name(home_team.get('country_id', ''), countries_cache)
        away_team_country = resolve_country_name(away_team.get('country_id', ''), countries_cache)
        competition_country = resolve_country_name(competition.get('country_id', ''), countries_cache)
        
        merged.update({
            'teams': {
                'home': {**home_team, 'country': home_team_country},
                'away': {**away_team, 'country': away_team_country}
            },
            'competition': {**competition, 'country': competition_country}
        })
    
    # Extract score arrays from details.py data (home_scores and away_scores)
    if details_data:
        home_scores = details_data.get('home_scores', [0,0,0,0,0,0,0])
        away_scores = details_data.get('away_scores', [0,0,0,0,0,0,0])
        
        merged.update({
            'scores': {
                'home': home_scores,
                'away': away_scores
            }
        })
    
    # Extract status_id from details.py data
    if details_data:
        merged.update({
            'details_status_id': details_data.get('status_id')
        })
    
    # Merge live data (current status only, no scores)
    if live_data:
        score_data = live_data.get('score', [])
        if len(score_data) >= 5:
            merged.update({
                'live_status': {
                    'status_id': score_data[1] if len(score_data) > 1 else 0,
                    'status_text': get_status_text(score_data[1]) if len(score_data) > 1 else 'Unknown',
                    'last_update': score_data[4] if len(score_data) > 4 else 0,
                    'last_update_readable': datetime.fromtimestamp(score_data[4]).strftime('%Y-%m-%d %H:%M:%S') if len(score_data) > 4 and score_data[4] else 'Unknown'
                }
            })
        
        # Extract VAR incidents while filtering out other data
        # VAR incidents (type: 28) are preserved for analysis, all other incidents/stats/tlive filtered out
        var_incidents = []
        if 'incidents' in live_data:
            var_incidents = [
                incident for incident in live_data['incidents'] 
                if incident.get('type') == 28  # VAR Decision type
            ]
        
        # Add VAR incidents to merged data if any exist
        if var_incidents:
            merged['var_incidents'] = var_incidents
        
        # Note: stats, non-VAR incidents, and tlive fields are intentionally filtered out
        # These fields contained detailed match statistics, non-VAR incident tracking, and live commentary
        # but have been removed to reduce data size and focus on core match information
        # VAR incidents (type: 28) are preserved for regulatory analysis
    
    # Merge filtered odds data (pregame to minute 10, no duplicates)
    if odds_data:
        filtered_odds = filter_odds_data(odds_data, match_id)
        if filtered_odds:
            merged['odds'] = filtered_odds
    
    return merged

def main_merge():
    """Main merge function"""
    # Record pipeline start time
    pipeline_start_time = time.time()
    
    print("Starting comprehensive match data merge...")
    print("="*50)
    
    # Load all data sources
    print("Loading data sources...")
    
    # Load live data
    live_data = load_json_file('/workspaces/TMUX_FINAL_SPORTS/logs/live/live.json')
    print(f"✓ Live data loaded: {live_data is not None}")
    
    # Load details data  
    details_data = load_json_file('/workspaces/TMUX_FINAL_SPORTS/logs/details/details.json')
    print(f"✓ Details data loaded: {details_data is not None}")
    
    # Load odds data
    odds_data = load_json_file('/workspaces/TMUX_FINAL_SPORTS/logs/odds/odds.json')
    print(f"✓ Odds data loaded: {odds_data is not None}")
    
    # Load cache data
    teams_cache = load_cache_data('teams')
    competitions_cache = load_cache_data('competitions')
    countries_cache = load_cache_data('countries')
    
    print(f"✓ Teams cache: {len(teams_cache)} teams")
    print(f"✓ Competitions cache: {len(competitions_cache)} competitions")
    print(f"✓ Countries cache: {len(countries_cache)} countries")
    
    # Extract match lists
    live_matches = {}
    if live_data and 'fetch_history' in live_data:
        # Use the most recent fetch from the accumulating live.json structure
        latest_fetch = live_data['fetch_history'][-1] if live_data['fetch_history'] else {}
        if 'api_response' in latest_fetch and 'results' in latest_fetch['api_response']:
            for match in latest_fetch['api_response']['results']:
                match_id = match.get('id')
                if match_id:
                    live_matches[match_id] = match
    
    details_matches = {}
    if details_data and 'api_response' in details_data:
        for match in details_data['api_response']:
            match_id = match.get('id')
            if match_id:
                details_matches[match_id] = match
    
    # Process odds data - extract from data key
    odds_by_match = odds_data.get('data', {}) if odds_data else {}
    
    print(f"✓ Found {len(live_matches)} live matches")
    print(f"✓ Found {len(details_matches)} detailed matches")
    print(f"✓ Found odds for {len(odds_by_match)} matches")
    
    # Get all unique match IDs
    all_match_ids = set(live_matches.keys()) | set(details_matches.keys())
    print(f"✓ Total unique matches to process: {len(all_match_ids)}")
    
    # Merge data for each match
    merged_matches = []
    
    print("\nProcessing matches...")
    for i, match_id in enumerate(sorted(all_match_ids), 1):
        live_match = live_matches.get(match_id)
        details_match = details_matches.get(match_id)
        
        print(f"Processing match {i}/{len(all_match_ids)}: {match_id}")
        
        # Show team names if available
        if details_match:
            home_team = resolve_team_name(details_match.get('home_team_id', ''), teams_cache)
            away_team = resolve_team_name(details_match.get('away_team_id', ''), teams_cache)
            print(f"  {home_team['short_name']} vs {away_team['short_name']}")
        
        # Find odds data for this match - direct lookup from odds_by_match
        match_odds = odds_by_match.get(match_id)
        
        # If no direct match found, odds will be None and handled properly by merge_match_data
        
        merged_match = merge_match_data(
            match_id, live_match, details_match, match_odds,
            teams_cache, competitions_cache, countries_cache
        )
        
        merged_matches.append(merged_match)
    
    # Calculate pipeline completion time
    pipeline_end_time = time.time()
    pipeline_duration = pipeline_end_time - pipeline_start_time
    
    # Count in-play matches (status_id 2-7)
    in_play_count = 0
    for match in merged_matches:
        if 'live_status' in match and 'status_id' in match['live_status']:
            status_id = match['live_status']['status_id']
            if 2 <= status_id <= 7:
                in_play_count += 1
    
    # Get New York timezone
    ny_tz = pytz.timezone('America/New_York')
    ny_time = datetime.now(ny_tz)
    
    # Format footer timestamp in NYC time (MM/DD/YYYY HH:MM:SS AM/PM EST/EDT)
    footer_timestamp = ny_time.strftime("%m/%d/%Y %I:%M:%S %p %Z")
    footer_line = f"--- Merge.py pipeline completed: {footer_timestamp} | Total pipeline time: {pipeline_duration:.3f}s ---\nIn-Play Matches: {in_play_count}"
    
    # Create final merged data structure
    final_merged_data = {
        'merge_metadata': {
            'timestamp': datetime.now().isoformat(),
            'total_matches': len(merged_matches),
            'data_sources': {
                'live_matches': len(live_matches),
                'details_matches': len(details_matches),
                'odds_matches': len(odds_by_match) if odds_data else 0,
                'teams_cached': len(teams_cache),
                'competitions_cached': len(competitions_cache), 
                'countries_cached': len(countries_cache)
            },
            'merge_version': '1.0',
            'pipeline_duration_seconds': round(pipeline_duration, 3),
            'completion_timestamp_nyc': footer_timestamp,
            'in_play_matches': in_play_count
        },
        'matches': merged_matches,
        'footer_completion': f"--- Merge.py pipeline completed: {footer_timestamp} | Total pipeline time: {pipeline_duration:.3f}s ---",
        'in_play_summary': f"In-Play Matches: {in_play_count}"
    }
    
    # Save merged data
    output_file = '/workspaces/TMUX_FINAL_SPORTS/logs/merge/merge.json'
    output_dir = os.path.dirname(output_file)
    
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created directory: {output_dir}")
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(final_merged_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Merge completed successfully!")
        print(f"✓ Output saved to: {output_file}")
        print(f"✓ Total matches merged: {len(merged_matches)}")
        print(f"✓ File size: {os.path.getsize(output_file):,} bytes")
        
        # Print sample merged match for verification
        if merged_matches:
            print(f"\n📋 Sample merged match (ID: {merged_matches[0]['match_id']}):")
            sample = merged_matches[0]
            if 'teams' in sample:
                print(f"  Teams: {sample['teams']['home']['short_name']} vs {sample['teams']['away']['short_name']}")
            if 'competition' in sample:
                print(f"  Competition: {sample['competition']['short_name']}")
            if 'live_status' in sample:
                print(f"  Status: {sample['live_status']['status_text']}")
            if 'score_summary' in sample:
                print(f"  Score: {sample['score_summary']['home_total']}-{sample['score_summary']['away_total']}")
        
        print(f"\n{footer_line}")
        
    except Exception as e:
        print(f"❌ Error saving merged data: {e}")
        return 1
    
    return 0

def trigger_next_stage():
    """Call pretty print stage for formatted output"""
    print("\n🎨 Calling pretty_print.py for formatted output...")
    
    try:
        subprocess.run(['python3', 'pretty_print.py'], check=True)
        print("✅ Pretty print completed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running pretty_print.py: {e}")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error with pretty_print.py: {e}")
        return 1
    
    return 0

def main():
    """Main entry point"""
    merge_exit_code = main_merge()
    if merge_exit_code == 0:
        return trigger_next_stage()
    else:
        return merge_exit_code

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)