# JSON Field Change Guide

## Overview
This guide provides step-by-step instructions for changing JSON field names in the pretty_conversion.py pipeline. This process allows you to rename any field in the output JSON structure while preserving all data and functionality.

## How It Works

The pretty_conversion.py script reads from pretty_print.json and extracts fields using identical structure. To change a field name, you modify the extraction logic to use a different key name in the output JSON while keeping the same source data.

## Step-by-Step Process

### 1. Identify the Target Field

First, locate the field you want to change:
- Check the **Field Roadmap** in pretty_conversion.py (lines 16-112)
- Note the field number and current name
- Verify the field exists in the current JSON output

### 2. Locate the Extraction Code

Find the extraction logic in the `extract_match_fields()` function:

```python
# Example: Current extraction for "asia" field
if "asia" in company_data:
    extracted["odds"][company_id]["asia"] = company_data["asia"]
```

### 3. Modify the Output Key

Change only the **output key** (left side), keep the **source key** (right side) unchanged:

```python
# Change: "asia" → "spread"
if "asia" in company_data:
    extracted["odds"][company_id]["spread"] = company_data["asia"]
```

**Important**: 
- ✅ **Change**: `extracted["odds"][company_id]["NEW_NAME"]`
- ❌ **Don't Change**: `company_data["original_name"]`
- ❌ **Don't Change**: `if "original_name" in company_data:`

### 4. Test the Change

Run the conversion script to test:

```bash
python3 pretty_conversion.py
```

### 5. Verify Output

Check the generated file:
```bash
# Look for your new field name
grep -A 5 -B 5 "NEW_NAME" /workspaces/TMUX_FINAL_SPORTS/logs/pretty_conversion/pretty_conversion.json
```

## Field Types and Locations

### Odds Fields (Fields 25-28)
Located in `extract_match_fields()` around lines 259-267:

```python
# Field 25: Asian Handicap odds
if "asia" in company_data:
    extracted["odds"][company_id]["asia"] = company_data["asia"]

# Field 26: Both Score/Over-Under odds  
if "bs" in company_data:
    extracted["odds"][company_id]["bs"] = company_data["bs"]

# Field 27: Correct Score/Corner odds
if "cr" in company_data:
    extracted["odds"][company_id]["cr"] = company_data["cr"]

# Field 28: European/1X2 odds
if "eu" in company_data:
    extracted["odds"][company_id]["eu"] = company_data["eu"]
```

### Score Fields (Fields 12-17)
Located around lines 210-223:

```python
if "home_total" in score_summary:
    extracted["score_summary"]["home_total"] = score_summary["home_total"]
```

### Team Fields (Fields 10-11)
Located around lines 194-204:

```python
if "name" in home_team:
    extracted["teams"]["home"]["name"] = home_team["name"]
```

### Environment Fields (Fields 29-33)
Located around lines 274-284:

```python
if "weather" in environment:
    extracted["environment"]["weather"] = environment["weather"]
```

## Example Transformations

### Example 1: Change "asia" to "spread"
```python
# Before
if "asia" in company_data:
    extracted["odds"][company_id]["asia"] = company_data["asia"]

# After  
if "asia" in company_data:
    extracted["odds"][company_id]["spread"] = company_data["asia"]
```

### Example 2: Change "home_total" to "home_score"
```python
# Before
if "home_total" in score_summary:
    extracted["score_summary"]["home_total"] = score_summary["home_total"]

# After
if "home_total" in score_summary:
    extracted["score_summary"]["home_score"] = score_summary["home_total"]
```

### Example 3: Change "weather" to "conditions"
```python
# Before
if "weather" in environment:
    extracted["environment"]["weather"] = environment["weather"]

# After
if "weather" in environment:
    extracted["environment"]["conditions"] = environment["weather"]
```

## Best Practices

### ✅ Do:
- Only change the output key name (left side of assignment)
- Keep the source key and condition check unchanged
- Test each change immediately
- Document changes in the Field Roadmap comments
- Use descriptive, clear field names

### ❌ Don't:
- Change the source key (right side of assignment)
- Change the condition check (`if "original_name" in...`)
- Modify multiple fields simultaneously without testing
- Use special characters or spaces in field names
- Change fundamental data structures

## Troubleshooting

### Field Not Appearing in Output
- Check that the source field exists in pretty_print.json
- Verify the condition check uses the correct source field name
- Ensure proper indentation and syntax

### Data Loss or Corruption
- Verify you only changed the output key name
- Check that source field references remain unchanged
- Run the script and compare output counts

### JSON Structure Issues
- Maintain proper nesting levels
- Don't change parent object structures
- Preserve array and object types

## Quick Reference

| Component | Location | Pattern |
|-----------|----------|---------|
| Odds Fields | Lines 259-267 | `extracted["odds"][company_id]["NEW"] = company_data["OLD"]` |
| Score Fields | Lines 210-223 | `extracted["score_summary"]["NEW"] = score_summary["OLD"]` |
| Team Fields | Lines 194-204 | `extracted["teams"]["home"]["NEW"] = home_team["OLD"]` |
| Environment | Lines 274-284 | `extracted["environment"]["NEW"] = environment["OLD"]` |

## Common Field Changes

Based on field roadmap, commonly changed fields:

- Field 25: `"asia"` → `"spread"` (Asian Handicap)
- Field 26: `"bs"` → `"totals"` (Over/Under)
- Field 27: `"cr"` → `"corners"` (Corner kicks)
- Field 28: `"eu"` → `"moneyline"` (1X2 odds)

Remember: Always test changes immediately and verify the output maintains data integrity!