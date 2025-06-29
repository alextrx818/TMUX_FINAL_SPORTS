#!/usr/bin/env python3

import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional
import pytz

def load_monitoring_data() -> Optional[Dict[str, Any]]:
    """Load monitoring.json data with error handling"""
    source_file = '/workspaces/TMUX_FINAL_SPORTS/logs/monitoring/monitoring.json'
    
    try:
        if os.path.exists(source_file):
            with open(source_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            print(f"ERROR: Source file not found: {source_file}")
            return None
    except Exception as e:
        print(f"ERROR: Failed to load data: {e}")
        return None

def extract_match_fields(match: Dict[str, Any]) -> Dict[str, Any]:
    """Extract fields using defensive patterns with individual logic"""
    
    # PASSTHROUGH: Copy all fields from source match as-is
    # Individual field processing logic can be added here later
    extracted = {}
    
    # Copy all fields from the source match
    for field_name, field_value in match.items():
        extracted[field_name] = field_value
    
    return extracted

def create_output(source_data: Dict[str, Any], processed_matches: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Create output with structure preservation"""
    
    ny_tz = pytz.timezone('US/Eastern')
    current_time = datetime.now(ny_tz)
    
    output = {
        "alert_metadata": {
            "generated_at": current_time.isoformat(),
            "generated_at_readable": current_time.strftime('%m/%d/%Y %I:%M:%S %p %Z'),
            "total_matches": len(processed_matches),
            "source_file": "monitoring.json",
            "version": "1.0"
        },
        "matches": processed_matches
    }
    
    return output

def save_data(output_data: Dict[str, Any]) -> bool:
    """Save data with error handling"""
    output_dir = '/workspaces/TMUX_FINAL_SPORTS/logs/alert'
    output_file = os.path.join(output_dir, 'alert.json')
    
    try:
        # Create directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Save the data
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Alert data saved to: {output_file}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to save alert data: {e}")
        return False

def trigger_next_stage():
    """Trigger next pipeline stage after successful completion"""
    # TODO: Add next stage triggering logic when next stage is created
    print("📋 Alert processing completed - ready for next stage")
    pass

def main() -> int:
    """Main processing with defensive patterns"""
    print("🚨 Starting Alert Processing...")
    
    # Load source data
    source_data = load_monitoring_data()
    if not source_data:
        print("❌ Failed to load source data")
        return 1
    
    # Validate source data structure
    if "matches" not in source_data or not isinstance(source_data["matches"], list):
        print("❌ Invalid source data structure")
        return 1
    
    print(f"📊 Processing {len(source_data['matches'])} matches...")
    
    # Process matches (skeleton only - no actual processing yet)
    processed_matches = []
    
    for match in source_data["matches"]:
        if isinstance(match, dict):
            # Extract fields using defensive patterns
            extracted_match = extract_match_fields(match)
            if extracted_match:  # Only add if extraction was successful
                processed_matches.append(extracted_match)
    
    # Create output structure
    output_data = create_output(source_data, processed_matches)
    
    # Save data
    if save_data(output_data):
        print(f"✅ Successfully processed {len(processed_matches)} matches")
        trigger_next_stage()
        return 0
    else:
        print("❌ Failed to save processed data")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)