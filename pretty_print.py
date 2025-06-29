#!/usr/bin/env python3

"""
=============================================================================
PRETTY_PRINT.PY - PIPELINE DATA FORMATTER & FILTER
=============================================================================

MODIFICATION NOTE:
Modified pretty_conversion.py to remove analysis metadata and extract clean field values 
instead of detailed field analysis. The conversion now produces clean data format 
similar to pretty_print.json rather than comprehensive field analysis metadata.

PURPOSE:
This is the FINAL STEP in the TMUX_FINAL_SPORTS data pipeline. It takes the 
comprehensive merge.json output and creates a clean, filtered version containing 
only essential match data for end-user consumption.

# ========================================
# PIPELINE CALLING STANDARD - PRETTY_PRINT.PY
# ========================================
# POSITION: merge.py → pretty_print.py → pretty_conversion.py [TERMINAL]
# CALLS NEXT: trigger_next_stage() → subprocess.run(['python3', 'pretty_conversion.py'], check=True)
# PATTERN: Standard pipeline pattern with try/except CalledProcessError handling
# ========================================

PIPELINE POSITION:
live.py → details.py → teams.py/competitions.py/countries.py → merge.py → **PRETTY_PRINT.PY** → pretty_conversion.py

TRIGGER/INITIATION:
- Automatically called by merge.py after successful completion
- Triggered via: subprocess.run(['python3', 'pretty_print.py'], check=True)
- Follows standard pipeline calling pattern

TASK OVERVIEW:
1. READ: /workspaces/TMUX_FINAL_SPORTS/logs/merge/merge.json (comprehensive data)
2. FILTER: Extract only specific essential fields from each match
3. TRANSFORM: Convert timestamps to NY Eastern time format (MM/DD/YYYY HH:MM AM/PM)  
4. OUTPUT: /workspaces/TMUX_FINAL_SPORTS/logs/pretty_print/pretty_print.json (clean data)

SPECIFIC FIELDS EXTRACTED:
Core Match Info:
- match_id (unique identifier)
- timestamp (processing time, converted to NY Eastern)
- scheduled_time_readable (match start time, converted to NY Eastern)

Teams & Competition:
- competition.name (league/tournament name)
- teams.home.name / teams.away.name (team names)

Scores:
- score_summary.home_total / away_total (current scores)
- score_summary.home_ft / away_ft (full-time scores)  
- score_summary.home_ht / away_ht (half-time scores)

Optional Data (only if present):
- var_incidents[] (Video Assistant Referee decisions)
- odds{} (betting odds by company)
- environment{} (weather, temperature, pressure, wind, humidity)

OUTPUT STRUCTURE:
{
  "pretty_print_metadata": {
    "generated_at": "ISO timestamp",
    "generated_at_readable": "MM/DD/YYYY HH:MM:SS AM/PM EST",
    "total_matches": count,
    "source_file": "merge.json",
    "version": "1.0"
  },
  "matches": [ filtered match objects ],
  "footer_completion": "timestamp message"
}

HOW IT WORKS:
1. Loads merge.json (exits silently if not found)
2. Iterates through each match in merge_data.matches[]
3. Extracts only the specified fields using extract_match_fields()
4. Converts Unix timestamps to NY Eastern readable format
5. Creates filtered output structure with metadata
6. Saves to pretty_print.json (creates directory if needed)
7. Returns success/failure status (no console output)

ERROR HANDLING:
- Missing merge.json: prints error and exits
- Invalid JSON: prints error and exits
- File write errors: prints error and returns failure
- All other processing: silent operation

TIMEZONE CONVERSION:
- Input: Unix timestamps and ISO timestamps
- Output: "MM/DD/YYYY HH:MM AM/PM" in US/Eastern timezone
- Handles both live timestamps and scheduled match times

FUTURE REFERENCE:
This file should remain simple and focused. It's designed as a pure data 
transformer with no complex logic. If additional fields are needed, update 
extract_match_fields() function. The field list is guided by the 
merge.json-field-checklist.md communication protocol.

=============================================================================
"""

import json
import os
import sys
import subprocess
from datetime import datetime
from typing import Dict, List, Any, Optional
import pytz

