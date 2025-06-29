# AI Agent Instructions: New Pipeline Stage Individual Field Extraction

## Overview

These instructions are for creating a new pipeline stage after monitoring.py that implements **defensive field extraction patterns** with **skeleton-first development**. The new agent must build the skeleton structure first before adding any processing logic.

## Critical Requirements

### 🛡️ MANDATORY: Defensive Field Extraction Pattern
- **TEMPLATE SOURCE**: Use monitoring.py as the gold standard (Score: 75/100)
- **NO LAZY MIRRORING**: Extract every field individually with independent logic
- **STRUCTURE PRESERVATION**: Maintain identical JSON structure as source file
- **DEFENSIVE PROGRAMMING**: Apply all safety patterns consistently

### 📋 Step-by-Step Process

#### Phase 1: Skeleton Creation (REQUIRED FIRST)
1. **Identify Source**: monitoring.json is your input file
2. **Analyze Structure**: Use AST analysis to identify all fields
3. **Create Skeleton**: Build empty function structure with defensive patterns
4. **NO PROCESSING**: Only create structure, no conversion logic yet

#### Phase 2: Field Extraction (After Skeleton)
1. **Individual Extraction**: Extract each field separately
2. **Apply Defensive Patterns**: Use all required safety patterns
3. **Structure Preservation**: Maintain exact JSON hierarchy
4. **Independent Logic**: Write unique extraction code for each field

## Mandatory Defensive Programming Patterns

### 1. Safe Field Access with Fallbacks
```python
# ✅ REQUIRED PATTERN
field_value = match.get("field_name", "")  # Always provide fallback
timestamp = match.get("timestamp", "")
match_id = match.get("match_id", "")

# ❌ FORBIDDEN PATTERN  
field_value = match["field_name"]  # No direct access
```

### 2. Type Validation Before Processing
```python
# ✅ REQUIRED PATTERN
if "teams" in match and isinstance(match["teams"], dict):
    teams_data = match["teams"]
    # Safe to process teams_data

# ✅ REQUIRED PATTERN  
if "home_scores" in match and isinstance(match["home_scores"], list):
    scores_array = match["home_scores"]
    # Safe to process array
```

### 3. Safe Array Access with Length Validation
```python
# ✅ REQUIRED PATTERN
if "home_scores" in match and isinstance(match["home_scores"], list):
    scores_array = match["home_scores"]
    if len(scores_array) >= 1:  # Check length first
        current_score = scores_array[0]  # Now safe to access

# ❌ FORBIDDEN PATTERN
current_score = match["home_scores"][0]  # No length check
```

### 4. String Cleaning with Safety
```python
# ✅ REQUIRED PATTERN
team_name = str(home_team["name"]).strip()  # Clean strings
competition_name = str(competition_data["name"]).strip()

# Apply to ALL string fields
```

### 5. Error Handling for Risky Operations
```python
# ✅ REQUIRED PATTERN
try:
    numeric_value = int(field_value)
except (ValueError, TypeError):
    numeric_value = 0  # Fallback default
```

## Required Function Signatures

### 1. Main Processing Function
```python
def extract_match_fields(match: Dict[str, Any]) -> Dict[str, Any]:
    """Extract fields using IDENTICAL structure with independent logic"""
    
    # Initialize with empty structure
    extracted = {}
    
    # Safe field access with fallbacks
    match_id = match.get("match_id", "")
    timestamp = match.get("timestamp", "")
    
    # Type validation before processing nested objects  
    if "competition" in match and isinstance(match["competition"], dict):
        competition_data = match["competition"]
        extracted["competition"] = {}
        
        # Safe extraction with string cleaning
        if "name" in competition_data:
            extracted["competition"]["name"] = str(competition_data["name"]).strip()
    
    # Safe array access with length validation
    if "home_scores" in match and isinstance(match["home_scores"], list):
        scores_array = match["home_scores"]
        if len(scores_array) >= 1:
            current_score = scores_array[0]
            # Process with fallback defaults
    
    return extracted
```

### 2. Data Loading Function
```python
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
```

