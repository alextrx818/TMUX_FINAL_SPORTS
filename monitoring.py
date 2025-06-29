#!/usr/bin/env python3

"""
=============================================================================
MONITORING.PY - INDEPENDENT FIELD EXTRACTION & LOGGING
=============================================================================

# ========================================
# FIELD CONVERSION MODIFICATIONS LOG
# ========================================
# DATE: 06/29/2025 01:15 AM EST
# CHANGES MADE: HOME SCORES ARRAY CONVERSION
#
# ORIGINAL FORMAT (from pretty_conversion.json):
# "home_scores": [1, 1, 0, 2, 2, 0, 0]  // 7-element array
#
# NEW FORMAT (in monitoring.json):
# "home_score_current": 1    // Array[0] - Goals in regular time
# "home_score_half": 1       // Array[1] - Goals by halftime  
# "home_corners": 2          // Array[4] - Corner kicks
# "away_score_current": 0    // Array[0] - Goals in regular time
# "away_score_half": 0       // Array[1] - Goals by halftime
# "away_corners": 3          // Array[4] - Corner kicks
#
# CONVERSION LOCATION: extract_match_fields() function ~line 151
# PIPELINE IMPACT: All future monitoring.json outputs use new format
# STATUS: away_scores converted to individual fields (COMPLETED)
# ========================================

# ========================================
# API SCORE SCHEMA REFERENCE - THESPORTS.COM
# ========================================
# home_scores & away_scores Array[7] Structure:
# [0] Score (regular time)                                                              (Integer type)
# [1] Halftime score                                                                    (Integer type)  
# [2] Red cards                                                                         (Integer type)
# [3] Yellow cards                                                                      (Integer type)
# [4] Corners，-1 means no corner kick data                                             (Integer type)
# [5] Overtime score (120 minutes，including regular time)，only available in overtime  (Integer type)
# [6] Penalty shootout score，only penalty shootout                                     (Integer type)
#
# EXAMPLE: [1, 0, 0, 0, -1, 0, 0]
# • Position [0] = 1 (1 goal in regular time)
# • Position [1] = 0 (0 goals at halftime)
# • Position [2] = 0 (0 red cards)
# • Position [3] = 0 (0 yellow cards)
# • Position [4] = -1 (no corner kick data available)
# • Position [5] = 0 (0 overtime goals)
# • Position [6] = 0 (0 penalty shootout goals)
# ========================================

# ========================================
# PIPELINE CALLING STANDARD - MONITORING.PY
# ========================================
# POSITION: pretty_conversion.py → monitoring.py [TERMINAL - NO NEXT CALLS]
# CALLS NEXT: None - This is the final stage of the pipeline
# PATTERN: Standard pipeline pattern but NO trigger_next_stage() function (terminal)
# ========================================

# ========================================
# UPDATED PIPELINE INTEGRATION - JUNE 27, 2025
# ========================================
# 🔄 PIPELINE POSITION UPDATE:
# start.sh → live.py → details.py + odds.py → teams.py + competitions.py + countries.py → merge.py → pretty_print.py → pretty_conversion.py → **MONITORING.PY** [NEW TERMINAL]
#
# 📋 INTEGRATION NOTES:
# • pretty_conversion.py will be modified to call monitoring.py after completion
# • monitoring.py becomes the new terminal stage (replaces pretty_conversion.py as final)
# • Pipeline calling via: subprocess.run(['python3', 'monitoring.py'], check=True)
# • Follows established JSON Python Duplication Guideline pattern
# • Independent field extraction with identical structure preservation
# ========================================

PIPELINE POSITION:
start.sh → live.py → details.py + odds.py → teams.py/competitions.py/countries.py → merge.py → pretty_print.py → pretty_conversion.py → **MONITORING.PY** [TERMINAL]

TRIGGER/INITIATION:
- Automatically called by pretty_conversion.py after successful completion
- Triggered via: subprocess.run(['python3', 'monitoring.py'], check=True)
- Follows standard pipeline calling pattern

PURPOSE:
This module INDEPENDENTLY processes the output of pretty_conversion.py by:
1. Reading from pretty_conversion.json (NOT copying or mirroring)
2. IDENTIFYING and EXTRACTING each individual field from the JSON structure
3. Creating its own independent field analysis and processing
4. Logging results to its own independent monitoring.json file

INDEPENDENT FIELD EXTRACTION:
- Each JSON field is individually identified and extracted
- No copy/paste or mirroring operations
- Independent processing logic for each data type
- Separate logging system with its own file paths

OUTPUT:
- File: /workspaces/TMUX_FINAL_SPORTS/logs/monitoring/monitoring.json
- Independent logging system
- Field-by-field extraction results with identical structure

FUTURE ENHANCEMENTS:
- Foundation for sorting and filtering capabilities
- Advanced data manipulation and conversion features
- Enhanced monitoring and analysis functionality
=============================================================================
"""

