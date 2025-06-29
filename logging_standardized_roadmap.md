# Logging Standardized Roadmap

## Overview
This document outlines the standardized logging logic implemented across all files in the TMUX_FINAL_SPORTS post-merge processing pipeline. The logging system is designed specifically for AI-assisted development with fault isolation and session recovery capabilities.

## Post-Merge Processing Pipeline

### Sequential Processing Chain
```
merge.py → pretty_print.py → pretty_conversion.py → monitoring.py
```

Each stage reads from the previous stage's output and logs its own transformed dataset independently.

## Standardized Logging Pattern

### 1. Unified Metadata Structure
**Applied to ALL 3 post-merge files:**

```json
"pretty_print_metadata": {
  "generated_at": "2025-06-28T23:04:27.225642-04:00",
  "generated_at_readable": "06/28/2025 11:04:27 PM EDT", 
  "total_matches": 36,
  "source_file": "{previous_stage}.json",
  "version": "1.0"
}
```

### 2. Sequential Source Chain Logic
- **pretty_print.py**: `source_file: "merge.json"`
- **pretty_conversion.py**: `source_file: "pretty_print.json"`
- **monitoring.py**: `source_file: "pretty_conversion.json"`

### 3. Individual Field Extraction Standard
**Core Pattern Used in ALL Files:**
```python
processed_match = {
    "match_id": match.get("match_id", ""),
    "timestamp": convert_timestamp(match.get("timestamp")),
    "competition": {"name": competition.get("name", "Unknown")},
    "teams": {
        "home": {"name": home_team.get("name", "Unknown Team")},
        "away": {"name": away_team.get("name", "Unknown Team")}
    }
    # ... field by field extraction continues
}
```

## Stage-Specific Logging Details

### Stage 1: pretty_print.py - Data Filtering & Timezone Conversion

**What Gets Logged:**
- Filtered match data with essential fields only
- Unix timestamps converted to NY Eastern timezone
- Competition names, team names, score arrays
- Optional data: VAR incidents, odds, environment

**Logging Timing:**
- After successful merge.json loading
- During filtering and timestamp conversion
- Before calling pretty_conversion.py

**Output Location:**
- `/workspaces/TMUX_FINAL_SPORTS/logs/pretty_print/pretty_print.json`

**Data Transformations:**
- Unix timestamps → `"MM/DD/YYYY HH:MM AM/PM"` format
- Field filtering to essential data only
- Timezone conversion to NY Eastern

### Stage 2: pretty_conversion.py - Format Conversion & Enhancement

**What Gets Logged:**
- Identical structure to pretty_print.py with converted values
- American odds format (converted from Hong Kong/European)
- Imperial environment units (Fahrenheit, mph, natural language weather)
- Filtered odds arrays (2nd earliest minute timing)

**Logging Timing:**
- After loading pretty_print.json
- During live odds conversion (Hong Kong → American, European → American)
- During environment conversions (Celsius → Fahrenheit, m/s → mph)
- Before calling monitoring.py

**Output Location:**
- `/workspaces/TMUX_FINAL_SPORTS/logs/pretty_conversion/pretty_conversion.json`

**Data Transformations:**
- European odds (2.0, 4.0) → American odds ("+300", "+400")
- Hong Kong odds (0.87, 0.92) → American odds ("-115", "-109")
- Temperature: "19°C" → "66°F"
- Wind: "3.2m/s" → "7mph (Gentle Breeze)"
- Weather codes (5) → Natural language ("Fair")

### Stage 3: monitoring.py - Terminal Field Processing & Array Decomposition

**What Gets Logged:**
- Individual score fields extracted from arrays
- String processing with `.strip()` operations
- Type-safe conversions with error handling
- Identical structure preservation with field-level extraction

**Logging Timing:**
- After loading pretty_conversion.json
- During score array decomposition (7-element arrays → individual fields)
- String validation and type safety processing
- Final terminal stage (no subsequent stage calls)

**Output Location:**
- `/workspaces/TMUX_FINAL_SPORTS/logs/monitoring/monitoring.json`