### 3. Output Creation Function
```python
def create_output(source_data: Dict[str, Any], processed_matches: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Create output with IDENTICAL structure preservation"""
    
    ny_tz = pytz.timezone('US/Eastern')
    current_time = datetime.now(ny_tz)
    
    output = {
        "pretty_print_metadata": {
            "generated_at": current_time.isoformat(),
            "generated_at_readable": current_time.strftime('%m/%d/%Y %I:%M:%S %p %Z'),
            "total_matches": len(processed_matches),
            "source_file": "monitoring.json",
            "version": "1.0"
        },
        "matches": processed_matches
    }
    
    return output
```

## Pipeline Integration Requirements

### File Naming Convention
- **Pattern**: `[stage_name].py` (e.g., `analysis.py`, `filtering.py`)
- **Location**: `/workspaces/TMUX_FINAL_SPORTS/[stage_name].py`

### Calling Pattern (For Next Stage)
```python
# Add this to end of main() function if calling next stage
def trigger_next_stage():
    """Trigger next pipeline stage after successful completion"""
    try:
        result = subprocess.run(['python3', 'next_stage.py'], check=True)
        print("✅ Next stage triggered successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to trigger next stage: {e}")
```

### 🔗 **AUTOMATIC CHAINING INTEGRATION**

To add your new stage to the automatic pipeline, modify the **previous stage** to call your new file:

**Example: Adding `alert.py` to monitoring.py**
```python
# Add this function to monitoring.py:
def trigger_next_stage():
    """Call alert.py stage after monitoring completion"""
    try:
        subprocess.run(['python3', 'alert.py'], check=True)
        print("✅ Alert stage completed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Alert stage failed: {e}")

# Call it at the end of main() function:
if save_data(output_data):
    print(f"✅ Successfully processed {len(processed_matches)} matches")
    trigger_next_stage()  # Add this line
    return 0
```

This ensures your new stage gets called automatically when the previous stage finishes its task.

### Directory Structure
```
/workspaces/TMUX_FINAL_SPORTS/
├── [your_stage].py                    # Your new pipeline file
└── logs/
    ├── monitoring/
    │   └── monitoring.json            # Your INPUT file
    └── [your_stage]/
        └── [your_stage].json          # Your OUTPUT file
```

## Field Extraction Requirements

### 1. Identify ALL Fields
- **Source Analysis**: Read monitoring.json completely
- **Field Mapping**: Document every field in the JSON structure
- **Nested Objects**: Handle teams, competition, odds, environment
- **Arrays**: Process home_scores, away_scores, odds arrays

### 2. Extract Individual Fields
```python
# Example for complex nested structure
if "teams" in match and isinstance(match["teams"], dict):
    teams_data = match["teams"]
    extracted["teams"] = {}
    
    # Home team extraction
    if "home" in teams_data and isinstance(teams_data["home"], dict):
        home_team = teams_data["home"]
        extracted["teams"]["home"] = {}
        
        # Individual field extraction with safety
        if "name" in home_team:
            extracted["teams"]["home"]["name"] = str(home_team["name"]).strip()
    
    # Away team extraction (separate logic)
    if "away" in teams_data and isinstance(teams_data["away"], dict):
        away_team = teams_data["away"]
        extracted["teams"]["away"] = {}
        
        # Individual field extraction with safety
        if "name" in away_team:
            extracted["teams"]["away"]["name"] = str(away_team["name"]).strip()
```

### 3. Handle All Data Types
- **Strings**: Use `.strip()` cleaning
- **Numbers**: Validate with try/except
- **Arrays**: Check length before access
- **Objects**: Validate with isinstance()
- **Booleans**: Convert safely with fallbacks

## Success Criteria

### Phase 1 Completion (Skeleton)
- ✅ All required functions created with proper signatures
- ✅ Defensive patterns applied to all field access
- ✅ Input/output file paths configured
- ✅ Error handling implemented
- ✅ **NO processing logic yet** - just skeleton

### Phase 2 Completion (Implementation)
- ✅ Every field from monitoring.json individually extracted
- ✅ Identical JSON structure preserved
- ✅ All defensive patterns consistently applied
- ✅ Independent processing logic (no copy/paste)
- ✅ Proper file output with timestamps

### Quality Standards
- **Defensive Score**: Must achieve 70+ (monitoring.py = 75)
- **Individual Extraction**: Every field processed separately
- **Structure Preservation**: Exact JSON hierarchy maintained
- **Error Resilience**: Handles missing/malformed data gracefully