def load_merge_data() -> Optional[Dict[str, Any]]:
    """Load merge.json data"""
    merge_file = '/workspaces/TMUX_FINAL_SPORTS/logs/merge/merge.json'
    
    try:
        if os.path.exists(merge_file):
            with open(merge_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            print(f"ERROR: Merge file not found: {merge_file}")
            return None
    except Exception as e:
        print(f"ERROR: Failed to load merge data: {e}")
        return None

def convert_to_ny_time(timestamp: Optional[str]) -> str:
    """Convert ISO timestamp to NY Eastern time MM/DD/YYYY HH:MM AM/PM"""
    if not timestamp:
        return "N/A"
    
    try:
        # Parse ISO timestamp
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        
        # Convert to NY Eastern timezone
        ny_tz = pytz.timezone('US/Eastern')
        ny_time = dt.astimezone(ny_tz)
        
        # Format as MM/DD/YYYY HH:MM AM/PM
        return ny_time.strftime('%m/%d/%Y %I:%M %p')
    except Exception as e:
        print(f"Warning: Failed to convert timestamp {timestamp}: {e}")
        return "N/A"

def convert_scheduled_time(unix_timestamp: Optional[int]) -> str:
    """Convert Unix timestamp to NY Eastern time MM/DD/YYYY HH:MM AM/PM"""
    if not unix_timestamp:
        return "N/A"
    
    try:
        # Convert Unix timestamp to datetime
        dt = datetime.fromtimestamp(unix_timestamp)
        
        # Convert to NY Eastern timezone
        ny_tz = pytz.timezone('US/Eastern')
        ny_time = ny_tz.localize(dt)
        
        # Format as MM/DD/YYYY HH:MM AM/PM
        return ny_time.strftime('%m/%d/%Y %I:%M %p')
    except Exception as e:
        print(f"Warning: Failed to convert scheduled time {unix_timestamp}: {e}")
        return "N/A"

def extract_match_fields(match: Dict[str, Any]) -> Dict[str, Any]:
    """Extract only the specified fields from a match record"""
    
    # Extract basic match info
    extracted = {
        "match_id": match.get("match_id", ""),
        "timestamp": convert_to_ny_time(match.get("timestamp")),
        "scheduled_time_readable": convert_scheduled_time(match.get("scheduled_time"))
    }
    
    # Extract details_status_id from merge.py
    if "details_status_id" in match:
        extracted["details_status_id"] = match["details_status_id"]
    
    # Extract competition info
    competition = match.get("competition", {})
    extracted["competition"] = {
        "name": competition.get("name", "Unknown Competition")
    }
    
    # Extract teams info
    teams = match.get("teams", {})
    home_team = teams.get("home", {})
    away_team = teams.get("away", {})
    
    extracted["teams"] = {
        "home": {
            "name": home_team.get("name", "Unknown Team")
        },
        "away": {
            "name": away_team.get("name", "Unknown Team")
        }
    }
    
    # Extract raw score arrays
    scores = match.get("scores", {})
    extracted["home_scores"] = scores.get("home", [0,0,0,0,0,0,0])
    extracted["away_scores"] = scores.get("away", [0,0,0,0,0,0,0])
    
    # Extract VAR incidents (only if present)
    var_incidents = match.get("var_incidents", [])
    if var_incidents:
        extracted["var_incidents"] = []
        for incident in var_incidents:
            var_incident = {
                "type": incident.get("type", 0),
                "position": incident.get("position", 0),
                "time": incident.get("time", 0),
                "player_id": incident.get("player_id", ""),
                "player_name": incident.get("player_name", ""),
                "var_reason": incident.get("var_reason", 0),
                "var_result": incident.get("var_result", 0)
            }
            extracted["var_incidents"].append(var_incident)
    
    # Extract odds (only if present)
    odds = match.get("odds", {})
    if odds:
        extracted["odds"] = {}
        for company_id, company_data in odds.items():
            extracted["odds"][company_id] = {}
            
            # Extract each odds type
            for odds_type in ["asia", "eu", "bs", "cr"]:
                if odds_type in company_data:
                    extracted["odds"][company_id][odds_type] = company_data[odds_type]
    
    # Extract environment (only if present)
    environment = match.get("environment", {})
    if environment:
        extracted["environment"] = {
            "weather": environment.get("weather", 0),
            "pressure": environment.get("pressure", ""),
            "temperature": environment.get("temperature", ""),
            "wind": environment.get("wind", ""),
            "humidity": environment.get("humidity", "")
        }
    
    return extracted

def process_pretty_print():
    """Main processing function"""
    # Load merge data
    merge_data = load_merge_data()
    if not merge_data:
        print("ERROR: No merge data available")
        return False
    
    # Extract matches
    matches = merge_data.get("matches", [])
    if not matches:
        print("ERROR: No matches found in merge data")
        return False
    
    
    # Extract fields from each match
    pretty_matches = []
    for match in matches:
        extracted_match = extract_match_fields(match)
        pretty_matches.append(extracted_match)
    
    # Get NY timezone for timestamps
    ny_tz = pytz.timezone('US/Eastern')
    ny_time = datetime.now(ny_tz)
    
    # Create pretty print output structure
    pretty_output = {
        "pretty_print_metadata": {
            "generated_at": ny_time.isoformat(),
            "generated_at_readable": ny_time.strftime('%m/%d/%Y %I:%M:%S %p %Z'),
            "total_matches": len(pretty_matches),
            "source_file": "merge.json",
            "version": "1.0"
        },
        "matches": pretty_matches,
        "footer_completion": f"--- Pretty print completed: {ny_time.strftime('%m/%d/%Y %I:%M:%S %p %Z')} ---"
    }
    
    # Save to pretty_print.json
    output_file = '/workspaces/TMUX_FINAL_SPORTS/logs/pretty_print/pretty_print.json'
    output_dir = os.path.dirname(output_file)
    
    # Create output directory if needed
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created directory: {output_dir}")
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(pretty_output, f, indent=2, ensure_ascii=False)
        
        return True
        
    except Exception as e:
        print(f"❌ Error saving pretty print data: {e}")
        return False

def trigger_next_stage():
    """Call final conversion stage"""
    print("\n🎨 Calling pretty_conversion.py for final processing...")
    
    try:
        subprocess.run(['python3', 'pretty_conversion.py'], check=True)
        print("✅ Pretty conversion completed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running pretty_conversion.py: {e}")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error with pretty_conversion.py: {e}")
        return 1
    
    return 0

def main():
    """Main entry point"""
    success = process_pretty_print()
    if success:
        exit_code = trigger_next_stage()
        return exit_code
    else:
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

