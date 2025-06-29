# JSON Data Filtering Documentation

## Overview
This document explains the data filtering changes made to the sports data merge system to reduce output size and focus on essential match information.

## Filtered Fields

### 1. `stats` Array
**Description**: Match statistics containing detailed performance metrics
**Original Content**:
- Shot statistics (on target, off target, blocked)
- Possession percentages
- Card counts (yellow, red)
- Corner kicks, free kicks
- Offsides, fouls
- Pass accuracy

**Filtering Reason**: These detailed statistics significantly increased file size while providing granular data that may not be needed for basic match summaries.

### 2. `incidents` Array  
**Description**: Detailed match events and timeline
**Original Content**:
- Goals with scorer and assist information
- Cards (yellow/red) with player details
- Substitutions with in/out players
- VAR decisions and reviews
- Penalty events
- Timing information for all events

**Filtering Reason**: While valuable for detailed match analysis, incident tracking creates large amounts of data that may not be required for summary-level match information.

### 3. `tlive` Array
**Description**: Live text commentary feed
**Original Content**:
- Real-time match commentary
- Play-by-play descriptions
- Timing stamps for events
- Detailed action descriptions
- Position-based commentary

**Filtering Reason**: Live commentary generates extensive text data that dramatically increases file size. This is primarily useful for live viewing rather than data analysis.

## Implementation Details

### Changes Made
- **File Modified**: `merge.py`
- **Lines Affected**: 216-255 (statistics, incidents, and live commentary processing)
- **Method**: Complete removal of processing logic for these three field types

### Before Filtering
```python
# Process statistics
stats = live_data.get('stats', [])
processed_stats = {}
# ... extensive processing logic

# Process incidents  
incidents = live_data.get('incidents', [])
processed_incidents = []
# ... detailed incident processing

# Process live text commentary
tlive = live_data.get('tlive', [])
merged['live_commentary'] = tlive
```

### After Filtering
```python
# Note: stats, incidents, and tlive fields are intentionally filtered out
# These fields contained detailed match statistics, incident tracking, and live commentary
# but have been removed to reduce data size and focus on core match information
```

## Data Retained

The merge system still processes and includes:
- **Basic match information** (IDs, timestamps, venues)
- **Team details** (names, logos, countries)
- **Competition information** (names, logos)
- **Scores and results** (home/away scores, final results)
- **Match status** (live, finished, scheduled)
- **Environmental data** (weather, temperature, pressure)
- **Round and stage information**
- **Coverage details** (live coverage availability)

## Impact Assessment

### File Size Reduction
- **Before**: Approximately 93,382 bytes for 19 matches
- **Expected After**: Significant reduction (estimated 60-80% smaller)
- **Benefit**: Faster data transfer, reduced storage requirements

### Data Completeness
- **Core match data**: Fully preserved
- **Detailed analytics**: Removed
- **Use case**: Optimized for match summaries rather than detailed analysis

## Alternative Solutions

If detailed statistics, incidents, or live commentary are needed:

1. **Selective Filtering**: Modify the filtering logic to include only specific incident types or statistics
2. **Separate Endpoints**: Create dedicated endpoints for detailed data when needed
3. **Conditional Processing**: Add configuration flags to enable/disable detailed data processing
4. **Data Compression**: Implement compression for large text fields like live commentary

## Implementation Date
- **Modified**: 2025-06-20
- **Version**: 1.1 (with filtering)
- **Previous Version**: 1.0 (full data processing)

## Testing Recommendations

1. Run the modified merge script to verify filtering works correctly
2. Compare file sizes before and after filtering
3. Verify that essential match data is still preserved
4. Test with different match states (live, finished, scheduled)

---
*This filtering was implemented to optimize data size while maintaining core match information functionality.*