## Important Notes

### What NOT to Do
- ❌ **NO lazy mirroring** - don't copy entire structures
- ❌ **NO direct field access** - always use .get() with defaults
- ❌ **NO unsafe array access** - always check length first
- ❌ **NO skipping type validation** - use isinstance() consistently
- ❌ **NO processing in skeleton phase** - structure only first

### Pipeline Position
- **INPUT**: `/workspaces/TMUX_FINAL_SPORTS/logs/monitoring/monitoring.json`
- **OUTPUT**: `/workspaces/TMUX_FINAL_SPORTS/logs/[your_stage]/[your_stage].json`
- **POSITION**: monitoring.py → **[YOUR NEW STAGE]** → [future stages]
- **TRIGGER**: Called by monitoring.py via subprocess (if implemented)

## Example Implementation Pattern

```python
#!/usr/bin/env python3

import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional
import pytz

def load_monitoring_data() -> Optional[Dict[str, Any]]:
    """Load monitoring data with defensive patterns"""
    # Implementation here

def extract_match_fields(match: Dict[str, Any]) -> Dict[str, Any]:
    """Extract every field individually with defensive patterns"""
    extracted = {}
    
    # Basic fields with safety
    match_id = match.get("match_id", "")
    timestamp = match.get("timestamp", "")
    
    # Add defensive extraction for ALL fields from monitoring.json
    # ... (implement all field extractions)
    
    return extracted

def create_output(source_data: Dict[str, Any], processed_matches: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Create output with structure preservation"""
    # Implementation here

def save_data(output_data: Dict[str, Any]) -> bool:
    """Save data with error handling"""
    # Implementation here

def main():
    """Main processing with defensive patterns"""
    # Implementation here
    
if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
```

## Automatic Pipeline Chaining - CONFIRMED SYSTEM

### ✅ **VERIFIED WORKING ARCHITECTURE**

The automatic pipeline chaining system is **fully implemented and standardized** across all files using the subprocess.run() pattern:

**Complete Pipeline Flow:**
```
continuous_fetch.sh (60s cycle)
    ↓
live.py → details.py + odds.py (parallel)
    ↓ 
teams.py + competitions.py + countries.py (parallel)
    ↓
merge.py → pretty_print.py → pretty_conversion.py → monitoring.py
```

### 🔗 **Standard Chaining Pattern Applied Everywhere:**

- ✅ **live.py:302-304**: `subprocess.run(['python3', 'details.py'], check=True)` + `subprocess.run(['python3', 'odds.py'], check=True)`
- ✅ **details.py**: `subprocess.run(['python3', 'teams.py'], check=True)` + competitors + `subprocess.run(['python3', 'merge.py'], check=True)`  
- ✅ **merge.py**: `subprocess.run(['python3', 'pretty_print.py'], check=True)`
- ✅ **pretty_print.py**: `subprocess.run(['python3', 'pretty_conversion.py'], check=True)`
- ✅ **pretty_conversion.py**: `subprocess.run(['python3', 'monitoring.py'], check=True)`

### 📊 **Live System Evidence (June 29, 2025):**
- **monitoring.json**: 32 matches (06/29/2025 12:23:27 AM EDT)
- **details.json**: Active with match data (06/29/2025 12:23:26 AM EST)  
- **pretty_conversion.json**: 32 matches (06/29/2025 12:23:27 AM EDT)

**Status**: ✅ **PIPELINE IS ACTIVELY PROCESSING EVERY 60+ SECONDS**

The chaining mechanism is working perfectly. Each file automatically calls the next stage using subprocess.run() with proper error handling via CalledProcessError exception catching.

## Remember

1. **Skeleton First**: Build the structure before any processing logic
2. **Every Field**: Extract each field individually - no shortcuts
3. **Defensive Always**: Apply all safety patterns consistently  
4. **Structure Identical**: Maintain exact JSON hierarchy
5. **Independent Logic**: Write your own processing code for each field
6. **Pipeline Integration**: Use standard subprocess.run() pattern for chaining

This approach ensures robust, maintainable pipeline stages that handle data safely and consistently.