**Data Transformations:**
- Score arrays → Individual fields:
  ```json
  // From: "home_scores": [1, 0, 0, 2, 7, 0, 0]
  // To:
  "home_score_current": 1,
  "home_score_half": 0,
  "home_corners": 7
  ```

## Error Handling Standard

### Consistent Error Pattern Across All Files:
```python
try:
    # Load previous stage data
    # Process and transform data
    # Log transformed dataset
    with open(f"logs/{stage_name}/{stage_name}.json", "w") as f:
        json.dump(processed_data, f, indent=2)
    print(f"✅ {stage_name} completed - {len(processed)} matches processed")
except Exception as e:
    print(f"❌ {stage_name} logging failed: {e}")
```

## Console Logging Pattern

### Standard Progress Indicators:
```python
print(f"🔄 Processing {len(matches)} matches...")
print(f"✅ {stage_name} completed - {len(processed)} matches processed")
print(f"📊 Output logged to: logs/{stage_name}/{stage_name}.json")
```

## File System Organization

### Logging Directory Structure:
```
/workspaces/TMUX_FINAL_SPORTS/logs/
├── pretty_print/
│   └── pretty_print.json
├── pretty_conversion/
│   └── pretty_conversion.json
└── monitoring/
    └── monitoring.json
```

## AI Session Management Benefits

### 1. Independent Stage Recovery
- Each stage can be restarted from its log file
- No cross-dependencies between logging systems
- Clear data lineage through pipeline stages

### 2. Fault Isolation
- Stage failures contained to individual files
- Previous stages remain intact during failures
- Independent error handling per stage

### 3. Debugging Clarity
- Exact transformation point identification
- Clear input/output boundaries
- Field-by-field change tracking

### 4. Session Continuity
- Resume pipeline from any stage
- Maintain data integrity across AI sessions
- Checkpoint system for incremental development

## Data Flow Validation

### Sequential Validation Points:
1. **merge.json** → **pretty_print.json**: Field filtering + timezone conversion
2. **pretty_print.json** → **pretty_conversion.json**: Odds + environment conversion
3. **pretty_conversion.json** → **monitoring.json**: Array decomposition + field extraction

### Consistency Checks:
- Match count preservation across stages
- Match ID consistency validation
- Metadata timestamp progression
- Source file reference chain integrity

## Key Logging Standards

### Consistent Elements Across All Files:
1. **Metadata Structure**: Identical `pretty_print_metadata` format
2. **Timestamp Format**: NY Eastern with ISO + readable formats
3. **File Naming**: `{stage_name}.json` pattern
4. **Directory Structure**: Separate `/logs/{stage_name}/` directories
5. **Error Handling**: Try/catch blocks with graceful fallbacks
6. **Console Output**: Emoji-based progress indicators
7. **Pipeline Integration**: `trigger_next_stage()` pattern (except terminal monitoring.py)

### Progressive Data Evolution:
- **pretty_print.py**: Raw → Filtered + Timezone converted
- **pretty_conversion.py**: Filtered → American format + Imperial units
- **monitoring.py**: Converted → Individual named fields

### Independent Processing Requirements:
- **No Cross-Stage Dependencies**: Each file only logs its own output
- **No Previous Log Reading**: Only reads from immediate predecessor
- **Complete Data Independence**: Each log file can stand alone
- **Field-by-Field Extraction**: No bulk copying or lazy mirroring

## Conclusion

This standardized logging roadmap ensures:

- **Fault Tolerance**: Independent error handling and recovery
- **AI Compatibility**: Session recovery and incremental development
- **Data Integrity**: Field-by-field validation and transformation tracking
- **Development Velocity**: Clear boundaries and debugging capabilities
- **Production Readiness**: Comprehensive logging and monitoring support

The logging system creates a robust, traceable pipeline where each stage maintains data integrity while progressively transforming content for end-user consumption, perfectly supporting the part-by-part AI coding architecture.

---

**Generated**: 2025-06-28 | **Architecture**: TMUX_FINAL_SPORTS | **Purpose**: Logging Standards Documentation