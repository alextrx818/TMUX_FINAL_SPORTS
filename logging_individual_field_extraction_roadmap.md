# Individual Field Extraction Logging Roadmap

## Overview
This document describes the **Individual Field Extraction Pattern** implemented across the TMUX_FINAL_SPORTS post-merge processing pipeline. This pattern represents a defensive coding approach that extracts each field individually with fallback defaults, enabling fault tolerance and AI session recovery.

## Core Pattern Definition

### Pattern Name: **Defensive Field Extraction with Fallback Defaults**

The Individual Field Extraction Pattern is characterized by:
- **No Lazy Mirroring**: Each field is explicitly extracted using `.get()` methods
- **Type Safety**: String processing with `.strip()` operations and type validation
- **Fault Isolation**: Missing fields don't crash the pipeline due to fallback defaults
- **AI Session Recovery**: Clear field boundaries enable precise debugging

## Implementation Examples

### 1. Basic Field Extraction (All Stages)
```python
# Pattern used in pretty_print.py, pretty_conversion.py, monitoring.py
extracted["match_id"] = str(match["match_id"]).strip()
extracted["timestamp"] = str(match["timestamp"]).strip()
```

### 2. Nested Structure Preservation
```python
# Competition extraction with defensive programming
if "competition" in match and isinstance(match["competition"], dict):
    competition_data = match["competition"]  
    extracted["competition"] = {}
    if "name" in competition_data:
        extracted["competition"]["name"] = str(competition_data["name"]).strip()
```

### 3. Team Structure Extraction
```python
# Independent home/away team processing
if "teams" in match and isinstance(match["teams"], dict):
    teams_data = match["teams"]
    extracted["teams"] = {}
    
    # Home team extraction
    if "home" in teams_data and isinstance(teams_data["home"], dict):
        home_team = teams_data["home"]
        extracted["teams"]["home"] = {}
        if "name" in home_team:
            extracted["teams"]["home"]["name"] = str(home_team["name"]).strip()
    
    # Away team extraction  
    if "away" in teams_data and isinstance(teams_data["away"], dict):
        away_team = teams_data["away"]
        extracted["teams"]["away"] = {}
        if "name" in away_team:
            extracted["teams"]["away"]["name"] = str(away_team["name"]).strip()
```

### 4. Array Decomposition (monitoring.py Specialty)
```python
# Convert 7-element score arrays to individual named fields
if "home_scores" in match and isinstance(match["home_scores"], list):
    home_scores_array = match["home_scores"]
    if len(home_scores_array) >= 5:  # Safety check
        extracted["home_score_current"] = home_scores_array[0]  # Goals
        extracted["home_score_half"] = home_scores_array[1]     # Halftime  
        extracted["home_corners"] = home_scores_array[4]        # Corners

# Visual spacing separator
extracted[""] = ""

# Away team score decomposition
if "away_scores" in match and isinstance(match["away_scores"], list):
    away_scores_array = match["away_scores"]
    if len(away_scores_array) >= 5:
        extracted["away_score_current"] = away_scores_array[0]
        extracted["away_score_half"] = away_scores_array[1]
        extracted["away_corners"] = away_scores_array[4]
```

## Pipeline Data Evolution

### Stage-by-Stage Transformation

| Stage | Input | Output | Field Extraction Focus |
|-------|--------|---------|----------------------|
| **details.json** | Raw API | Metric units, 7-element arrays | N/A (source data) |
| **pretty_conversion.json** | Raw API | American odds + imperial units | Currency/unit conversion |
| **monitoring.json** | Converted data | Individual named fields | Array decomposition |

### Example Data Flow

#### From details.json (Raw):
```json
{
  "home_scores": [1, 1, 0, 2, 7, 0, 0],
  "temperature": "16°C",
  "odds": {"2": {"MoneyLine": [[1751165392, "10", 1.25, "+275", 2, 1, "0-0"]]}}
}
```

#### To pretty_conversion.json (Converted):
```json
{
  "home_scores": [1, 1, 0, 2, 7, 0, 0],
  "temperature": "61°F", 
  "odds": {"2": {"MoneyLine": [[1751165392, "10", "-120", "+275", 2, 1, "0-0"]]}}
}
```

#### To monitoring.json (Individual Fields):
```json
{
  "home_score_current": 1,
  "home_score_half": 1, 
  "home_corners": 7,
  "": "",
  "away_score_current": 0,
  "away_score_half": 0,
  "away_corners": 0,
  "temperature": "61°F",
  "odds": {"2": {"MoneyLine": [[1751165392, "10", "-120", 275.0, 2, 1, "0-0"]]}}
}
```