import json
import os
import sys
import subprocess
from datetime import datetime
from typing import Dict, List, Any, Optional
import pytz

def load_pretty_conversion_data() -> Optional[Dict[str, Any]]:
    """Load pretty_conversion.json data independently"""
    source_file = '/workspaces/TMUX_FINAL_SPORTS/logs/pretty_conversion/pretty_conversion.json'
    
    try:
        if os.path.exists(source_file):
            with open(source_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            print(f"ERROR: Pretty conversion source file not found: {source_file}")
            return None
    except Exception as e:
        print(f"ERROR: Failed to load pretty conversion data: {e}")
        return None

def extract_match_fields(match: Dict[str, Any]) -> Dict[str, Any]:
    """Extract fields using IDENTICAL structure as pretty_conversion.json with independent logic"""
    
    # Initialize extracted match with independent processing
    extracted = {}
    
    # Independent extraction of basic match info
    if "match_id" in match:
        extracted["match_id"] = str(match["match_id"]).strip()
    
    if "timestamp" in match:
        extracted["timestamp"] = str(match["timestamp"]).strip()
    
    if "scheduled_time_readable" in match:
        extracted["scheduled_time_readable"] = str(match["scheduled_time_readable"]).strip()
    
    # Independent extraction of competition with structure preservation
    if "competition" in match and isinstance(match["competition"], dict):
        competition_data = match["competition"]
        extracted["competition"] = {}
        
        if "name" in competition_data:
            extracted["competition"]["name"] = str(competition_data["name"]).strip()
    
    # Independent extraction of teams with structure preservation
    if "teams" in match and isinstance(match["teams"], dict):
        teams_data = match["teams"]
        extracted["teams"] = {}
        
        # Independent home team extraction
        if "home" in teams_data and isinstance(teams_data["home"], dict):
            home_team = teams_data["home"]
            extracted["teams"]["home"] = {}
            if "name" in home_team:
                extracted["teams"]["home"]["name"] = str(home_team["name"]).strip()
        
        # Independent away team extraction
        if "away" in teams_data and isinstance(teams_data["away"], dict):
            away_team = teams_data["away"]
            extracted["teams"]["away"] = {}
            if "name" in away_team:
                extracted["teams"]["away"]["name"] = str(away_team["name"]).strip()
    
    # Independent extraction of score data with FIELD CONVERSION
    # HOME SCORES: Convert 7-element array to individual named fields
    if "home_scores" in match and isinstance(match["home_scores"], list):
        home_scores_array = match["home_scores"]
        if len(home_scores_array) >= 5:  # Ensure array has enough elements
            extracted["home_score_current"] = home_scores_array[0]  # Goals in regular time
            extracted["home_score_half"] = home_scores_array[1]     # Goals by halftime
            extracted["home_corners"] = home_scores_array[4]        # Corner kicks
    
    
    # Visual spacing separator before away scores
    extracted[""] = ""
    
    # AWAY SCORES: Convert 7-element array to individual named fields  
    if "away_scores" in match and isinstance(match["away_scores"], list):
        away_scores_array = match["away_scores"]
        if len(away_scores_array) >= 5:  # Ensure array has enough elements
            extracted["away_score_current"] = away_scores_array[0]  # Goals in regular time
            extracted["away_score_half"] = away_scores_array[1]     # Goals by halftime
            extracted["away_corners"] = away_scores_array[4]        # Corner kicks
    
    # Independent extraction of details_status_id with IDENTICAL structure
    if "details_status_id" in match:
        extracted["details_status_id"] = match["details_status_id"]
    
    # Independent extraction of VAR incidents with structure preservation
    if "var_incidents" in match and isinstance(match["var_incidents"], list):
        var_incidents_data = match["var_incidents"]
        extracted["var_incidents"] = []
        
        for incident in var_incidents_data:
            if isinstance(incident, dict):
                extracted_incident = {}
                
                # Independent extraction of each VAR field
                var_fields = ["type", "position", "time", "player_id", "player_name", "var_reason", "var_result"]
                for field in var_fields:
                    if field in incident:
                        if field in ["type", "position", "time", "var_reason", "var_result"]:
                            try:
                                extracted_incident[field] = int(incident[field])
                            except (ValueError, TypeError):
                                extracted_incident[field] = incident[field]
                        else:
                            extracted_incident[field] = str(incident[field]).strip()
                
                extracted["var_incidents"].append(extracted_incident)
    
    # Independent extraction of odds with structure preservation
    if "odds" in match and isinstance(match["odds"], dict):
        odds_data = match["odds"]
        extracted["odds"] = {}
        
        for company_id, company_data in odds_data.items():
            if isinstance(company_data, dict):
                extracted["odds"][str(company_id)] = {}
                
                # Independent extraction of each odds type
                odds_types = ["spread", "MoneyLine", "Over/Under", "Corners"]
                for odds_type in odds_types:
                    if odds_type in company_data and isinstance(company_data[odds_type], list):
                        extracted["odds"][str(company_id)][odds_type] = []
                        
                        for odds_array in company_data[odds_type]:
                            if isinstance(odds_array, list) and len(odds_array) >= 8:
                                # Independent processing of each array element
                                processed_array = []
                                for i, element in enumerate(odds_array):
                                    if i in [0, 5, 6]:  # timestamp, status1, status2
                                        try:
                                            processed_array.append(int(element))
                                        except (ValueError, TypeError):
                                            processed_array.append(element)
                                    elif i in [1, 7]:  # period, score
                                        processed_array.append(str(element))
                                    elif i in [2, 4]:  # odds values (converted to American)
                                        processed_array.append(str(element))
                                    elif i == 3:  # line value (handicap/total)
                                        try:
                                            processed_array.append(float(element))
                                        except (ValueError, TypeError):
                                            processed_array.append(element)
                                    else:
                                        processed_array.append(element)
                                
                                extracted["odds"][str(company_id)][odds_type].append(processed_array)
    
    # Independent extraction of environment with structure preservation
    if "environment" in match and isinstance(match["environment"], dict):
        environment_data = match["environment"]
        extracted["environment"] = {}
        
        # Independent extraction of each environment field
        env_fields = ["weather", "pressure", "temperature", "wind", "humidity"]
        for field in env_fields:
            if field in environment_data:
                extracted["environment"][field] = str(environment_data[field]).strip()
    
    return extracted

def create_monitoring_output(source_data: Dict[str, Any], monitored_matches: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Create monitoring output with IDENTICAL structure as pretty_conversion.json"""
    
    # Get current NY timezone
    ny_tz = pytz.timezone('US/Eastern')
    monitoring_time = datetime.now(ny_tz)
    
    # Create output with IDENTICAL structure to pretty_conversion.json
    monitoring_output = {
        "pretty_print_metadata": {
            "generated_at": monitoring_time.isoformat(),
            "generated_at_readable": monitoring_time.strftime('%m/%d/%Y %I:%M:%S %p %Z'),
            "total_matches": len(monitored_matches),
            "source_file": "pretty_conversion.json",
            "version": "1.0"
        },
        "matches": monitored_matches,
        "footer_completion": f"--- Monitoring completed: {monitoring_time.strftime('%m/%d/%Y %I:%M:%S %p %Z')} ---"
    }
    
    return monitoring_output

def load_existing_monitoring_log() -> Dict[str, Any]:
    """Load existing accumulating monitoring log or create new structure"""
    log_file = '/workspaces/TMUX_FINAL_SPORTS/logs/monitoring/monitoring.json'
    
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
        print(f"Error loading existing monitoring log: {e}")
        return {
            "log_metadata": {
                "total_fetches": 0,
                "first_fetch": "",
                "last_fetch": "",
                "log_format": "accumulating_v1.0"
            },
            "fetch_history": []
        }

def archive_old_monitoring_fetches(accumulated_log: Dict[str, Any]) -> Dict[str, Any]:
    """Archive old fetches when exceeding 50 fetch limit"""
    max_history = 50
    
    if len(accumulated_log["fetch_history"]) > max_history:
        # Create archive directory
        archive_dir = '/workspaces/TMUX_FINAL_SPORTS/logs/monitoring/archive'
        os.makedirs(archive_dir, exist_ok=True)
        
        # Archive excess fetches
        excess_fetches = accumulated_log["fetch_history"][:-max_history]
        ny_tz = pytz.timezone('US/Eastern')
        archive_timestamp = datetime.now(ny_tz).strftime('%Y%m%d_%H%M%S')
        archive_file = f"{archive_dir}/monitoring_archive_{archive_timestamp}.json"
        
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
        
        print(f"Archived {len(excess_fetches)} old monitoring fetches to {archive_file}")
    
    return accumulated_log

def save_monitoring_data(processed_matches: List[Dict[str, Any]]) -> bool:
    """Save monitoring data with accumulating log pattern and archive rotation"""
    
    # Load existing accumulating log
    accumulated_log = load_existing_monitoring_log()
    
    # Get NY timezone
    ny_tz = pytz.timezone('US/Eastern')
    current_time = datetime.now(ny_tz)
    
    # Create new fetch entry
    new_fetch_entry = {
        "fetch_timestamp": current_time.isoformat(),
        "fetch_number": len(accumulated_log["fetch_history"]) + 1,
        "processed_data": {
            "matches": processed_matches,
            "total_matches": len(processed_matches)
        },
        "processing_metadata": {
            "source_file": "pretty_conversion.json",
            "processing_time": current_time.strftime('%m/%d/%Y %I:%M:%S %p %Z'),
            "status": "success"
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
    accumulated_log = archive_old_monitoring_fetches(accumulated_log)
    
    # Ensure output directory exists
    output_dir = '/workspaces/TMUX_FINAL_SPORTS/logs/monitoring'
    os.makedirs(output_dir, exist_ok=True)
    
    # Save accumulating log
    output_file = f'{output_dir}/monitoring.json'
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(accumulated_log, f, indent=2, ensure_ascii=False)
        
        # MANDATORY: NY Eastern time footer (LAST LINE OF EVERY FETCH)
        ny_time_footer = current_time.strftime('%m/%d/%Y %I:%M:%S %p')
        print(f"✅ monitoring.py completed: {ny_time_footer} EST")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to save monitoring data: {e}")
        return False

def trigger_next_stage():
    """Call alerts.py stage"""
    print(f"\n🔄 Calling alerts.py for final processing...")
    
    try:
        subprocess.run(['python3', 'alerts.py'], check=True)
        print(f"✅ alerts.py completed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running alerts.py: {e}")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error with alerts.py: {e}")
        return 1
    
    return 0

def main():
    """Main independent field extraction and monitoring process"""
    
    print("🔄 Starting independent field extraction from pretty_conversion.json...")
    
    # Load source data independently
    source_data = load_pretty_conversion_data()
    if not source_data:
        print("❌ Failed to load source data for independent processing")
        return 1
    
    # Extract matches list independently
    source_matches = source_data.get("matches", [])
    if not source_matches:
        print("❌ No matches found in source data for extraction")
        return 1
    
    print(f"📊 Processing {len(source_matches)} matches with INDEPENDENT field extraction...")
    
    # Process each match using INDEPENDENT logic
    monitored_matches = []
    for i, match in enumerate(source_matches, 1):
        print(f"   Independently extracting fields from match {i}/{len(source_matches)}: {match.get('match_id', 'UNKNOWN')}")
        monitored_match = extract_match_fields(match)
        monitored_matches.append(monitored_match)
    
    # Save with accumulating log pattern
    success = save_monitoring_data(monitored_matches)
    
    if success:
        print(f"✅ Independent field extraction completed with IDENTICAL structure")
        print(f"📁 Output: /workspaces/TMUX_FINAL_SPORTS/logs/monitoring/monitoring.json")
        
        # Call next stage in pipeline
        exit_code = trigger_next_stage()
        return exit_code
    else:
        print("❌ Independent field extraction failed")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)