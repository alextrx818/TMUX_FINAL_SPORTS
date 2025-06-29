# Individual Field Extraction Instructions - Skeleton Creation

## Purpose
This document provides standardized instructions for creating new pipeline files that follow the proven defensive field extraction pattern used throughout the TMUX_FINAL_SPORTS pipeline.

## Instructions for AI Coding Agents

**"Create a new pipeline file that follows the proven defensive field extraction pattern. Here's what I need:**

**1. CRITICAL: Use defensive field extraction pattern from monitoring.py - NO processing/conversion:**
- Individual field extraction with `.get()` and fallback defaults
- Type validation with `isinstance()` checks  
- Safe array access with length validation
- String cleaning with `.strip()`
- Try/catch error handling
- **IMPORTANT: Just mirror the data - NO processing, conversion, or transformation**

**2. Standard pipeline structure:**
- Reads from monitoring.json (the current last file in the pipeline)
- Uses the same metadata and output format
- Logs to its own independent directory
- Includes pipeline integration hook at the end

**3. Template skeleton (exactly these function names):**
- `load_monitoring_data()` function
- `extract_match_fields()` function with defensive programming
- `create_output()` and `save_data()` functions
- `main()` orchestration function

**4. DEFENSIVE PROGRAMMING REQUIREMENTS:**
- Use `match.get("field_name", "")` for ALL field extractions
- Use `isinstance(data, expected_type)` before processing nested objects
- Use `len(array) >= X` before accessing array elements
- Use `str(value).strip()` for string cleaning
- Wrap risky operations in try/except blocks
- Provide fallback defaults for all extractions

**5. Just create the foundation** - I'll add the specific processing logic myself afterward.

**The goal is to have a working pipeline file that safely processes monitoring.json data, maintains the same logging standards as existing files, and uses defensive field extraction throughout.**"

## Key Defensive Patterns to Include

### 1. Individual Field Extraction
```python
# Extract each field individually with safety checks
extracted["match_id"] = str(match.get("match_id", "")).strip()
extracted["timestamp"] = str(match.get("timestamp", "")).strip()
```

### 2. Type Validation
```python
# Validate data types before processing
if "teams" in match and isinstance(match["teams"], dict):
    teams_data = match["teams"]
    # Process teams safely...
```

### 3. Safe Array Access
```python
# Check array length before accessing elements
if "home_scores" in match and isinstance(match["home_scores"], list):
    home_scores_array = match["home_scores"]
    if len(home_scores_array) >= 5:  # Safety check
        extracted["home_score_current"] = home_scores_array[0]
```

### 4. Error Handling
```python
# Wrap risky operations in try/catch blocks
try:
    extracted["numeric_field"] = int(match.get("field", 0))
except (ValueError, TypeError):
    extracted["numeric_field"] = 0
```

## Standard File Structure

### Required Functions
1. **`load_monitoring_data()`** - Reads from monitoring.json
2. **`extract_match_fields(match)`** - Individual field extraction with defensive programming
3. **`create_output(source_data, processed_matches)`** - Creates standardized output format
4. **`save_data(output_data)`** - Saves to independent JSON file
5. **`main()`** - Orchestrates the entire process

### Standard Metadata Format
```python
{
    "pretty_print_metadata": {
        "generated_at": timestamp_iso,
        "generated_at_readable": timestamp_readable,
        "total_matches": match_count,
        "source_file": "monitoring.json",
        "version": "1.0"
    },
    "matches": processed_matches,
    "footer_completion": completion_message
}
```

## Pipeline Integration

### Calling Pattern
Add to monitoring.py after successful completion:
```python
# Call next pipeline stage
subprocess.run(['python3', 'new_filename.py'], check=True)
```

### Independent Logging
- Create new directory: `/workspaces/TMUX_FINAL_SPORTS/logs/[NEW_FILENAME]/`
- Save output as: `[NEW_FILENAME].json`
- Follow same logging standards as existing files

## Benefits of This Pattern

1. **Fault Tolerance** - Missing fields don't crash the pipeline
2. **AI Session Recovery** - Clear field boundaries enable precise debugging
3. **Scalability** - New fields can be added without affecting existing extraction
4. **Consistency** - Identical logging standards across all pipeline stages
5. **Maintainability** - Individual field processing makes code self-documenting

## Usage Notes

- Use this document when requesting new pipeline files from AI coding agents
- Emphasize that only the skeleton/foundation should be created initially
- Specific data processing logic will be added separately
- All files should maintain the proven defensive field extraction pattern

---

**Document Purpose**: Template instructions for creating consistent pipeline files
**Last Updated**: 2025-06-28
**Pipeline Position**: Post-monitoring.py stages