## Technical Benefits

### 1. Fault Tolerance
- **Missing Field Handling**: `.get()` methods with fallback defaults prevent crashes
- **Type Safety**: Explicit type conversion with error handling
- **Structure Validation**: `isinstance()` checks before nested access

### 2. AI Session Management
- **Precise Error Location**: Field-by-field extraction enables exact error identification
- **Independent Recovery**: Each field extraction is isolated from others
- **Clear Debugging**: No bulk operations that obscure failure points

### 3. Development Velocity
- **Incremental Debugging**: Add fields one at a time during development
- **Change Isolation**: Modifications to one field don't affect others
- **Clear Intent**: Explicit field handling makes code self-documenting

## Error Handling Standards

### Defensive Programming Pattern
```python
try:
    # Individual field extraction with validation
    if field_name in source_data and isinstance(source_data[field_name], expected_type):
        extracted[field_name] = process_field(source_data[field_name])
    else:
        extracted[field_name] = default_value
except Exception as e:
    logger.error(f"Failed to extract {field_name}: {e}")
    extracted[field_name] = default_value
```

### Array Processing Safety
```python
if "array_field" in match and isinstance(match["array_field"], list):
    array_data = match["array_field"]
    if len(array_data) >= required_length:
        # Safe array access
        extracted["field1"] = array_data[0]
        extracted["field2"] = array_data[1]
    else:
        # Fallback for insufficient array length
        extracted["field1"] = default_value
        extracted["field2"] = default_value
```

## Contrast with Lazy Mirroring

### Individual Field Extraction (Used)
```python
# Explicit field-by-field processing
extracted = {}
extracted["match_id"] = str(match.get("match_id", "")).strip()
extracted["timestamp"] = convert_timestamp(match.get("timestamp"))
extracted["competition"] = {"name": competition.get("name", "Unknown")}
```

### Lazy Mirroring (Avoided)
```python
# Bulk copying approach (NOT used)
extracted = match.copy()  # Everything copied at once
extracted["timestamp"] = convert_timestamp(extracted["timestamp"])  # Risky assumption
```

## Key Implementation Files

### File References
- **monitoring.py:129-270** - Primary array decomposition implementation
- **pretty_conversion.py** - Format conversion with individual field extraction  
- **pretty_print.py** - Initial filtering with field-by-field processing

### Logging Output Locations
- `/workspaces/TMUX_FINAL_SPORTS/logs/monitoring/monitoring.json` - Individual fields
- `/workspaces/TMUX_FINAL_SPORTS/logs/pretty_conversion/pretty_conversion.json` - Converted units
- `/workspaces/TMUX_FINAL_SPORTS/logs/pretty_print/pretty_print.json` - Filtered data

## Performance Characteristics

### Memory Usage
- **Controlled Allocation**: Only required fields are extracted
- **No Deep Copy Overhead**: Selective field copying vs bulk operations
- **Predictable Memory Pattern**: Each field extraction is independent

### Processing Speed
- **Early Validation**: Type checks prevent downstream errors
- **Fault Isolation**: Individual field failures don't cascade
- **Debugging Efficiency**: Precise error location identification

## Future Extensions

### Potential Enhancements
1. **Field Validation Rules**: Custom validation per field type
2. **Dynamic Field Mapping**: Configuration-driven field extraction
3. **Performance Metrics**: Per-field processing time tracking
4. **Advanced Type Conversion**: Automatic type inference and conversion

### Scalability Considerations
- **Field Addition**: New fields can be added without affecting existing extraction
- **Format Changes**: API format changes isolated to specific field handlers
- **Pipeline Extension**: Additional processing stages can use same pattern

## Conclusion

The Individual Field Extraction Pattern provides:

- **Robustness**: Defensive programming with fallback defaults
- **Maintainability**: Clear, explicit field handling
- **Debuggability**: Precise error location and fault isolation
- **AI Compatibility**: Session recovery through clear boundaries
- **Scalability**: Independent field processing enables easy extensions

This pattern ensures the TMUX_FINAL_SPORTS pipeline can handle API changes, missing data, and processing errors while maintaining data integrity and enabling efficient AI-assisted development workflows.

---

**Generated**: 2025-06-28 | **Architecture**: TMUX_FINAL_SPORTS | **Purpose**: Individual Field Extraction Documentation